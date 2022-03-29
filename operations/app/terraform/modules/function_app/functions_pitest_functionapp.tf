# PITest_FunctionApp functions

locals {
  PITest_FunctionApp_function_path = "../../../../../src/FunctionApps/PITest_FunctionApp"
  # Deploy zip and re-add WEBSITE_RUN_FROM_PACKAGE
  PITest_FunctionApp_publish_command = <<EOF
      az functionapp deployment source config-zip --resource-group ${var.resource_group_name} \
      --name ${azurerm_function_app.pdi.name} --src ${data.archive_file.PITest_FunctionApp_function_app.output_path} \
      --build-remote false
      az functionapp config appsettings set --resource-group ${var.resource_group_name} \
      --name ${azurerm_function_app.pdi.name} \
      --settings WEBSITE_RUN_FROM_PACKAGE="1" --query '[].[name]'
    EOF
}

data "archive_file" "PITest_FunctionApp_function_app" {
  type        = "zip"
  source_dir  = local.PITest_FunctionApp_function_path
  output_path = "function-app-PITest_FunctionApp.zip"

  excludes = [
    ".venv",
    ".vscode",
    "local.settings.json",
    "getting_started.md",
    "README.md",
    ".gitignore"
  ]
}

resource "null_resource" "PITest_FunctionApp_function_app_publish" {
  provisioner "local-exec" {
    command = local.PITest_FunctionApp_publish_command
  }
  depends_on = [
    local.PITest_FunctionApp_publish_command,
    azurerm_function_app.pdi
  ]
  triggers = {
    input_json           = filemd5(data.archive_file.PITest_FunctionApp_function_app.output_path)
    publish_code_command = local.PITest_FunctionApp_publish_command
  }
}
