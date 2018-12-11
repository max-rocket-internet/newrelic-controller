from .base import Resource


class AlertsConditions(Resource):
    """
    An interface for interacting with the NewRelic Alert Conditions API.
    """
    def create(self, policy_id, condition_data):
        '''
        Creates an alert condition
        '''
        if 'policy_id' not in condition_data:
            condition_data['policy_id'] = policy_id

        return self._post(
            url='{0}alerts_conditions/policies/{1}.json'.format(self.URL, policy_id),
            headers=self.headers,
            json={'condition': condition_data}
        )

    def list(self, policy_id):
        '''
        Gets a list of alert conditions for a policy
        '''
        return self._get(
            url='{0}alerts_conditions.json'.format(self.URL),
            headers=self.headers,
            data='policy_id={0}'.format(policy_id)
        )
