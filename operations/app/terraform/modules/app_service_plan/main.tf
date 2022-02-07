resource "azurerm_app_service_plan" "pdi" {
  name                = "${var.resource_prefix}-serviceplan"
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "linux"
  reserved            = true

  sku {
    tier = var.app_tier
    size = var.app_size
  }

  tags = {
    environment = var.environment
  }
}