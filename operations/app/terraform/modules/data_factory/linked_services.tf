resource "azurerm_data_factory_linked_service_azure_function" "pdi_func" {
  name                     = "AzureFunction1"
  resource_group_name      = var.resource_group_name
  data_factory_id          = azurerm_data_factory.pdi.id
  integration_runtime_name = azurerm_data_factory_integration_runtime_azure.pdi.name
  url                      = "https://${var.resource_prefix}-functionapp.azurewebsites.net"

  key_vault_key {
    linked_service_name = azurerm_data_factory_linked_service_key_vault.pdi_appkv.name
    secret_name         = "${var.resource_prefix}functionappaccess"
  }
}

resource "azurerm_data_factory_linked_service_key_vault" "pdi_appkv" {
  name                = "${var.resource_prefix}_app_kv"
  resource_group_name = var.resource_group_name
  data_factory_id     = azurerm_data_factory.pdi.id
  key_vault_id        = var.application_key_vault_id
}

resource "azurerm_data_factory_linked_service_azure_blob_storage" "pdi_datasa" {
  name                     = "${var.resource_prefix}datastorage"
  resource_group_name      = var.resource_group_name
  data_factory_id          = azurerm_data_factory.pdi.id
  integration_runtime_name = azurerm_data_factory_integration_runtime_azure.pdi.name
  use_managed_identity     = true
  service_endpoint         = "https://${var.resource_prefix}datasa${var.environment == "skylight" ? "1" : ""}.blob.core.windows.net"
}

resource "azurerm_data_factory_linked_service_sftp" "vdh" {
  name                     = "vdhsftp"
  resource_group_name      = var.resource_group_name
  data_factory_id          = azurerm_data_factory.pdi.id
  authentication_type      = "Basic"
  host                     = "vdhsftp.vdh.virginia.gov"
  port                     = 22
  username                 = "USDS_CDC"
  password                 = var.vdhsftp_pass
  skip_host_key_validation = true
  integration_runtime_name = azurerm_data_factory_integration_runtime_azure.pdi.name
}
