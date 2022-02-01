## Let's get our secrets from the secrets key vault
## Note, this will need to be pre-populated

# data "azurerm_key_vault" "tf-secrets" {
#  name                = var.tf_secrets_vault
#  resource_group_name = var.resource_group
# }