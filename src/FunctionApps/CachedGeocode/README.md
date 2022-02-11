# Using redis to cache values in function apps

## Overview

* Create a function app like normal
* Under the resource group, create an Azure Cache for Redis instance
	* `Basic C0` with default settings should be plenty for testing
* After deployment, we need to set some environment variables for the function app
	* Grab the hostname, port, and primary access key (the redis password) from the Access Keys
	* Add the settings as environment variables to the function app
		* `REDIS_HOST` is the hostname of the endpoint, like `my-geocode-cache.redis.cache.windows.net`
		* `REDIS_PORT` is a number like `6380`
		* `REDIS_PASSWORD` is the value of the primary access key (also listed as the password in the connection string)
		* `REDIS_TLS` is `1` when in Azure
		* Don't forget to manually save the configuration at the top


### Creating a local redis instance

You can create a docker instance for local testing quickly via:

```
docker run -d --name redis -p 6379:6379 redis:alpine
```

This allows all incoming connections on port 6379 without a password, so be careful not to do this outside of a laptop.
