# Command line interface
Barbucket is controlled by using its command line interface. The `barbucket` command is available after installation of the Python package.
```console
$ barbucket --help

Usage: barbucket [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose  -v for DEBUG
  --help         Show this message and exit.

Commands:
  contracts  Contracts commands
  quotes     Quotes commands
  universes  Universes commands
```
| Option | Description |
| ------ | ----------- |
| `-h`, `-- help` | shows help, available on all group levels as well |
| `-v` | shows debug messages on console |

## Further infos in the console

- For operations, that do not finish instantly, a progress bar is shown.
- Log-messages of level `Info` and above are also shown in the terminal.
- To show all log-messages in the terminal, provide the option `-v` to the `barbucket` command.

## Command groups
Further commands can be found within the command groups:

| Command group | Description |
| -------------- | ----------- |
| `contracts` | Contracts commands |
| `universes` | Universes commands |
| `quotes` | Quotes commands |

To see the available commands, use the `--help` option:
```console
$ barbucket contracts --help

Usage: barbucket contracts [OPTIONS] COMMAND [ARGS]...

  Contracts commands

Options:
  --help  Show this message and exit.

Commands:
  download-ib-details  Fetch details for all contracts from IB TWS
  read-tv-details      Read details for all contracts from TV files
  sync-listing         Sync master listing to IB exchange listing
```