from .base import Resource


class ExternalServiceConditions(Resource):
    """
    An interface for interacting with the NewRelic Alert Conditions API.
    """
    def create(self, policy_id, condition_data):
        """
        Creates an external service condition
        """
        if 'policy_id' not in condition_data:
            condition_data['policy_id'] = policy_id

        return self._post(
            url='{0}alerts_external_service_conditions/policies/{1}.json'.format(self.URL, policy_id),
            headers=self.headers,
            json={'external_service_condition': condition_data}
        )

    def list(self, policy_id):
        """
        Gets a list of external services conditions for a policy
        """
        return self._get(
            url='{0}alerts_external_service_conditions.json?policy_id={1}'.format(self.URL, policy_id),
            headers=self.headers,
        )['external_service_conditions']


    def update(self, condition_id, condition_data):
        """
        Updates an external service condition
        """

        return self._put(
            url='{0}alerts_external_service_conditions/{1}.json'.format(self.URL, condition_id),
            headers=self.headers,
            json={'external_service_condition': condition_data}
        )
