# Realtools (Web Tools for Horse Reality)

These tools were made on request from a close friend of mine who plays this game. A live instance can be found at [realtools.shay.cat](https://realtools.shay.cat).

The source is provided here for mostly for educational purposes, but you may also self-host it if the live instance is insufficient for your purposes.

# Self-Hosting

A live instance can be found at [realtools.shay.cat](https://realtools.shay.cat). This section is for if you wish to host your own instance for whatever reason you may have. Be sure as well to abide by [this project's license](https://github.com/shayypy/realtools/blob/main/LICENSE).

## Requirements

* Python >=3.7
* The packages in [`requirements.txt`](https://github.com/shayypy/realtools/blob/main/requirements.txt)
* A running PostgreSQL server

## Configuration

A configuration file named `config.json` is required to be in the working directory. An example of such a file can be found at [`config-example.json`](https://github.com/shayypy/realtools/blob/main/config-example.json).

### `address` and `port` (optional)

Specify the `address:port` that the webserver runs on. Defaults to `localhost:2965`.

### `authentication`

Horse pages cannot be viewed without being logged in, so we use cookies to tell Horse Reality that we are indeed authenticated. Because Horse Reality runs two servers (English and Dutch), each with separate account systems, the config file may define credentials for the English server (`.com`) and the Dutch server (`.nl`) separately.

If you don't want to support a specific server on your instance, just remove its key to ignore it. Blanking out both will raise an error, though.

##### Note: Dutch Server

The Dutch server will be sunsetted by HR soon. When this happens, Realtools will no longer read for `.nl` credentials and URLs inputted from the Dutch server will be interpretted as being invalid.

### `redis`

A redis address to store share IDs from the share button on [Multi mode](https://realtools.shay.cat/multi).

### `log`

A path to a file to log to. If not specified, logging is disabled (default).
