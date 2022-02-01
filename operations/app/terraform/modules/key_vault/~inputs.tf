variable "aad_object_keyvault_admin" {
  type        = string
  description = "Azure Active Directory ID for a user or group who will be given write access to Key Vaults"
}

variable "cdc_app_subnet_id" {}
variable "cdc_subnet_ids" {}

variable "cyberark_ip_ingress" {}

variable "environment" {
  type        = string
  description = "Target Environment"
}

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

variable "terraform_caller_ip_address" {
  type        = string
  description = "The IP address of the Terraform script caller. This IP will have already been whitelisted; it's inclusion is to prevent its removal during terraform apply calls."
  sensitive   = true
}

variable "terraform_object_id" {}

variable "use_cdc_managed_vnet" {
  type        = bool
  description = "If the environment should be deployed to the CDC managed VNET"
}