variable "cdc_vnet_name" {
  type = string
  description = "Name of CDC vnet"
}

variable "app_subnet_name" {
  type = string
  description = "Name of app subnet within CDC vnet"
}

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

variable "service_subnet_name" {
  type = string
  description = "Name of service subnet within CDC vnet"
}

variable "route_table_id" {
  type = string
  description = "Route Table resource id"
}
