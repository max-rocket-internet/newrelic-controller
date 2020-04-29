# Kubernetes newrelic-controller

  <img src="https://raw.githubusercontent.com/max-rocket-internet/newrelic-controller/master/img/k8s-logo.png" width="100"><img src="https://raw.githubusercontent.com/max-rocket-internet/newrelic-controller/master/img/new-relic-logo.png" width="180">

A simple k8s controller to update New Relic Application settings and Alert Policies.

Once you install the controller, you can create `NewRelicSetting` resource in k8s and the controller will apply the settings in New Relic.

The possible options under `application.settings` come from [here](https://new-relic-api.readthedocs.io/en/develop/ref/applications.html#newrelic_api.applications.Applications.update) and are:

- `app_apdex_threshold` (float): Application apdex threshold to update
- `end_user_apdex_threshold` (float): End user apdex threshold to update
- `enable_real_user_monitoring` (bool): Whether to enable real user monitoring

Example resource:

```yaml
apiVersion: newrelic.com/v1
kind: NewRelicSetting
metadata:
  name: app1
spec:
  application:
    settings:
      app_apdex_threshold: 0.85
```

You can also add Alert Policies and Alert Conditions, for example APM metrics. Each `alerts_policies` item follows the schema shown [here](https://rpm.newrelic.com/api/explore/alerts_policies/create) and can have multiple `conditions` with schema shown [here](https://rpm.newrelic.com/api/explore/alerts_conditions/create) and `channels` that are just notification channel IDs.

Here's a complete example:

```yaml
apiVersion: newrelic.com/v1
kind: NewRelicSetting
metadata:
  name: app2
spec:
  application:
    name: my-app2-in-new-relic
    alerts_policies:
      - name: my-app2-in-new-relic
        incident_preference: PER_CONDITION
        channels:
          - 123456789
        conditions:
          - name: my-app2 apdex
            enabled: true
            type: apm_app_metric
            condition_scope: application
            metric: apdex
            value_function: apdex_score
            terms:
              - duration: 5
                operator: below
                priority: critical
                threshold: 0.85
                time_function: all
```

There are more examples in [examples](examples).

Pull requests welcome.

### Installation

Use the included [Helm](https://helm.sh/) chart and set New Relic API key:

```shell
helm install ./chart --set new_relic_api_key="aaaaabbbbbccccdddd"
```

Or use the docker image: [maxrocketinternet/newrelic-controller](https://hub.docker.com/r/maxrocketinternet/newrelic-controller)

### Examples

See [examples](examples).

### Testing

Export required environment variables:

```
export NEW_RELIC_API_KEY=aaaaabbbbbccccdddd
export LOG_LEVEL=debug
```

Start the controller, it will use your default kubectl configuration/context:

```
./controller.py
```

Create or change some resources:

```
kubectl apply -f examples/simple.yaml
```

### Thanks

Thanks to this python package where much of the New Relic code was copied from: https://github.com/ambitioninc/newrelic-api
