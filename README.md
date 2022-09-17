# Realtools API

These tools were made on request from a close friend of mine who plays this game. A live instance can be found at [realtools.shay.cat](https://realtools.shay.cat).

The source is provided here primarily for educational purposes - I am aware that the target audience of this program is not tech-savvy in this way.

# Self-hosting

A live instance can be found at [realtools.shay.cat](https://realtools.shay.cat). This section is for if you wish to host your own instance for whatever reason you may have. Be sure as well to abide by [this project's license](LICENSE).

The face you see at the above domain can be found at [this repository](https://github.com/hr-tools/front). Chances are you will want to design a custom interface if you are self-hosting this API, however.

## Requirements

* Python >=3.7
* The packages in [`requirements.txt`](requirements.txt)
* A running PostgreSQL server

## Configuration

A configuration file named `config.json` is required to be in the working directory. An example of such a file can be found at [`config-example.json`](config-example.json). Minimal documentation of the supported values can be found below:

### `remember_cookie_name` and `remember_cookie_value`

The remembrance cookie for authenticating with Horse Reality. See [hr-tools/horsereality](https://github.com/hr-tools/horsereality#mini-api-reference) for more info.

### `postgres`

Authentication details for a PostgreSQL server. Must include `database`, `user`, and `password`.

### `address` and `port` (optional)

Specify the `address:port` that the webserver runs on. Defaults to `localhost:2965`. You may specify one, both, or neither values.

### `redis` (optional)

A redis address to store share IDs. Share IDs last for 1 week, but this may be changed in the [`api.merge.create_share_link`](api/v2/merge.py) function.

### `log` (optional)

A path to a file to log to. If not specified, logging is disabled.
