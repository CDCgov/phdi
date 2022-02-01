output "sa_datastorage_access_key" {
  value = azurerm_storage_account.storage_account.primary_access_key
}

output "sa_datastorage_connection_string" {
  value = azurerm_storage_account.storage_account.primary_connection_string
}

output "sa_datastorage_name" {
  value = azurerm_storage_account.storage_account.name
}

output "sa_datastorage_id" {
  value = azurerm_storage_account.storage_account.id
}
