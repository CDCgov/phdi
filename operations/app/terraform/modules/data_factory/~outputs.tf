output "adf_uuid" {
  value = azurerm_data_factory.pdi.identity[0].principal_id
}

output "adf_id" {
  value = azurerm_data_factory.pdi.id
}
