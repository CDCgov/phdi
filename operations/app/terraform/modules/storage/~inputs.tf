variable "application_key_vault_id" {}

variable "cdc_subnet_ids" {
  description = "IDs of subnets in the CDC vnet"
}

variable "app_subnet_ids" {
  description = "IDs of app subnets in the CDC vnet"
}

variable "databricks_subnet_ids" {
  description = "IDs of subnets in the Databricks vnet"
}

variable "cdc_service_subnet_id" {
  description = "ID of service subnet in the CDC vnet"
}

variable "environment" {
  type        = string
  description = "Target Environment"
}

variable "location" {
  type        = string
  description = "Storage Account Location"
}

variable "resource_group_name" {
  type        = string
  description = "Resource Group Name"
}

variable "resource_prefix" {
  type        = string
  description = "Resource Prefix"
}

variable "rsa_key_4096" {
  type        = string
  description = "Name of the 2048 length RSA key in the Key Vault. Omitting will use Azure-managed key instead of a customer-key."
}

variable "terraform_caller_ip_address" {
  type        = list(string)
  description = "The IP address of the Terraform script caller. This IP will have already been whitelisted; its inclusion is to prevent its removal during terraform apply calls."
  sensitive   = true
}

variable "use_cdc_managed_vnet" {
  type        = bool
  description = "If the environment should be deployed to the CDC managed VNET"
}

variable "resource_group_id" {
  type        = string
  description = "Resource Group resource id"
}

variable "data_access_group" {
  type        = string
  description = "AD group to grant data access"
}

variable "data_access_sp" {
  type        = string
  description = "Service principal to grant data access"
}

variable "adf_uuid" {
  type        = string
  description = "Azure Data Factory resource uuid"
}

variable "python_function_app_uuid" {
  type        = string
  description = "Python function app resource uuid"
}
