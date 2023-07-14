# AKS Friendly URL through Azure Services Tutorial

For Kubernetes and Azure Kubernetes Service (AKS), the building blocks can be accessed through an external IP generated through AKS. However, the IP addresses used can be brittle and hard to work with. However, through the use of services and ingresses, Azure CLI commands can generate a friendly url for the building blocks.

Instead of having the building blocks pods exposed via an IP address such as `12.345.2345` it can be exposed by a url such as `ingestion.7cde46e98e7e4eff8e80.centralus.aksapp.io`

## Generating a URL through AKS

When deploying the Kubernetes cluster to AKS you can enable `http_routing` on the cluster. Use the following command and replace with the `myResourceGroup` and `myAKSCluster` with your configuration.

```Azure CLI
az aks enable-addons --resource-group myResourceGroup --name myAKSCluster --addons http_application_routing
```

Then run the following command and also replace with your configuration

```Azure CLI
az aks show --resource-group myResourceGroup --name myAKSCluster --query addonProfiles.httpApplicationRouting.config.HTTPApplicationRoutingZoneName -o table
```

The output should be similar to this:

```Output
7cde46e98e7e4eff8e80.centralus.aksapp.io
```

Next, connect to your cluster:

```Azure CLI
az aks get-credentials --resource-group myResourceGroup --name myAKSCluster
```

Then, create a service and ingress for the desired pod such as the validation example:

```.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: validation-app
  name: validation
spec:
  replicas: 1
  selector:
    matchLabels:
      app: validation-app
  template:
    metadata:
      labels:
        app: validation-app
    spec:
      containers:
        - name: validation
          image: ghcr.io/cdcgov/phdi/validation:v1.0.7
          imagePullPolicy: Always
          ports:
            - containerPort: 8080
              name: validation
---
apiVersion: v1
kind: Service
metadata:
  name: validation-service
spec:
  type: ClusterIP
  ports:
  - port: 8080
  selector:
    app: validation-app
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: validation-ingress
  annotations:
    kubernetes.io/ingress.class: addon-http-application-routing # This must be included
spec:
  rules:
  - host: validation.7cde46e98e7e4eff8e80.centralus.aksapp.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: validation-service
            port:
              number: 8080
```

Note that the `host:` in the ingress begins with a custom name. It does not necessarily need to match the app name. Then run `apply` to your AKS cluster.

```Command line
kubectl apply -f your-yaml-path.yaml
```

To test the URL, go to the URL defined in `host` and ensure that the page displays `{status: "OK"}`. It may take a few minutes for the URL to work.

Now your AKS pod has a friendly URL that is exposed for external use.

## Further Reading
