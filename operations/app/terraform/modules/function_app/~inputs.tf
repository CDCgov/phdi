variable "ai_instrumentation_key" {
  type        = string
  description = "Application Insights Instrumentation Key"
  sensitive   = true
}

variable "ai_connection_string" {
  type        = string
  description = "Application Insights Connection String"
  sensitive   = true
}

variable "app_service_plan" {}

variable "application_key_vault_id" {}

variable "cdc_app_subnet_id" {}

variable "environment" {
  type        = string
  description = "Target Environment"
}

variable "location" {
  type        = string
  description = "Function App Location"
}

variable "sa_datastorage_access_key" {
  type        = string
  description = "Data storage account access key"
}

variable "sa_datastorage_connection_string" {
  type        = string
  description = "Data storage account connection string"
}

variable "sa_datastorage_name" {
  type        = string
  description = "Data storage account name"
}

variable "resource_group_name" {
  type        = string
  description = "Resource Group Name"
}

variable "resource_prefix" {
  type        = string
  description = "Resource Prefix"
}

variable "terraform_caller_ip_address" {
  type        = string
  description = "The IP address of the Terraform script caller. This IP will have already been whitelisted; it's inclusion is to prevent its removal during terraform apply calls."
  sensitive   = true
}

variable "use_cdc_managed_vnet" {
  type        = bool
  description = "If the environment should be deployed to the CDC managed VNET"
}