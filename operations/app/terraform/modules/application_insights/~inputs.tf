variable "environment" {
  type        = string
  description = "Target Environment"
}

variable "resource_group_name" {
  type        = string
  description = "Resource Group Name"
}

variable "location" {
  type        = string
  description = "Function App Location"
}

variable "resource_prefix" {
  type        = string
  description = "Resource Prefix"
}

variable "service_plan_id" {}

variable "log_analytics_workspace_id" {
  type        = string
  description = "Log Analytics Workspace resource id"
}
