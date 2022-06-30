output "cdc_app_subnet_id" {
  value = azurerm_subnet.cdc_app_subnet.id
}

output "cdc_service_subnet_id" {
  value = azurerm_subnet.cdc_service_subnet.id
}

# output "dev_app_subnet_id" {
#   value = azurerm_subnet.dev_app_subnet.id
# }
# 
# output "dev_service_subnet_id" {
#   value = azurerm_subnet.dev_service_subnet.id
# }

output "private_nsg_id" {
  value = azurerm_network_security_group.vnet_nsg_private.id
}

output "app_subnet_ids" {
  value = toset([
    azurerm_subnet.cdc_app_subnet.id,
    #    azurerm_subnet.dev_app_subnet.id,
  ])
}

output "cdc_subnet_ids" {
  value = toset([
    azurerm_subnet.cdc_app_subnet.id,
    azurerm_subnet.cdc_service_subnet.id
  ])
}

# output "dev_subnet_ids" {
#   value = toset([
#     azurerm_subnet.dev_app_subnet.id,
#     azurerm_subnet.dev_service_subnet.id
#   ])
# }

output "service_subnet_ids" {
  value = toset([
    azurerm_subnet.cdc_service_subnet.id,
    #    azurerm_subnet.dev_service_subnet.id,
  ])
}

# output "public_subnet_ids" {
#   value = azurerm_subnet.public_subnet[*].id
# }
# 
# output "container_subnet_ids" {
#   value = azurerm_subnet.container_subnet[*].id
# }
# 
# output "private_subnet_ids" {
#   value = azurerm_subnet.private_subnet[*].id
# }
# 
# output "endpoint_subnet_ids" {
#   value = azurerm_subnet.endpoint_subnet[*].id
# }

output "cdc_managed_vnet_id" {
  value = data.azurerm_virtual_network.cdc_vnet.id
}

output "databricks_managed_vnet_id" {
  value = azurerm_virtual_network.databricks_vnet.id
}

output "databricks_subnet_ids" {
  value = toset([
    azurerm_subnet.databricks_vnet_public_subnet.id,
    azurerm_subnet.databricks_vnet_private_subnet.id
  ])
}

output "databricks_public_subnet_nsg_association_id" {
  value = azurerm_subnet_network_security_group_association.databricks_vnet_public_subnet_nsg_association.id
}

output "databricks_private_subnet_nsg_association_id" {
  value = azurerm_subnet_network_security_group_association.databricks_vnet_private_subnet_nsg_association.id
}
