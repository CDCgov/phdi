output "ai_instrumentation_key" {
  value = azurerm_application_insights.pdi.instrumentation_key
}

output "ai_app_id" {
  value = azurerm_application_insights.pdi.app_id
}

output "ai_connection_string" {
  value = azurerm_application_insights.pdi.connection_string
}