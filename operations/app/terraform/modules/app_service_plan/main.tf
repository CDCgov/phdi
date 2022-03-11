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
    managed-by  = "terraform"
    // hard code automated tags where "ignore-tags" is not supported
    created-at = "2022-03-08T21:32+00:00"
    created-by = "TEY1-SU@cdc.gov"
  }
}
