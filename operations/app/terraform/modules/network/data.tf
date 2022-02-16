locals {
  #   dns_zones_private = [
  #     "privatelink.vaultcore.azure.net",
  #     "privatelink.postgres.database.azure.com",
  #     "privatelink.blob.core.windows.net",
  #     "privatelink.file.core.windows.net",
  #     "privatelink.queue.core.windows.net",
  #     #"privatelink.azurecr.io",
  #     "privatelink.servicebus.windows.net",
  #     "privatelink.azurewebsites.net",
  #     "prime.local",
  #   ]

  #   # Due to only a single DNS record allowed per resource group, some private endpoints conflicts in with multiple VNETs
  #   # By omitting the DNS records, we ensure the Azure backbone is used instead of attempting to reach an unpeered VNET
  #   omit_dns_zones_private_in_cdc_vnet = [
  #     "privatelink.vaultcore.azure.net",
  #   ]

  # not sure if these are still needed... we may turn them into outputs instead...
  # vnet_primary_name = var.cdc_vnet_name
  # vnet_primary      = data.azurerm_virtual_network.cdc_vnet[local.vnet_primary_name]
  # vnet_names = [
  #   local.vnet_primary_name
  # ]
}

# we need this data lookup because we need to reference/manipulate
# the CDC-managed VNet
data "azurerm_virtual_network" "cdc_vnet" {
  name                = var.cdc_vnet_name
  resource_group_name = var.resource_group_name
}

# Note that I manually added to this subnet the equivalent of the following
#
#   # via the UI
#   service_endpoints    = [
#     "Microsoft.Storage",
#     "Microsoft.KeyVault",
#     "Microsoft.ContainerRegistry",
#   ],
#
#   # via the UI: this is required to put a functionapp in the subnet
#   delegation {
#     name = "server_farms"
#     service_delegation {
#       name    = "Microsoft.Web/serverFarms"
#       actions = [
#         "Microsoft.Network/virtualNetworks/subnets/action",
#       ]
#     }
#   }
#
#   # via the CLI, see: https://docs.microsoft.com/en-us/azure/private-link/disable-private-endpoint-network-policy#azure-cli
#   enforce_private_link_endpoint_network_policies = true  # true = disable, false = enable