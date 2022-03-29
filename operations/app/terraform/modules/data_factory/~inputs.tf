variable "environment" {
  type        = string
  description = "Target Environment"
}

variable "location" {
  type        = string
  description = "Function App Location"
}

variable "resource_group_name" {
  type        = string
  description = "Resource Group Name"
}

variable "resource_prefix" {
  type        = string
  description = "Resource Prefix"
}

variable "application_key_vault_id" {
  type        = string
  description = "Application Key Vault resource id"
}

variable "sa_data_id" {
  type        = string
  description = "Data storage account id"
}

variable "vdhsftp_pass" {
  type        = string
  description = "Password for VDH SFTP"
  sensitive   = true
}
