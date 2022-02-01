variable "endpoint_subnet_ids" {
  type        = list(string)
  description = "IDs of subnet we'll create endpoints in"
}

variable "location" {
  type        = string
  description = "Network Location"
}

variable "name" {
  type        = string
  description = "The name of the resource for which an endpoint will be created"
}

variable "resource_group_name" {
  type        = string
  description = "Resource Group Name"
}

variable "resource_id" {
  type        = string
  description = "ID of the resource for which an endpoint will be created"
}

variable "type" {
  type        = string
  description = "Type of private endpoint to create. Options include: key_vault"
}