##########
## 00-cdc managed resources
##########

module "resource_group" {
  source              = "../../modules/resource_group"
  resource_group_name = var.resource_group_name
}

module "route_table" {
  source              = "../../modules/route_table"
  resource_group_name = var.resource_group_name
  route_table_name    = var.route_table_name
}

##########
## 01-network (including vnets)
##########

module "network" {
  source              = "../../modules/network"
  app_subnet_name     = var.app_subnet_name
  cdc_vnet_name       = var.cdc_vnet_name
  environment         = var.environment
  location            = var.location
  resource_group_name = var.resource_group_name
  resource_prefix     = var.resource_prefix
  service_subnet_name = var.service_subnet_name
  route_table_id      = module.route_table.cdc_managed_route_table_id
}

##########
## 02-storage
##########

module "key_vault" {
  source                      = "../../modules/key_vault"
  environment                 = var.environment
  resource_group_name         = var.resource_group_name
  resource_prefix             = var.resource_prefix
  location                    = var.location
  aad_object_keyvault_admin   = var.aad_object_keyvault_admin
  cdc_app_subnet_id           = module.network.cdc_app_subnet_id
  cdc_subnet_ids              = module.network.cdc_subnet_ids
  cyberark_ip_ingress         = ""
  terraform_caller_ip_address = var.terraform_caller_ip_address
  terraform_object_id         = var.terraform_object_id
  use_cdc_managed_vnet        = var.use_cdc_managed_vnet
}

module "storage" {
  source                      = "../../modules/storage"
  environment                 = var.environment
  location                    = var.location
  resource_group_name         = var.resource_group_name
  resource_prefix             = var.resource_prefix
  application_key_vault_id    = module.key_vault.application_key_vault_id
  cdc_service_subnet_id       = module.network.cdc_service_subnet_id
  cdc_subnet_ids              = module.network.cdc_subnet_ids
  rsa_key_4096                = var.rsa_key_4096
  terraform_caller_ip_address = var.terraform_caller_ip_address
  use_cdc_managed_vnet        = var.use_cdc_managed_vnet
  app_subnet_ids              = module.network.app_subnet_ids
  resource_group_id           = module.resource_group.cdc_managed_resource_group_id
}

##########
## 03-App
##########

module "app_service_plan" {
  source              = "../../modules/app_service_plan"
  environment         = var.environment
  resource_group_name = var.resource_group_name
  resource_prefix     = var.resource_prefix
  location            = var.location
  app_tier            = var.app_tier
  app_size            = var.app_size
}

module "application_insights" {
  source                     = "../../modules/application_insights"
  environment                = var.environment
  resource_group_name        = var.resource_group_name
  resource_prefix            = var.resource_prefix
  location                   = var.location
  service_plan_id            = module.app_service_plan.service_plan_id
  log_analytics_workspace_id = module.log_analytics_workspace.log_analytics_workspace_id
}

module "function_app" {
  source                           = "../../modules/function_app"
  environment                      = var.environment
  resource_group_name              = var.resource_group_name
  resource_prefix                  = var.resource_prefix
  location                         = var.location
  ai_instrumentation_key           = module.application_insights.instrumentation_key
  ai_connection_string             = module.application_insights.connection_string
  app_service_plan                 = module.app_service_plan.service_plan_id
  application_key_vault_id         = module.key_vault.application_key_vault_id
  cdc_app_subnet_id                = module.network.cdc_app_subnet_id
  sa_datastorage_access_key        = module.storage.sa_datastorage_access_key
  sa_datastorage_connection_string = module.storage.sa_datastorage_connection_string
  sa_datastorage_name              = module.storage.sa_datastorage_name
  terraform_caller_ip_address      = var.terraform_caller_ip_address
  use_cdc_managed_vnet             = var.use_cdc_managed_vnet
}

##########
## 04-Monitoring
##########

module "log_analytics_workspace" {
  source                         = "../../modules/log_analytics_workspace"
  resource_group_name            = var.resource_group_name
  location                       = var.location
  function_app_id                = module.function_app.function_app_id
  function_infrastructure_app_id = module.function_app.function_infrastructure_app_id
  app_service_plan_id            = module.app_service_plan.service_plan_id
  cdc_managed_vnet_id            = module.network.cdc_managed_vnet_id
  sa_datastorage_id              = module.storage.sa_datastorage_id
}
