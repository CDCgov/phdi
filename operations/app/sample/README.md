# README: Sample applications

Functions here are meant to be deployed to the environment constructed by the terraform code. They should
only be executed manually so they can give feedback as to whether the environment is setup properly.

* Function `infrastructurecheck`
    * Reaches out to https://www.ipify.org/ to check that:
        1. we can get out of the network, and
        2. what our IP address is (return payload: `{"ip": "a.b.c.d"}`)
    * Reads a blob from each of the data containers and writes an update back.
    * Reads a value from the key vault
* Function `raise`
    * Raises an exception so you can see what it looks like in App Insights