output "infrastructure_function_app_id" {
  value = module.pdi_function_app["infra"].submodule_function_app.id
}

output "infrastructure_function_app_uuid" {
  value = module.pdi_function_app["infra"].submodule_function_app.identity[0].principal_id
}

output "python_function_app_id" {
  value = module.pdi_function_app["python"].submodule_function_app.id
}

output "python_function_app_uuid" {
  value = module.pdi_function_app["python"].submodule_function_app.identity[0].principal_id
}
