# TODO: not currently used
variable "tf_secrets_vault" {
  default = "pidev-tf-secrets"
}

## Set basic variables
variable "terraform_object_id" {
  type        = string
  description = "Object id of user running TF"
  # NOTE: set to object ID of CT-DMZ-PRIME-INGESTION-TST-AZ-Contributor
  default = "9ff42a69-beb8-4b4a-9406-e7fbcbf847ee"
}

variable "app_subnet_name" {
  default = "app"
}

variable "cdc_vnet_name" {
  default = "prime-ingestion-dev-VNET"
}

variable "environment" {
  default = "dev"
}

variable "https_cert_names" {
  default = []
}

variable "location" {
  default = "eastus"
}

variable "resource_group_name" {
  default = "prime-ingestion-dev"
}

variable "resource_prefix" {
  default = "pidev"
}

variable "rsa_key_2048" {
  default = null
}

variable "rsa_key_4096" {
  default = null
}

variable "service_subnet_name" {
  default = "service"
}

variable "route_table_name" {
  default = "prime-ingestion-test-RT"
}

variable "route_table_resource_group_name" {
  default = "prime-ingestion-test"
}

variable "publish_functions" {
  type    = bool
  default = true
}

variable "aad_object_keyvault_admin" {
  # NOTE: set to object ID of CT-DMZ-PRIME-INGESTION-TST-AZ-Contributor
  default = "9ff42a69-beb8-4b4a-9406-e7fbcbf847ee"
} # Group or individual user id

variable "service_subnet_ip" {
  default = "172.17.9.128/28"
}

variable "app_subnet_ip" {
  default = "172.17.9.144/28"
}

/* Variables to generate multiple dns records for private endpoint via for_each */
variable "dns_vars" {
  default = {
    "blob" = {
      type   = "blob"
      record = "172.17.9.134"
      guid   = "81980b71-8fc6-4e39-a291-1b42d5f4fe3b"
    },
    "file" = {
      type   = "file"
      record = "172.17.9.132"
      guid   = "e68a9884-1f0d-497b-b52c-90bffc665851"
    },
    "queue" = {
      type   = "queue"
      record = "172.17.9.133"
      guid   = "68f761fe-1e84-4f55-82dc-39e7e50b54cc"
    }
  }
}

##################
## App Service Plan Vars
##################

variable "app_tier" {
  default = "PremiumV3"
}

variable "app_size" {
  default = "P1v3"
}

##################
## KeyVault Vars
##################

variable "use_cdc_managed_vnet" {
  default = true
}

variable "terraform_caller_ip_address" {
  type    = list(string)
  default = ["162.224.209.174/32", "73.173.186.141/32", "24.163.118.70/32"]
}

variable "data_access_group" {
  type    = string
  default = "CT-PRIMEIngestion-AZ-Owners"
}

variable "data_access_sp" {
  type    = string
  default = "pitest-service-principal"
}
