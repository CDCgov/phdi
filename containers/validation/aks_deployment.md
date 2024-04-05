# Deploying Validation to Kubernetes Azure

Deploying to Azure Kubernetes requires Azure Command Line Interface (Azure CLI) and kubectl already installed. If you do not have them installed install Azure CLI, then run `az aks install-cli`

After, run `az login` and log into the desired Azure account

## Creating a Kubernetes Cluster

To create a Kuberentes cluster in Azure Kubernetes Service (AKS), you can use the `az aks create` command in your command line to create a cluster. Replace `yourresourcegroup` and `yourclusternamehere` with your resource group and cluster name

```azurecli
az aks create -g yourresourcegroup -n yourclusternamehere --enable-managed-identity --node-count 1 --enable-addons monitoring --enable-msi-auth-for-monitoring  --generate-ssh-keys
```

## Configuring the Connection

In your terminal, run this command to connnect to your Kubernetes cluster 

`az aks get-credentials --resource-group myResourceGroup --name myAKSCluster`

Then, run the following command to ensure a connection

`kubectl get nodes`

The following output should show if there was a single node in one of the previous steps. Also ensure that status is ready

```
NAME                       STATUS   ROLES   AGE     VERSION
aks-nodepool1-31718369-0   Ready    agent   6m44s   v1.12.8
```

## Deploying the application 

In the `Dockerfile`, take note of the port that the app is exposed to. In this example, we will use 8080

``` 
FROM python:3.11-slim
...
EXPOSE 8080
CMD uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Then create manifest file that uses the validation image in GitHub 

```
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: validation
  name: validation
spec:
  replicas: 1
  selector:
    matchLabels:
      app: validation
  template:
    metadata:
      labels:
        app: validation
    spec:
      containers:
      - image: ghcr.io/cdcgov/phdi/validation:v1.0.7
        imagePullPolicy: Always
        name: validation
        ports:
        - containerPort: 8080
          name: validation
---
apiVersion: v1
kind: Service
metadata:
  name: validation-load-balancer
spec:
  type: LoadBalancer
  ports:
  - port: 8080
  selector:
    app: validation

```

Note that the container port needs to match the port defined in the Dockerfile. The service port also matches the `containerPort`. If you are using a different container, you must edit the `-image` tag on the containers section. Create and name the manifest file as a `.yml` file.

Then run the apply command with your manifest file

`kubectl apply -f yourmanifesthere.yml`

Once the apply runs successfully, you can view the LoadBalancer by running

`kubectl get service azure-vote-front --watch`

Once the `EXTERNAL-IP` is finished you can copy that IP address and append `:8080/validate` to the end of the url and run a validation request through it. So an example url would be `12.34.567.9:8080/validate`

Using Postman or any API endpoint tester, you can run a validation message through the endpoint and get a message back. 