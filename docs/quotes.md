# Quotes downloading
To download historical quotes, Ineractive Brokers's TWS needs to be running and API access enabled. Then execute:

```console
$ barbucket quotes download --universe my_universe
```
| Option | Description |
| ------ | ----------- |
| `-u`, `--universe` | Name of the universe to download quotes for |

## Configuration
You can find some configuration options for quotes downloading within the `quotes` section of the [config file](config.md).

## Restrictions
- Right now, only daily quotes are supported
- End-date will always be today
- IB is enforcing strict speedlimits, so downloading quotes on IB for many contracts will need some time.
