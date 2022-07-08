terraform {
  required_version = ">= 1.0.5" # This version must also be changed in other environments

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 2.99.0" # 3.0 contains breaking changes!
    }
  }

  backend "azurerm" {
    resource_group_name  = "prime-ingestion-skylight"
    storage_account_name = "piskylightterraform"
    container_name       = "terraformstate"
    key                  = "prime-ingestion-skylight.tfstate"
  }
}

provider "azurerm" {
  features {}
  skip_provider_registration = true
  subscription_id            = "6848426c-8ca8-4832-b493-fed851be1f95"
  storage_use_azuread        = true
}
