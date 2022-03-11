variable "primary" {
  type = object({
    name                = string
    type                = string
    location            = string
    resource_group_name = string
    environment         = string
  })
}

variable "endpoint_subnet_ids" {
  type        = list(string)
  description = "IDs of subnet we'll create endpoints in"
}

variable "resource_id" {
  type        = string
  description = "ID of the resource for which an endpoint will be created"
}
