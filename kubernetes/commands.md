az aks create \
    --resource-group adfk8stesting \
    --name adfTesting \
    --node-count 2 \
    --generate-ssh-keys


az aks get-credentials --resource-group adfk8stesting --name adfTesting

    kubectl apply -f manifest.yaml

kubectl get service test-load-balancer --watch