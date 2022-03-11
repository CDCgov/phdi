resource "azurerm_application_insights" "pdi" {
  name                = "${var.resource_prefix}-appinsights"
  location            = var.location
  resource_group_name = var.resource_group_name
  application_type    = "web"
  workspace_id        = var.log_analytics_workspace_id

  tags = {
    environment = var.environment
    managed-by  = "terraform"
    // hard code automated tags where "ignore-tags" is not supported
    created-at = "2022-03-08T21:32+00:00"
    created-by = "TEY1-SU@cdc.gov"
  }
}
