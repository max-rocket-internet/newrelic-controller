from .base import Resource


class AlertsPolicyChannels(Resource):
    """
    An interface for interacting with the Notification channels API.
    """
    def create(self, policy_id, channel_id):
        '''
        Creates an association between an alerts channel and a policy
        '''
        return self._put(
            url='{0}alerts_policy_channels.json?policy_id={1}&channel_ids={2}'.format(self.URL, policy_id, channel_id),
            headers=self.headers
        )

    def delete(self, policy_id, channel_id):
        '''
        Deletes an association between an alerts channel and a policy
        '''
        return self._delete(
            url='{0}alerts_policy_channels.json?channel_id={2}&policy_id={1}'.format(self.URL, policy_id, channel_id),
            headers=self.headers
        )

    def list(self):
        '''
        Lists the Notification channels
        '''
        return self._get(
            url='{0}alerts_channels.json'.format(self.URL),
            headers=self.headers
        )
