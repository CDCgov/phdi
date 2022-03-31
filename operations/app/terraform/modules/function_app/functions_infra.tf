# infra functions

locals {
  infra_function_path = "../../../../../src/FunctionApps/DevOps"
  # Deploy zip and re-add WEBSITE_RUN_FROM_PACKAGE
  infra_publish_command = <<EOF
      az functionapp deployment source config-zip --resource-group ${var.resource_group_name} \
      --name ${module.pdi_function_app["infra"].submodule_function_app.name} --src ${data.archive_file.infra_function_app.output_path} \
      --build-remote false
      az functionapp config appsettings set --resource-group ${var.resource_group_name} \
      --name ${module.pdi_function_app["infra"].submodule_function_app.name} \
      --settings WEBSITE_RUN_FROM_PACKAGE="1" --query '[].[name]'
    EOF
}

data "archive_file" "infra_function_app" {
  type        = "zip"
  source_dir  = local.infra_function_path
  output_path = "function-app-infra.zip"

  excludes = [
    ".venv",
    ".vscode",
    "local.settings.json",
    "getting_started.md",
    "README.md",
    ".gitignore"
  ]
}

resource "null_resource" "infra_function_app_publish" {
  provisioner "local-exec" {
    command = local.infra_publish_command
  }
  depends_on = [
    local.infra_publish_command,
    module.pdi_function_app["infra"].submodule_function_app
  ]
  triggers = {
    input_json           = filemd5(data.archive_file.infra_function_app.output_path)
    publish_code_command = local.infra_publish_command
  }
}
