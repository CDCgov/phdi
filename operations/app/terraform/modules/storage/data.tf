# data "azurerm_client_config" "current" {}

# // Network

# data "azurerm_subnet" "public" {
#   name                 = "public"
#   virtual_network_name = "${var.resource_prefix}-vnet"
#   resource_group_name  = var.resource_group
# }

# data "azurerm_subnet" "container" {
#   name                 = "container"
#   virtual_network_name = "${var.resource_prefix}-vnet"
#   resource_group_name  = var.resource_group
# }

# data "azurerm_subnet" "endpoint" {
#   name                 = "endpoint"
#   virtual_network_name = "${var.resource_prefix}-vnet"
#   resource_group_name  = var.resource_group
# }

# data "azurerm_subnet" "public_subnet" {
#   name                 = "public"
#   virtual_network_name = "${var.resource_prefix}-East-vnet"
#   resource_group_name  = var.resource_group
# }

# data "azurerm_subnet" "container_subnet" {
#   name                 = "container"
#   virtual_network_name = "${var.resource_prefix}-East-vnet"
#   resource_group_name  = var.resource_group
# }

# data "azurerm_subnet" "endpoint_subnet" {
#   name                 = "endpoint"
#   virtual_network_name = "${var.resource_prefix}-East-vnet"
#   resource_group_name  = var.resource_group
# }


# // Key Vault

# data "azurerm_key_vault" "application" {
#   name                = "${var.resource_prefix}-keyvault"
#   resource_group_name = var.resource_group
# }

# data "azurerm_key_vault_secret" "hhsprotect_ip_ingress" {
#   name         = "hhsprotect-ip-ingress"
#   key_vault_id = data.azurerm_key_vault.application.id
# }

# data "azurerm_key_vault_secret" "cyberark_ip_ingress" {
#   name         = "cyberark-ip-ingress"
#   key_vault_id = data.azurerm_key_vault.application.id
# }

// Generate SAS token for Data Factory access to storage account
data "azurerm_storage_account_sas" "adf_sa_access" {
  connection_string = azurerm_storage_account.pdi_data.primary_connection_string
  https_only        = true
  signed_version    = "2020-08-04"

  resource_types {
    service   = true
    container = true
    object    = true
  }

  services {
    blob  = true
    queue = true
    table = true
    file  = true
  }

  start  = "2022-02-04T15:43:06Z"
  expiry = "2026-02-04T23:43:06Z"

  permissions {
    read    = true
    write   = true
    delete  = true
    list    = true
    add     = true
    create  = true
    update  = true
    process = true
  }

  depends_on = [azurerm_storage_account.pdi_data]
}
