data "azurerm_client_config" "current" {}

resource "azurerm_storage_account" "pdi_data" {
  resource_group_name       = var.resource_group_name
  name                      = "${var.resource_prefix}datasa"
  location                  = var.location
  account_kind              = "StorageV2"
  account_tier              = "Standard"
  account_replication_type  = "GRS"
  min_tls_version           = "TLS1_2"
  allow_blob_public_access  = false
  enable_https_traffic_only = true
  is_hns_enabled            = true

  network_rules {
    default_action = "Deny"
    bypass         = ["AzureServices"]
    ip_rules = [
      "100.6.165.133",
      "136.226.6.186",
      "136.36.137.172",
      "158.111.21.225",
      "158.111.236.95",
      "24.163.118.70",
      "73.173.186.141",
    ]
    # ip_rules = sensitive(concat(
    #   split(",", data.azurerm_key_vault_secret.cyberark_ip_ingress.value),
    #   [split("/", var.terraform_caller_ip_address)[0]], # Storage accounts only allow CIDR-notation for /[0-30]
    # ))

    #ip_rules = [var.terraform_caller_ip_address]

    virtual_network_subnet_ids = var.app_subnet_ids
  }

  blob_properties {
    change_feed_enabled = false
    versioning_enabled  = false
  }

  # Required for customer-managed encryption
  identity {
    type = "SystemAssigned"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      tags
    ]
  }

  tags = {
    environment = var.environment
    managed-by  = "terraform"
  }
}

# Turns out that creating containers in storage accounts doesn't work like you'd expect; may be able
# to inline a template for it.
#
# See: https://github.com/hashicorp/terraform-provider-azurerm/issues/2977
# resource "azurerm_storage_container" "data_bronze" {
#   name                  = "bronze"
#   storage_account_name  = azurerm_storage_account.pdi_data.name
#   container_access_type = "private"
# }
# 
# resource "azurerm_storage_container" "data_silver" {
#   name                  = "silver"
#   storage_account_name  = azurerm_storage_account.pdi_data.name
#   container_access_type = "private"
# }
# 
# resource "azurerm_storage_container" "data_gold" {
#   name                  = "gold"
#   storage_account_name  = azurerm_storage_account.pdi_data.name
#   container_access_type = "private"
# }

/* Generate multiple storage private endpoints via for_each */
module "storageaccount_private_endpoint" {
  for_each = toset(["blob", "file", "queue"])
  source   = "../common/private_sa_endpoint"
  primary = {
    name                = "${azurerm_storage_account.pdi_data.name}-${each.key}-privateendpoint"
    type                = "storage_account_${each.key}"
    location            = "eastus"
    resource_group_name = var.resource_group_name
    environment         = var.environment
  }

  endpoint_subnet_ids = [var.cdc_service_subnet_id]

  private_dns_zone_group = {
    id                   = "${var.resource_group_id}/providers/Microsoft.Network/privateEndpoints/${azurerm_storage_account.pdi_data.name}-${each.key}-privateendpoint/privateDnsZoneGroups/default"
    name                 = "default"
    private_dns_zone_ids = "${var.resource_group_id}/providers/Microsoft.Network/privateDnsZones/privatelink.${each.key}.core.windows.net"
  }

  private_service_connection = {
    is_manual_connection           = false
    name                           = "${azurerm_storage_account.pdi_data.name}-${each.key}-privateendpoint"
    private_connection_resource_id = azurerm_storage_account.pdi_data.id
    subresource_names              = "${each.key}"
  }

  depends_on = [azurerm_storage_account.pdi_data]
}

# Point-in-time restore, soft delete, versioning, and change feed were
# enabled in the portal as terraform does not currently support this.
# At some point, this should be moved into an azurerm_template_deployment
# resource.
# These settings can be configured under the "Data protection" blade
# for Blob service

# Grant the storage account Key Vault access, to access encryption keys
resource "azurerm_key_vault_access_policy" "storage_policy" {
  key_vault_id = var.application_key_vault_id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_storage_account.pdi_data.identity.0.principal_id

  key_permissions = ["Get", "UnwrapKey", "WrapKey"]
}

resource "azurerm_storage_account_customer_managed_key" "storage_key" {
  count              = var.rsa_key_4096 != null && var.rsa_key_4096 != "" ? 1 : 0
  key_name           = var.rsa_key_4096
  key_vault_id       = var.application_key_vault_id
  key_version        = null // Null allows automatic key rotation
  storage_account_id = azurerm_storage_account.pdi_data.id

  depends_on = [azurerm_key_vault_access_policy.storage_policy]
}
