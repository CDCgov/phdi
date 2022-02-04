output "function_app_id" {
  value = azurerm_function_app.pdi.id
}

output "function_infrastructure_app_id" {
  value = azurerm_function_app.pdi_infrastructure.id
}
