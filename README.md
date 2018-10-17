# Kubernetes newrelic-controller

  <img src="https://raw.githubusercontent.com/max-rocket-internet/newrelic-controller/master/img/k8s-logo.png" width="100"> + <img src="https://raw.githubusercontent.com/max-rocket-internet/newrelic-controller/master/img/new-relic-logo.png" width="180">

A simple k8s controller to update New Relic application settings. Once you install the controller, you can create `NewRelicSetting` resource in k8s and the controller will will set the application settings in New Relic.

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

Pull requests welcome.

### Installation

Use the included [Helm](https://helm.sh/) chart and set New Relic API key:

```shell
helm install ./chart --set new_relic_api_key="aaaaabbbbbccccdddd"
```

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
