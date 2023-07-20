# Loading environment variables into your kubernetes pod
1. Connect to azure from your command line `az login`
2. If creating a new resource group `az group create -n myResourceGroup -l eastus2`
3. If creating a new azure kubernetes service `az aks create -n myAKSCluster -g myResourceGroup --enable-addons azure-keyvault-secrets-provider`
4. If using an existing AKS `az aks enable-addons --addons azure-keyvault-secrets-provider --name myAKSCluster --resource-group myResourceGroup`
5. Find the client id/managed identity by running `az aks show -g <resource-group> -n <cluster-name> --query addonProfiles.azureKeyvaultSecretsProvider.identity.clientId -o tsv`
6. Create or use an existing key vault `az keyvault create -n <keyvault-name> -g myResourceGroup -l eastus2`
  a. Add secrets through the GUI
7. Grand the identity from step 5 access to the key vault
  a. --spn is the number from step 5
```
# Set policy to access keys in your key vault
az keyvault set-policy -n <keyvault-name> --key-permissions get --spn <identity-client-id>

# Set policy to access secrets in your key vault
az keyvault set-policy -n <keyvault-name> --secret-permissions get --spn <identity-client-id>

# Set policy to access certs in your key vault
az keyvault set-policy -n <keyvault-name> --certificate-permissions get --spn <identity-client-id>
```
8. You can verify this has been done correctly by seeing the new additions to the access policy in the key vault. You should see one entry for the aks application with the different access levels for keys, secrets, and certificates.
9. Copy the `secrets-example.yaml` file to `secrets.yaml`. This file is gitignored
  a. The tenant id can be found as the subscription id of the aks created earlier.
  b. The objects array corresponds to the secrets in the key vault. Name these the same with lower case and `-`
  c. Secret objects contains groups of secrets that can be set on the deployed apps
  d. Object name matches the alias from the array
  e. The key is used in the deployment manifest
10. Update the manifest of the deployed app by adding the following to a container at its "root" level
```
env:
  - name: <NAME OF THE ENV VARIABLE IN THE APP
    valueFrom:
      secretKeyRef:
        name: <NAME OF THE GROUP OF SECRETS, secretName>
        key: <KEY OF THE SECRET>
```
11. Apply the secrets.yaml and then the manifest.yaml
12. Check that the pod is running without error `kubectl get pods`
