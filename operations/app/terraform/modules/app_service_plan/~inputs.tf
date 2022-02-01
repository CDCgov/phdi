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

variable "app_size" {}
variable "app_tier" {}