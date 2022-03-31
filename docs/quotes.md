# Quotes downloading
To download historical quotes, IB's TWS needs to be running and API access enabled. Then execute

```console
$ barbucket quotes download --universe my_universe
```
| Option | Description |
| ------ | ----------- |
| `-u`, `--universe` | Name of the universe to download quotes for |
 

## Restrictions
- Right now, only daily quotes are supported
- End-date will always be today
- Duration will be 15 years or shorter, if youngest existing quote is newer
- IB is enforcing strict speedlimits, so downloading quotes on IB for many contracts will need some time.

## Configuration
Some adjustments to the process can be changed in the config file at 
`~/.barbucket/config.ini`