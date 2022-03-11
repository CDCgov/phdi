variable "location" {
  type        = string
  description = "Network Location"
}

variable "resource_group_name" {
  type        = string
  description = "Resource Group Name"
}

variable "resource_prefix" {
  type        = string
  description = "Resource Prefix"
}

variable "function_app_id" {
  type        = string
  description = "Function app resource id"
}

variable "function_infrastructure_app_id" {
  type        = string
  description = "Infrastructure function app resource id"
}

variable "app_service_plan_id" {
  type        = string
  description = "App Service Plan resource id"
}

variable "cdc_managed_vnet_id" {
  type        = string
  description = "CDC Vnet resource id"
}

variable "sa_data_id" {
  type        = string
  description = "Data storage account id"
}

variable "adf_id" {
  type        = string
  description = "Data Factory resource id"
}

variable "healthcare_service_id" {
  type        = string
  description = "FHIR service resource id"
}

variable "databricks_workspace_id" {
  type        = string
  description = "Databricks resource id"
}

variable "environment" {
  type        = string
  description = "Target Environment"
}
