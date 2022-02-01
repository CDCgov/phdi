resource "azurerm_application_insights" "app_insights" {
  name                = "${var.resource_prefix}-appinsights"
  location            = var.location
  resource_group_name = var.resource_group_name
  application_type    = "web"
  workspace_id        = var.log_analytics_workspace_id

  tags = {
    environment = var.environment
  }
}
