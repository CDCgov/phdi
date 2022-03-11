resource "azurerm_route_table" "pdi" {
  name                          = var.route_table_name
  location                      = var.location
  resource_group_name           = var.resource_group_name
  disable_bgp_route_propagation = true

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      tags
    ]
  }

  tags = {
    environment = var.environment
  }
}

resource "azurerm_route" "Net_10000-8" {
  name                   = "Net_10.0.0.0-8"
  route_table_name       = var.route_table_name
  resource_group_name    = var.resource_group_name
  address_prefix         = "10.0.0.0/8"
  next_hop_type          = "VirtualAppliance"
  next_hop_in_ip_address = "172.30.6.20"
}

resource "azurerm_route" "Net_15811100-0" {
  name                   = "Net_158.111.0.0-0"
  route_table_name       = var.route_table_name
  resource_group_name    = var.resource_group_name
  address_prefix         = "158.111.0.0/16"
  next_hop_type          = "VirtualAppliance"
  next_hop_in_ip_address = "172.30.6.20"
}

resource "azurerm_route" "Net_1721600-12" {
  name                   = "Net_172.16.0.0-12"
  route_table_name       = var.route_table_name
  resource_group_name    = var.resource_group_name
  address_prefix         = "172.16.0.0/12"
  next_hop_type          = "VirtualAppliance"
  next_hop_in_ip_address = "172.30.6.20"
}

resource "azurerm_route" "Net_1581112360-24" {
  name                   = "Net_158.111.236.0-24"
  route_table_name       = var.route_table_name
  resource_group_name    = var.resource_group_name
  address_prefix         = "158.111.236.0/24"
  next_hop_type          = "VirtualAppliance"
  next_hop_in_ip_address = "172.30.6.25"
}

resource "azurerm_route" "cspo-az-ext" {
  name                = "cspo-az-ext"
  route_table_name    = var.route_table_name
  resource_group_name = var.resource_group_name
  address_prefix      = "172.30.6.64/28"
  next_hop_type       = "None"
}

resource "azurerm_route" "CSPO-AZ-MGMT" {
  name                = "CSPO-AZ-MGMT"
  route_table_name    = var.route_table_name
  resource_group_name = var.resource_group_name
  address_prefix      = "172.30.6.96/27"
  next_hop_type       = "None"
}

resource "azurerm_route" "Net_19216800-16" {
  name                   = "Net_192.168.0.0-16"
  route_table_name       = var.route_table_name
  resource_group_name    = var.resource_group_name
  address_prefix         = "192.168.0.0/16"
  next_hop_type          = "VirtualAppliance"
  next_hop_in_ip_address = "172.30.6.20"
}

resource "azurerm_route" "Net_198246960-19" {
  name                   = "Net_198.246.96.0-19"
  route_table_name       = var.route_table_name
  resource_group_name    = var.resource_group_name
  address_prefix         = "198.246.96.0/19"
  next_hop_type          = "VirtualAppliance"
  next_hop_in_ip_address = "172.30.6.20"
}

resource "azurerm_route" "UDR-Default" {
  name                   = "UDR-Default"
  route_table_name       = var.route_table_name
  resource_group_name    = var.resource_group_name
  address_prefix         = "0.0.0.0/0"
  next_hop_type          = "VirtualAppliance"
  next_hop_in_ip_address = "172.30.6.20"
}
