#data "azurerm_client_config" "current" {}

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
  shared_access_key_enabled = false

  network_rules {
    default_action = "Deny"
    bypass         = ["AzureServices"]

    virtual_network_subnet_ids = setunion(var.app_subnet_ids, var.databricks_subnet_ids)
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
      tags,
      network_rules[0].ip_rules
    ]
  }

  tags = {
    environment = var.environment
    managed-by  = "terraform"
  }
}

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

# Function apps store their required configuration files in a dedicated storage account.
# Grant function apps full access to this storage account, while limiting their access to others.
resource "azurerm_storage_account" "function_apps" {
  resource_group_name       = var.resource_group_name
  name                      = "${var.resource_prefix}functionapps"
  location                  = var.location
  account_kind              = "StorageV2"
  account_tier              = "Standard"
  account_replication_type  = "GRS"
  min_tls_version           = "TLS1_2"
  allow_blob_public_access  = false
  enable_https_traffic_only = true


  network_rules {
    default_action = "Deny"
    bypass         = ["AzureServices"]

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
      tags,
      shared_access_key_enabled,
      network_rules[0].ip_rules
    ]
  }

  tags = {
    environment = var.environment
    managed-by  = "terraform"
  }
}
