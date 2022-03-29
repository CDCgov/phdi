output "sa_data_name" {
  value = azurerm_storage_account.pdi_data.name
}

output "sa_data_id" {
  value = azurerm_storage_account.pdi_data.id
}

output "sa_functionapps" {
  value = azurerm_storage_account.function_apps
}
