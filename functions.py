# -*- coding: utf-8 -*-

import os
import json
import logging
import logging.handlers
from kubernetes import config
from newrelic_api import Applications


logger = logging.getLogger()


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


def create_logger(log_level):
    '''
    Creates logging object
    '''
    json_format = logging.Formatter('{"time":"%(asctime)s", "level":"%(levelname)s", "message":"%(message)s"}')
    logger = logging.getLogger()
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(json_format)
    logger.addHandler(stdout_handler)

    if log_level == 'debug':
        logger.setLevel(logging.DEBUG)
    elif log_level == 'info':
        logger.setLevel(logging.INFO)
    else:
        raise Exception('Unsupported log_level {0}'.format(log_level))

    return logger


def process_event(crds, obj, event_type):
    '''
    Processes events in order to set New Relic settings
    '''
    nr = Applications()
    spec = obj.get('spec')
    metadata = obj.get('metadata')
    k8s_resource_name = metadata.get('name')

    if 'name' in spec['application']:
        nr_app_name = spec['application']['name']
    else:
        nr_app_name = k8s_resource_name

    logger.debug('Processing event: {0}'.format(json.dumps(obj, indent=1)))

    if event_type == 'DELETED':
        logger.debug('Ignoring deletion for New Relic app {0}, deletion not supported'.format(nr_app_name))
        return
    else:
        try:
            apps = nr.list()
        except Exception as e:
            logger.error('Getting list of applications from New Relic failed: {2}'.format(e))

        id = None
        for app in apps['applications']:
            if app['name'] == nr_app_name:
                id = app['id']
                break
        if not id:
            logger.error('New Relic application {0} not found'.format(nr_app_name))
            # Should the application be created here?
            return

        try:
            nr.update(id=id, **spec['application']['settings'])
        except Exception as e:
            logger.error('Updating application {0} failed: {1}'.format(nr_app_name, e))

        logger.info('Update of application {0} with id {1} completed with settings: {2}'.format(nr_app_name, id, json.dumps(spec['application']['settings'])))
