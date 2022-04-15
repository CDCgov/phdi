# java functions
# publish:
# requires build in the correct workspace 
# terraform apply -replace=module.function_app.null_resource.java_function_app_publish[0]

locals {
  java_function_path = "../../../../../src/FunctionApps/TestJava"
}

locals {
  java_publish_command = <<EOF
      mvn clean package -Denv=${var.environment} -f ${local.java_function_path}/pom.xml
      mvn azure-functions:deploy -Denv=${var.environment} -f ${local.java_function_path}/pom.xml
    EOF
}

resource "null_resource" "java_function_app_publish" {
  count = var.publish_functions ? 1 : 0
  provisioner "local-exec" {
    command = local.java_publish_command
  }
  depends_on = [
    local.java_publish_command,
    module.pdi_function_app["java"].submodule_function_app
  ]
  triggers = {
    publish_code_command = local.java_publish_command
  }
}
