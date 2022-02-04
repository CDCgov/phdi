data "azurerm_key_vault_secret" "vdhsftp" {
  name         = "VDHSFTPPassword"
  key_vault_id = azurerm_key_vault.application.id
}
