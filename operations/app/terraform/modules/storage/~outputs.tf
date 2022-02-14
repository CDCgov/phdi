output "sa_data_access_key" {
  value = azurerm_storage_account.pdi_data.primary_access_key
}

output "sa_data_connection_string" {
  value = azurerm_storage_account.pdi_data.primary_connection_string
}

output "sa_data_name" {
  value = azurerm_storage_account.pdi_data.name
}

output "sa_data_id" {
  value = azurerm_storage_account.pdi_data.id
}

output "sa_data_adf_sas" {
  value     = data.azurerm_storage_account_sas.adf_sa_access.sas
  sensitive = true
}
