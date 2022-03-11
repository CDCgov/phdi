resource "azurerm_databricks_workspace" "pdi" {
  name                          = "${var.resource_prefix}-databricks"
  location                      = var.location
  resource_group_name           = var.resource_group_name
  sku                           = "standard"
  public_network_access_enabled = true

  custom_parameters {
    nat_gateway_name         = "${var.resource_prefix}-nat-gateway"
    no_public_ip             = false
    public_ip_name           = "${var.resource_prefix}-nat-gw-public-ip"
    storage_account_name     = "${var.resource_prefix}dbstorage"
    storage_account_sku_name = "Standard_GRS"
    vnet_address_prefix      = "10.139"
  }

  lifecycle {
    ignore_changes = [
      public_network_access_enabled,
      name,
      tags,
      custom_parameters
    ]
  }

  tags = {
    environment = var.environment
    managed-by  = "terraform"
  }
}
