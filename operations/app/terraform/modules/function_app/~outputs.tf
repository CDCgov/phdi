output "function_app_id" {
  value = azurerm_function_app.function_app.id
}

output "function_infrastructure_app_id" {
  value = azurerm_function_app.infrastructure_app.id
}
