# Realmerge (Image Combiner for Horse Reality)

This was made on request from a close friend of mine who plays this game. A live instance can be found at [realmerge.shay.cat](https://realmerge.shay.cat).

The source is provided here for part educational purposes (the actual merge process is really simple) and partly for self-hosting, if you ever want to do that for whatever reason.

# Demonstration

![demonstration](https://github.com/shayypy/realmerge/blob/main/static/example.gif)

# Self-Hosting

A live instance can be found at [realmerge.shay.cat](https://realmerge.shay.cat). This section is for if you wish to host your own instance for whatever reason you may have. Be sure as well to abide by [this project's license](https://github.com/shayypy/realmerge/blob/main/LICENSE).

## Requirements

* Python >=3.7
* The packages in [`requirements.txt`](https://github.com/shayypy/realmerge/blob/main/requirements.txt)
* A folder to save merged files to in your working directory. By default this should be `rendered`.

## Configuration

A configuration file named `config.json` is required to be in the working directory. An example of such a file can be found at [`config-example.json`](https://github.com/shayypy/realmerge/blob/main/config-example.json).

### `address` and `port` (optional)

Specify the `address:port` that the webserver runs on. Defaults to `localhost:2965`.

### `authentication`

Horse pages cannot be viewed without being logged in, so we use cookies to tell Horse Reality that we are indeed authenticated. Because Horse Reality runs two servers (English and Dutch), each with separate account systems, the config file may define credentials for the English server (`.com`) and the Dutch server (`.nl`) separately.

If you don't want to support a specific server on your instance, just remove its key to ignore it. Blanking out both will raise an error, though.

### `output` (optional)

If you want to customize where Realmerge saves merged images, you can set the `name` and `path` values here.

#### `name`

The route that the webserver will serve files on. E.g., if it is `coolhorsepics`, files will be available on `cooldomain.com/coolhorsepics/...`. Defaults to `rendered`.

#### `name-multi`

Same as `name`, but for [Multi mode](https://realmerge.shay.cat/multi) renders.

#### `path`

An absolute or relative path on your filesystem to where Realmerge should save merged files. Defauls to `rendered` in the current working directory. Set to `null` to disable saving to the local disk and instead serve images as base64 data. If Realmerge fails to save locally due to a permissions error, this will be done anyway, even if the value is not `null`.

#### `path-multi`

Same as `path`, but for [Multi mode](https://realmerge.shay.cat/multi) renders.

### `support`

An HTML string indicating where users of this instance should contact you for support. You should generally only set this if you have modified your Realmerge instance.
