# Realtools API

These tools were made on request from a close friend of mine who plays this game. A live instance can be found at [realtools.shay.cat](https://realtools.shay.cat).

The source is provided here primarily for educational purposes - I am aware that the target audience of this program is not tech-savvy in this way.

# Self-hosting

A live instance can be found at [realtools.shay.cat](https://realtools.shay.cat). This section is for if you wish to host your own instance for whatever reason you may have. Be sure as well to abide by [this project's license](LICENSE).

In order to have a face for this API, you will also need to run an instance of [the front-end server](https://github.com/hr-tools/website), and follow the self-hosting instructions there.

## Requirements

* Python >=3.7
* The packages in [`requirements.txt`](requirements.txt)
* A running PostgreSQL server
* An account on [horsereality.com](https://horsereality.com)

## Configuration

A configuration file named `config.json` is required to be in the working directory. An example of such a file can be found at [`config-example.json`](config-example.json). Minimal documentation of the supported values can be found below:

### `authentication`

Horse pages cannot be viewed without being logged in, so we must provide credentials for Realtools to work properly. You may define credentials at `authentication.com.email` and `authentication.com.password`. Previously, you could also specify credentials in `authentication.nl.*`, but Horse Reality's Dutch server was shut down in January 2022, so Realtools does not support it anymore.

### `postgres`

Authentication details for a PostgreSQL server. Must include `database`, `user`, and `password`.

### `address` and `port` (optional)

Specify the `address:port` that the webserver runs on. Defaults to `localhost:2965`. You may specify one, both, or neither values.

### `redis` (optional)

A redis address to store share IDs. Share IDs last for 1 week, but this may be changed in the [`api.merge.create_share_link`](api/v2/merge.py) function.

### `log` (optional)

A path to a file to log to. If not specified, logging is disabled.
