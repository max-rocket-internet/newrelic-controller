#!/usr/bin/env python3

import json
import sys
from kubernetes import client, watch
from functions import get_config, process_event, create_logger, parse_too_old_failure


runtime_config = get_config()
crds = client.CustomObjectsApi()
logger = create_logger(log_level=runtime_config['log_level'])


resource_version = ''

if __name__ == "__main__":
    logger.info('newrelic-controller initializing')
    while True:
        stream = watch.Watch().stream(crds.list_cluster_custom_object, 'newrelic.com', 'v1', 'newrelicsettings', resource_version=resource_version)
        try:
            for event in stream:
                event_type = event["type"]
                obj = event["object"]
                metadata = obj.get('metadata')
                spec = obj.get('spec')
                code = obj.get('code')

                if code == 410:
                    logger.debug('Error code 410')
                    new_version = parse_too_old_failure(obj.get('message'))
                    if new_version == None:
                        logger.error('Failed to parse 410 error code')
                        resource_version = ''
                        break
                    else:
                        resource_version = new_version
                        logger.debug('Updating resource version to {0} due to "too old" error'.format(new_version))
                        break

                if not metadata or not spec:
                    logger.error('No metadata or spec in object, skipping: {0}'.format(json.dumps(obj, indent=1)))
                    break

                if metadata['resourceVersion'] is not None:
                    resource_version = metadata['resourceVersion']
                    logger.debug('resourceVersion now: {0}'.format(resource_version))

                process_event(crds, obj, event_type)

        except client.rest.ApiException as e:
            if e.status == 404:
                logger.error('Custom Resource Definition not created in cluster')
                sys.exit(1)
            elif e.status == 401:
                logger.error('Unauthorized')
                sys.exit(1)
            else:
                raise e
        except KeyboardInterrupt:
            logger.info('newrelic-controller exiting')
            sys.exit(0)
