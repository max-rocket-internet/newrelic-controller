# -*- coding: utf-8 -*-

import os
import json
import logging
import re
import logging.handlers
from kubernetes import config
from newrelic_api import Applications, AlertsPolicies, AlertsConditions, AlertsPolicyChannels
from newrelic_api.exceptions import NewRelicAPIServerException


def get_config():
    '''
    Gets the run time configuration from the environment
    '''

    if 'KUBERNETES_PORT' in os.environ:
        config.load_incluster_config()
    else:
        config.load_kube_config()

    if 'NEW_RELIC_API_KEY' not in os.environ:
        raise Exception('NEW_RELIC_API_KEY environment variable not set')

    settings = {
        'log_level': os.getenv('LOG_LEVEL', 'info'),
    }

    return settings


def parse_api_error(error):
    '''
    Returns a nicer from string from a new relic API error
    '''
    text = str(error)
    return text.replace('{"error":{"title":"', '').replace('."}}', '')


class K8sLoggingFilter(logging.Filter):
    '''
    A small filter to add add extra logging data if not present
    '''
    def filter(self, record):
        if not hasattr(record, 'resource_name'):
            record.resource_name = '-'
        if not hasattr(record, 'new_relic_app'):
            record.new_relic_app = '-'
        return True


def create_logger(log_level):
    '''
    Creates logging object
    '''
    json_format = logging.Formatter('{"time":"%(asctime)s", "level":"%(levelname)s", "resource_name":"%(resource_name)s", "new_relic_app":"%(new_relic_app)s", "message":"%(message)s"}')
    filter = K8sLoggingFilter()
    logger = logging.getLogger()
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(json_format)
    logger.addHandler(stdout_handler)
    logger.addFilter(filter)

    if log_level == 'debug':
        logger.setLevel(logging.DEBUG)
    elif log_level == 'info':
        logger.setLevel(logging.INFO)
    else:
        raise Exception('Unsupported log_level {0}'.format(log_level))

    return logger


def parse_too_old_failure(message):
    '''
    Parse an error from watch API when resource version is too old
    '''
    regex = r"too old resource version: .* \((.*)\)"

    result = re.search(regex, message)
    if result == None:
        return None

    match = result.group(1)
    if match == None:
        return None

    try:
        return int(match)
    except:
        return None


def process_event(crds, obj, event_type):
    '''
    Processes events in order to set New Relic settings
    '''
    nr_applications = Applications()

    spec = obj.get('spec')
    metadata = obj.get('metadata')
    k8s_resource_name = metadata.get('name')

    if 'name' in spec['application']:
        nr_app_name = spec['application']['name']
    else:
        nr_app_name = k8s_resource_name

    logger = logging.LoggerAdapter(logging.getLogger(), {'resource_name': k8s_resource_name, 'new_relic_app': nr_app_name})

    logger.debug('Processing event: {0}'.format(json.dumps(obj)))

    if event_type == 'DELETED':
        if 'alerts_policies' in spec['application']:
            alerts_policies_api = AlertsPolicies()
            for policy in spec['application']['alerts_policies']:
                policies = alerts_policies_api.list(filter_name=policy['name'])
                try:
                    result = alerts_policies_api.delete(policy_id=policies['policies'][0]['id'])
                except NewRelicAPIServerException as e:
                    logger.error('Failed to delete alert policy {0}: {1}'.format(policy['name'], e.formatted_error))
                except IndexError:
                    logger.error('Failed to delete alert policy {0}: no matching policy found'.format(policy['name']))
                else:
                    logger.info('Alert policy deleted: {0}'.format(policy['name']))

    else:
        try:
            apps = nr_applications.list(filter_name=nr_app_name)
            nr_app_id = apps['applications'][0]['id']
        except NewRelicAPIServerException as e:
            logger.error('Failed to get list of applications from New Relic: {0} {1}'.format(e.formatted_error))
            return
        except IndexError:
            logger.error('Failed to find application ID for {0}'.format(nr_app_name))
            return
        else:
            logger.debug('Found application with id {0}'.format(nr_app_id))

        if 'alerts_policies' in spec['application']:
            alerts_policies_api = AlertsPolicies()

            for policy in spec['application']['alerts_policies']:
                policy_id = None

                try:
                    alerts_policies_list = alerts_policies_api.list(filter_name=policy['name'])
                    policy_id = alerts_policies_list['policies'][0]['id']
                except IndexError:
                    logger.info('Alerts policy does not exist: {0}'.format(policy['name']))
                except Exception as e:
                    logger.info('Failed to list alerts policies: {0}'.format(parse_api_error(e)))
                    return
                else:
                    logger.info('Found existing alerts policy with ID: {0}'.format(policy_id))

                if policy_id == None:
                    try:
                        result = alerts_policies_api.create(name=policy['name'], incident_preference=policy['incident_preference'])
                        policy_id = result['policy']['id']
                    except Exception as e:
                        logger.info('Failed to create alerts policy: {0}'.format(parse_api_error(e)))
                        return
                    else:
                        logger.info('Created alerts policy {0}'.format(policy_id))

                if 'channels' in policy:
                    alerts_policy_channels_api = AlertsPolicyChannels()
                    for channel_id in policy['channels']:
                        try:
                            alerts_policy_channels_api.create(policy_id=policy_id, channel_id=channel_id)
                        except NewRelicAPIServerException as e:
                            logger.error('Failed to create alerts policy channel {0}: {1}'.format(channel_id, e.formatted_error))
                            continue
                        else:
                            logger.info('Created alerts policy channel {0}'.format(channel_id))

                if 'conditions' in policy:
                    alerts_conditions_api = AlertsConditions()
                    try:
                        alerts_conditions = alerts_conditions_api.list_all(policy_id=policy_id)
                    except NewRelicAPIServerException as e:
                        logger.error('Failed to get alerts condition for {0}: {1}'.format(policy['name'], e.formatted_error))
                        continue

                    for condition in policy['conditions']:
                        data = condition
                        data['entities'] = [nr_app_id]
                        existing_alerts_conditions = [i['id'] for i in alerts_conditions if i['name'] == condition['name']]

                        if existing_alerts_conditions:
                            try:
                                result = alerts_conditions_api.update(condition_id=existing_alerts_conditions[0], condition_data=data)
                            except NewRelicAPIServerException as e:
                                logger.error('Failed to update alerts condition {0}: {1}'.format(data['name'], e.formatted_error))
                                continue
                            else:
                                logger.info('Updated alerts condition {0} ID {1}'.format(data['name'], existing_alerts_conditions[0]))
                        else:
                            try:
                                result = alerts_conditions_api.create(policy_id=policy_id, condition_data=data)
                            except NewRelicAPIServerException as e:
                                logger.error('Failed to create alerts condition {0}: {1}'.format(data['name'], e.formatted_error))
                                continue
                            else:
                                logger.info('Created alerts condition {0}'.format(data['name']))

        if 'settings' in spec['application']:
            try:
                nr_applications.update(id=nr_app_id, **spec['application']['settings'])
            except NewRelicAPIServerException as e:
                logger.error('Failed to update app {0}: {1}'.format(nr_app_name, e.formatted_error))
            else:
                logger.info('Update of application with ID {0} completed'.format(nr_app_id))

        return
