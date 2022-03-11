resource "azurerm_healthcare_service" "pdi" {
  name                = "${var.resource_prefix}-fhir"
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "fhir-R4"
  cosmosdb_throughput = 400

  access_policy_object_ids = []

  lifecycle {
    ignore_changes = [name, tags]
  }

  tags = {
    environment = var.environment
    managed-by  = "terraform"
  }
}
