resource "azurerm_storage_data_lake_gen2_filesystem" "pdi_data" {
  for_each           = toset(local.data_containers)
  name               = each.value
  storage_account_id = azurerm_storage_account.pdi_data.id
  owner              = data.azuread_group.owners.id
  group              = data.azuread_group.owners.id
  properties         = {}

  dynamic "ace" {
    for_each = local.data_ace_access
    content {
      id          = ace.value.id
      permissions = ace.value.permissions
      scope       = ace.value.scope
      type        = ace.value.type
    }
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "azurerm_storage_data_lake_gen2_path" "pdi_data_bronze" {
  for_each           = { for entry in local.bronze_mapping : "${entry.bronze_root_dir}${entry.bronze_sub_dir}" => entry }
  filesystem_name    = azurerm_storage_data_lake_gen2_filesystem.pdi_data["bronze"].name
  storage_account_id = azurerm_storage_account.pdi_data.id
  resource           = "directory"
  owner              = data.azuread_group.owners.id
  group              = data.azuread_group.owners.id
  path               = "${each.value.bronze_root_dir}${each.value.bronze_sub_dir}"

  lifecycle {
    prevent_destroy = true
  }
}

resource "azurerm_storage_data_lake_gen2_path" "pdi_data_silver" {
  for_each           = { for entry in local.silver_mapping : "${entry.silver_root_dir}${entry.silver_sub_dir}" => entry }
  filesystem_name    = azurerm_storage_data_lake_gen2_filesystem.pdi_data["silver"].name
  storage_account_id = azurerm_storage_account.pdi_data.id
  resource           = "directory"
  owner              = data.azuread_group.owners.id
  group              = data.azuread_group.owners.id
  path               = "${each.value.silver_root_dir}${each.value.silver_sub_dir}"

  lifecycle {
    prevent_destroy = true
  }
}

resource "azurerm_storage_data_lake_gen2_path" "pdi_data_gold" {
  for_each           = { for entry in local.gold_mapping : "${entry.gold_root_dir}${entry.gold_sub_dir}" => entry }
  filesystem_name    = azurerm_storage_data_lake_gen2_filesystem.pdi_data["gold"].name
  storage_account_id = azurerm_storage_account.pdi_data.id
  resource           = "directory"
  owner              = data.azuread_group.owners.id
  group              = data.azuread_group.owners.id
  path               = "${each.value.gold_root_dir}${each.value.gold_sub_dir}"

  lifecycle {
    prevent_destroy = true
  }
}
