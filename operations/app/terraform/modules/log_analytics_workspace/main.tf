resource "azurerm_log_analytics_workspace" "pdi" {
  name                = "${var.resource_prefix}-law"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_monitor_diagnostic_setting" "diagnostics" {
  for_each                   = local.default
  name                       = "${var.resource_prefix}-${each.value.name}-diag"
  target_resource_id         = each.value.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.pdi.id

  dynamic "log" {
    for_each = each.value.diags.logs
    content {
      category = log.value

      retention_policy {
        enabled = true
        days    = 60
      }
    }
  }

  dynamic "metric" {
    for_each = each.value.diags.metrics
    content {
      category = metric.value

      retention_policy {
        enabled = true
        days    = 60
      }
    }
  }

  lifecycle {
    ignore_changes = [
      log_analytics_destination_type
    ]
  }
}
