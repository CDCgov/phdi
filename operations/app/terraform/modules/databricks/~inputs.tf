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

variable "databricks_managed_vnet_id" {
  type        = string
  description = "ID of the Databricks managed VNET"
}

variable "databricks_public_subnet_network_security_group_association_id" {
  type        = string
  description = "ID of the Databricks public subnet network security group association"
}

variable "databricks_private_subnet_network_security_group_association_id" {
  type        = string
  description = "ID of the Databricks private subnet network security group association"
}
