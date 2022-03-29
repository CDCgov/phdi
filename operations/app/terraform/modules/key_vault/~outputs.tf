output "application_key_vault_id" {
  value = azurerm_key_vault.application.id
}

# output "adf_sa_sas_name" {
#   value = azurerm_key_vault_secret.adf_sa_access.name
# }

# output "adf_sa_sas_id" {
#   value = azurerm_key_vault_secret.adf_sa_access.id
# }

output "vdhsftp_pass" {
  value     = data.azurerm_key_vault_secret.vdhsftp.value
  sensitive = true
}