locals {
  default = {
    "infrastructure_function_app" = {
      id    = var.infrastructure_function_app_id
      name  = "infrastructure_function_app"
      diags = data.azurerm_monitor_diagnostic_categories.infrastructure_function_app
    },
    "pdi_function_app" = {
      id    = var.pdi_function_app_id
      name  = "pdi_function_app"
      diags = data.azurerm_monitor_diagnostic_categories.pdi_function_app
    },
    "app_service_plan" = {
      id    = var.app_service_plan_id
      name  = "app_service_plan"
      diags = data.azurerm_monitor_diagnostic_categories.app_service_plan
    },
    "cdc_managed_vnet" = {
      id    = var.cdc_managed_vnet_id
      name  = "cdc_managed_vnet"
      diags = data.azurerm_monitor_diagnostic_categories.cdc_managed_vnet
    },
    "sa_data" = {
      id    = var.sa_data_id
      name  = "sa_data"
      diags = data.azurerm_monitor_diagnostic_categories.sa_data
    },
    "adf" = {
      id    = var.adf_id
      name  = "adf"
      diags = data.azurerm_monitor_diagnostic_categories.adf
    },
    "fhir" = {
      id    = var.healthcare_service_id
      name  = "fhir"
      diags = data.azurerm_monitor_diagnostic_categories.fhir
    }
  }
}

data "azurerm_monitor_diagnostic_categories" "infrastructure_function_app" {
  resource_id = var.infrastructure_function_app_id
}

data "azurerm_monitor_diagnostic_categories" "pdi_function_app" {
  resource_id = var.pdi_function_app_id
}

data "azurerm_monitor_diagnostic_categories" "app_service_plan" {
  resource_id = var.app_service_plan_id
}

data "azurerm_monitor_diagnostic_categories" "cdc_managed_vnet" {
  resource_id = var.cdc_managed_vnet_id
}

data "azurerm_monitor_diagnostic_categories" "sa_data" {
  resource_id = var.sa_data_id
}

data "azurerm_monitor_diagnostic_categories" "adf" {
  resource_id = var.adf_id
}

data "azurerm_monitor_diagnostic_categories" "fhir" {
  resource_id = var.healthcare_service_id
}
