resource "azurerm_data_factory" "pdi" {
  name                            = "${var.resource_prefix}-df"
  location                        = var.location
  resource_group_name             = var.resource_group_name
  public_network_enabled          = false
  managed_virtual_network_enabled = true

  identity {
    type = "SystemAssigned"
  }

  lifecycle {
    ignore_changes = [
      tags
    ]
  }

  tags = {
    environment = var.environment
    managed-by  = "terraform"
  }
}

resource "azurerm_data_factory_integration_runtime_azure" "pdi" {
  name                    = "${var.resource_prefix}-ir"
  data_factory_id         = azurerm_data_factory.pdi.id
  resource_group_name     = var.resource_group_name
  location                = var.location
  virtual_network_enabled = true
  time_to_live_min        = 10
}

resource "azurerm_data_factory_managed_private_endpoint" "pdi_appkv" {
  name               = replace("${var.resource_prefix}-app-kv-privateendpoint", "-", "_")
  data_factory_id    = azurerm_data_factory.pdi.id
  target_resource_id = var.application_key_vault_id
  subresource_name   = "vault"

  lifecycle {
    ignore_changes = [
      fqdns
    ]
  }

  timeouts {}
}

resource "azurerm_data_factory_managed_private_endpoint" "pdi_datasa" {
  name               = replace("${var.resource_prefix}datasa-privateendpoint", "-", "_")
  data_factory_id    = azurerm_data_factory.pdi.id
  target_resource_id = var.sa_data_id
  subresource_name   = "blob"

  lifecycle {
    ignore_changes = [
      fqdns
    ]
  }

  timeouts {}
}
