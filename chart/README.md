# Kubernetes New Relic Controller

This chart creates a [newrelic-controller](https://github.com/max-rocket-internet/newrelic-controller) deployment and a `NewRelicSetting` Custom Resource Definition.

## TL;DR;

```console
$ helm install --name my-release stable/newrelic-controller --set new_relic_api_key="aaaaabbbbbccccdddd"
```

## Prerequisites

- Kubernetes 1.8+

## Uninstalling the Chart

To delete the chart:

```console
$ helm delete my-release
```

## Configuration

The following table lists the configurable parameters for this chart and their default values.

| Parameter                          | Description                               | Default                        |
| ---------------------------------- | ----------------------------------------- |------------------------------- |
| `new_relic_api_key`                | Your New Relic Account API key            | `nil`                          |
| `annotations`                      | Optional deployment annotations           | `{}`                           |
| `affinity`                         | Map of node/pod affinities                | `{}`                           |
| `image.repository`                 | Image                                     | `maxrocketinternet/newrelic-controller` |
| `image.tag`                        | Image tag                                 | `0.8`                          |
| `image.pullPolicy`                 | Image pull policy                         | `IfNotPresent`                 |
| `rbac.create`                      | RBAC                                      | `true`                         |
| `resources`                        | CPU limit                                 | `{}`                           |
| `tolerations`                      | Optional deployment tolerations           | `{}`                           |
| `log_level`                        | Log level for controller (`info`|`debug`) | `info`                         |

Specify each parameter using the `--set key=value[,key=value]` argument to `helm install` or provide a YAML file containing the values for the above parameters:

```console
$ helm install --name my-release stable/newrelic-controller --values values.yaml
```
