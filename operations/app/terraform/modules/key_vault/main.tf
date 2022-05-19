# this empty call gives us the current client_id, tenant_id, subscription_id, and object_id (?)
data "azurerm_client_config" "current" {}

# Note that the CDC created their own key vault called "prime-ingestion-test-ts" that's not managed by Terraform


resource "azurerm_key_vault" "application" {
  # NOTE: if this key vault gets deleted (via terraform destroy) you'll have to rename the keyvault, as
  # Azure issues a soft delete so you can recover when you accidentally delete your secrets.
  name                            = "${var.resource_prefix}-app-kv"
  location                        = var.location
  resource_group_name             = var.resource_group_name
  sku_name                        = "premium"
  tenant_id                       = data.azurerm_client_config.current.tenant_id
  enabled_for_deployment          = true
  enabled_for_disk_encryption     = true
  enabled_for_template_deployment = true
  purge_protection_enabled        = true

  network_acls {
    bypass         = "AzureServices"
    default_action = "Deny"

    ip_rules = var.terraform_caller_ip_address

    virtual_network_subnet_ids = toset([var.cdc_app_subnet_id])
  }

  lifecycle {
    prevent_destroy = false
    ignore_changes = [
      tags,
      network_acls[0].ip_rules
    ]
  }

  tags = {
    "environment" = var.environment
    managed-by    = "terraform"
  }
}

resource "azurerm_key_vault_access_policy" "adf_access_policy" {
  key_vault_id = azurerm_key_vault.application.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = var.adf_uuid

  secret_permissions = [
    "Get",
    "List"
  ]
}

resource "azurerm_key_vault_access_policy" "dev_access_policy" {
  key_vault_id = azurerm_key_vault.application.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = var.aad_object_keyvault_admin

  key_permissions = [
    "Get",
    "List",
    "Update",
    "Create",
    "Import",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
  ]

  secret_permissions = [
    "Get",
    "List",
    "Set",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
  ]

  certificate_permissions = [
    "Get",
    "List",
    "Update",
    "Create",
    "Import",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
    "ManageContacts",
    "ManageIssuers",
    "GetIssuers",
    "ListIssuers",
    "SetIssuers",
    "DeleteIssuers",
  ]
}
