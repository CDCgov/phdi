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

variable "private_dns_zone_group" {
  type = object({
    id                   = string
    name                 = string
    private_dns_zone_ids = string
  })
}

variable "private_service_connection" {
  type = object({
    is_manual_connection           = string
    name                           = string
    private_connection_resource_id = string
    subresource_names              = string
  })
}
