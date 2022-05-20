locals {
  # Tie to existing project variables
  interface = {
    function_app_name          = "${var.resource_prefix}-ingestion-admin"
    resource_group_name        = var.resource_group_name
    location                   = var.location
    app_service_plan_id        = var.app_service_plan
    storage_account_name       = var.sa_functionapps.name
    storage_account_access_key = var.sa_functionapps.primary_access_key

    # Path to functions parent directory
    # How to create functions:
    # VS Code Azure Functions extension > Create new project
    functions_path = "../../../../../src/FunctionApps/DevOps"
  }
  # Set all "Application Settings"
  # Add/remove to adjust dynamically
  app_settings = {
    WEBSITE_DNS_SERVER                 = "168.63.129.16"
    FUNCTIONS_WORKER_RUNTIME           = "python"
    WEBSITE_VNET_ROUTE_ALL             = 1
    WEBSITE_CONTENTOVERVNET            = 1
    SCM_DO_BUILD_DURING_DEPLOYMENT     = true
    WEBSITE_HTTPLOGGING_RETENTION_DAYS = 3
  }
  # Set app configuration
  config = {
    use_32_bit_worker_process = false
    vnet_route_all_enabled    = true
    # Deployments may fail if not always on
    always_on                = true
    environment              = var.environment
    linux_fx_version         = "PYTHON|3.9"
    FUNCTIONS_WORKER_RUNTIME = "python"
  }
  # Set network configuration
  network = {
    subnet_id = var.cdc_app_subnet_id
  }
  # Set ip restrictions within site_config
  ip_restrictions = []
}

########################################
#
#         DO NOT EDIT BELOW!
#
########################################

resource "azurerm_function_app" "admin" {
  name                       = local.interface.function_app_name
  location                   = local.interface.location
  resource_group_name        = local.interface.resource_group_name
  app_service_plan_id        = local.interface.app_service_plan_id
  storage_account_name       = local.interface.storage_account_name
  storage_account_access_key = local.interface.storage_account_access_key
  https_only                 = true
  os_type                    = "linux"
  version                    = "~4"
  enable_builtin_logging     = false
  site_config {
    ftps_state                = "Disabled"
    linux_fx_version          = local.config.linux_fx_version
    use_32_bit_worker_process = local.config.use_32_bit_worker_process
    vnet_route_all_enabled    = local.config.vnet_route_all_enabled
    always_on                 = local.config.always_on
    dynamic "ip_restriction" {
      for_each = local.ip_restrictions
      content {
        action                    = ip_restriction.value.action
        name                      = ip_restriction.value.name
        priority                  = ip_restriction.value.priority
        virtual_network_subnet_id = ip_restriction.value.virtual_network_subnet_id
        service_tag               = ip_restriction.value.service_tag
        ip_address                = ip_restriction.value.ip_address
      }
    }
  }
  app_settings = local.app_settings
  identity {
    type = "SystemAssigned"
  }
  lifecycle {
    ignore_changes = [
      tags,
      site_config[0].ip_restriction
    ]
  }
  tags = {
    environment = local.config.environment
    managed-by  = "terraform"
  }
}

resource "time_sleep" "wait_admin_function_app" {
  create_duration = "2m"

  depends_on = [azurerm_function_app.admin]
  triggers = {
    function_app = azurerm_function_app.admin.identity.0.principal_id
  }
}

resource "azurerm_app_service_virtual_network_swift_connection" "admin_function_app_vnet_integration" {
  app_service_id = azurerm_function_app.admin.id
  subnet_id      = local.network.subnet_id
}

locals {
  admin_publish_command = <<EOF
      az functionapp deployment source config-zip --resource-group ${local.interface.resource_group_name} \
      --name ${azurerm_function_app.admin.name} --src ${data.archive_file.admin_function_app.output_path} \
      --build-remote false --timeout 600
    EOF
}

data "archive_file" "admin_function_app" {
  type        = "zip"
  source_dir  = local.interface.functions_path
  output_path = "function-app-admin.zip"

  excludes = [
    ".venv",
    ".vscode",
    "local.settings.json",
    "getting_started.md",
    "README.md",
    ".gitignore"
  ]
}

resource "null_resource" "admin_function_app_publish" {
  provisioner "local-exec" {
    command = local.admin_publish_command
  }
  depends_on = [
    local.admin_publish_command,
    azurerm_function_app.admin,
    time_sleep.wait_admin_function_app
  ]
  triggers = {
    input_json           = filemd5(data.archive_file.admin_function_app.output_path)
    publish_code_command = local.admin_publish_command
  }
}
