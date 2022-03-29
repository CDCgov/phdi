resource "azurerm_function_app" "pdi" {
  name                       = "${var.resource_prefix}-functionapp"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  app_service_plan_id        = var.app_service_plan
  https_only                 = true
  os_type                    = "linux"
  version                    = "~3"
  enable_builtin_logging     = false
  storage_account_name       = var.sa_functionapps.name
  storage_account_access_key = var.sa_functionapps.primary_access_key

  app_settings = {
    WEBSITE_DNS_SERVER = "168.63.129.16"

    # App Insights
    PRIVATE_KEY                           = "@Microsoft.KeyVault(SecretUri=https://${var.resource_prefix}-app-kv.vault.azure.net/secrets/PrivateKey)"
    PRIVATE_KEY_PASSWORD                  = "@Microsoft.KeyVault(SecretUri=https://${var.resource_prefix}-app-kv.vault.azure.net/secrets/PrivateKeyPassword)"
    AZURE_STORAGE_CONTAINER_NAME          = "bronze"
    APPINSIGHTS_INSTRUMENTATIONKEY        = var.ai_instrumentation_key
    APPLICATIONINSIGHTS_CONNECTION_STRING = var.ai_connection_string
    BUILD_FLAGS                           = "UseExpressBuild"
    FUNCTIONS_WORKER_RUNTIME              = "python"
    SCM_DO_BUILD_DURING_DEPLOYMENT        = true
    VDHSFTPHostname                       = "vdhsftp.vdh.virginia.gov"
    VDHSFTPPassword                       = "@Microsoft.KeyVault(SecretUri=https://${var.resource_prefix}-app-kv.vault.azure.net/secrets/VDHSFTPPassword)"
    VDHSFTPUsername                       = "USDS_CDC"
    XDG_CACHE_HOME                        = "/tmp/.cache"
    WEBSITE_RUN_FROM_PACKAGE              = 1
    DATA_STORAGE_ACCOUNT                  = var.sa_data_name
  }

  site_config {
    ftps_state = "Disabled"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    environment = var.environment
    managed-by  = "terraform"
  }

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

resource "azurerm_function_app" "infrastructure" {
  name                       = "${var.resource_prefix}-infra-functionapp"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  app_service_plan_id        = var.app_service_plan
  https_only                 = true
  os_type                    = "linux"
  version                    = "~3"
  enable_builtin_logging     = false
  storage_account_name       = var.sa_functionapps.name
  storage_account_access_key = var.sa_functionapps.primary_access_key

  app_settings = {
    APPINSIGHTS_INSTRUMENTATIONKEY        = var.ai_instrumentation_key
    APPLICATIONINSIGHTS_CONNECTION_STRING = var.ai_connection_string
    BUILD_FLAGS                           = "UseExpressBuild"
    FUNCTIONS_WORKER_RUNTIME              = "python"
    SCM_DO_BUILD_DURING_DEPLOYMENT        = true
    WEBSITE_DNS_SERVER                    = "168.63.129.16"
    WEBSITE_RUN_FROM_PACKAGE              = 1
    WEBSITES_ENABLE_APP_SERVICE_STORAGE   = false
    XDG_CACHE_HOME                        = "/tmp/.cache"
    DATA_STORAGE_ACCOUNT                  = var.sa_data_name
  }

  lifecycle {
    ignore_changes = [
      tags
    ]
  }

  identity {
    type = "SystemAssigned"
  }

  site_config {
    ftps_state                = "Disabled"
    use_32_bit_worker_process = false
    vnet_route_all_enabled    = true
  }

  tags = {
    environment = var.environment
    managed-by  = "terraform"
  }
}

resource "azurerm_key_vault_access_policy" "pdi_function_app" {
  key_vault_id = var.application_key_vault_id
  tenant_id    = azurerm_function_app.pdi.identity.0.tenant_id
  object_id    = azurerm_function_app.pdi.identity.0.principal_id

  secret_permissions = [
    "Get",
  ]
}

resource "azurerm_key_vault_access_policy" "pdi_infrastructure_app" {
  key_vault_id = var.application_key_vault_id
  tenant_id    = azurerm_function_app.infrastructure.identity.0.tenant_id
  object_id    = azurerm_function_app.infrastructure.identity.0.principal_id

  secret_permissions = [
    "Get",
  ]
}

resource "azurerm_app_service_virtual_network_swift_connection" "pdi_function_app" {
  app_service_id = azurerm_function_app.pdi.id
  subnet_id      = var.cdc_app_subnet_id
}

resource "azurerm_app_service_virtual_network_swift_connection" "pdi_infrastructure_app" {
  app_service_id = azurerm_function_app.infrastructure.id
  subnet_id      = var.cdc_app_subnet_id
}
