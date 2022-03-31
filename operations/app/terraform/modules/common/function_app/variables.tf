variable "primary" {
  type = object({
    name                       = string
    location                   = string
    resource_group_name        = string
    app_service_plan_id        = string
    storage_account_name       = string
    storage_account_access_key = string
    environment                = string
    subnet_id                  = string
    application_key_vault_id   = string
  })
}

variable "app_settings" {
  type    = map(string)
  default = {}
}
