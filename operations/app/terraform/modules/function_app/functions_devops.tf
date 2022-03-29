# Devops functions

locals {
  devops_function_path = "../../../../../src/FunctionApps/DevOps"
  # Deploy zip and re-add WEBSITE_RUN_FROM_PACKAGE
  devops_publish_command = <<EOF
      az functionapp deployment source config-zip --resource-group ${var.resource_group_name} \
      --name ${azurerm_function_app.infrastructure.name} --src ${data.archive_file.devops_function_app.output_path} \
      --build-remote false
      az functionapp config appsettings set --resource-group ${var.resource_group_name} \
      --name ${azurerm_function_app.infrastructure.name} \
      --settings WEBSITE_RUN_FROM_PACKAGE="1" --query '[].[name]'
    EOF
}

data "archive_file" "devops_function_app" {
  type        = "zip"
  source_dir  = local.devops_function_path
  output_path = "function-app-devops.zip"

  excludes = [
    ".venv",
    ".vscode",
    "local.settings.json",
    "getting_started.md",
    "README.md",
    ".gitignore"
  ]
}

resource "null_resource" "devops_function_app_publish" {
  provisioner "local-exec" {
    command = local.devops_publish_command
  }
  depends_on = [
    local.devops_publish_command,
    azurerm_function_app.infrastructure
  ]
  triggers = {
    input_json           = filemd5(data.archive_file.devops_function_app.output_path)
    publish_code_command = local.devops_publish_command
  }
}
