variable "primary" {
  type = object({
    name                = string
    resource_group_name = string
    environment         = string
    resource_prefix     = string
  })
}

variable "dns_zone_names" {
  type        = list(string)
  description = "List of DNS zone names, ex. ['privatelink.vaultcore.azure.net']"
}

variable "vnet" {
  type        = object({ id = string, name = string })
  description = "VNET to associate the DNS zones with"
}
