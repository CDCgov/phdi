resource "azurerm_databricks_workspace" "databricks_VNET" {
  name                                  = "${var.resource_prefix}-databricks"
  location                              = var.location
  resource_group_name                   = var.resource_group_name
  sku                                   = "standard"
  public_network_access_enabled         = true
  network_security_group_rules_required = "AllRules"

  custom_parameters {
    virtual_network_id                                   = var.databricks_managed_vnet_id
    public_subnet_name                                   = "databricks-public"
    public_subnet_network_security_group_association_id  = var.databricks_public_subnet_network_security_group_association_id
    private_subnet_name                                  = "databricks-private"
    private_subnet_network_security_group_association_id = var.databricks_private_subnet_network_security_group_association_id
  }

  tags = {
    environment = var.environment
    managed-by  = "terraform"
  }
}
