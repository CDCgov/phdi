resource "azurerm_private_endpoint" "sa_endpoint" {
  count               = length(var.endpoint_subnet_ids)
  name                = var.primary.name
  location            = var.primary.location
  resource_group_name = var.primary.resource_group_name
  subnet_id           = var.endpoint_subnet_ids[count.index]

  private_dns_zone_group {
    name                 = var.private_dns_zone_group.name
    private_dns_zone_ids = [var.private_dns_zone_group.private_dns_zone_ids]
  }

  private_service_connection {
    is_manual_connection           = var.private_service_connection.is_manual_connection
    name                           = var.private_service_connection.name
    private_connection_resource_id = var.private_service_connection.private_connection_resource_id
    subresource_names              = [var.private_service_connection.subresource_names]
  }
}
