# Using Cosmos DB to cache values in function apps

## Overview

* Create a function app like normal
* Under the resource group, create a Cosmos DB instance for MongoDB with the serverless option checked
* After deployment, we need to set an environment variable for the function app
	* In the Cosmos DB console, go to `Connection String`, then copy the `PRIMARY CONNECTION STRING`
	* Go to the function config and add an extra environment variable called `COSMOSDB_CONN_STRING` with the value above


### Creating a local mongodb instance

You can create a docker instance for local testing quickly via:

```
docker run -d --name mongo -p 27017:27017 mongo
```

This allows all incoming connections on port 27017 without a password, so be careful not to do this outside of a laptop.

Using this config (running locally with the default port) allows you to skip configuration if you want to run it locally via `func start`.
