output "pdi_function_app" {
  value = azurerm_function_app.pdi
}

output "pdi_function_app_uuid" {
  value = azurerm_function_app.pdi.identity[0].principal_id
}

output "infrastructure_function_app" {
  value = azurerm_function_app.infrastructure
}

output "infrastructure_function_app_uuid" {
  value = azurerm_function_app.infrastructure.identity[0].principal_id
}
