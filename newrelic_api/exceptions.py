import json

class ConfigurationException(Exception):
    """
    An exception for Configuration errors
    """
    message = 'There was an error in the configuration'


class NewRelicAPIServerException(Exception):
    """
    An exception for New Relic server errors
    """
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.formatted_error = 'Error {0}, {1}'.format(self.status_code, json.loads(self.message)['error']['title'])
