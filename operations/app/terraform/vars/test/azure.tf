terraform {
  required_version = ">= 1.0.5" # This version must also be changed in other environments

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 2.99.0" # 3.0 contains breaking changes!
    }
  }

  backend "azurerm" {
    resource_group_name  = "prime-ingestion-test"
    storage_account_name = "pitestterraform"
    container_name       = "terraformstate"
    key                  = "prime-ingestion-test.tfstate"
  }
}

provider "azurerm" {
  features {}
  skip_provider_registration = true
  subscription_id            = "7d1e3999-6577-4cd5-b296-f518e5c8e677"
  storage_use_azuread        = true
}