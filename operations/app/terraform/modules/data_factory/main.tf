resource "azurerm_data_factory" "pdi" {
  name                            = "${var.resource_prefix}-df"
  location                        = var.location
  resource_group_name             = var.resource_group_name
  public_network_enabled          = false
  managed_virtual_network_enabled = true

  identity {
    type = "SystemAssigned"
  }

  lifecycle {
    ignore_changes = [
      tags
    ]
  }

  tags = {
    environment = var.environment
    managed-by  = "terraform"
  }
}

resource "azurerm_data_factory_integration_runtime_azure" "pdi" {
  name                    = "${var.resource_prefix}-ir"
  data_factory_id         = azurerm_data_factory.pdi.id
  resource_group_name     = var.resource_group_name
  location                = var.location
  virtual_network_enabled = true
  time_to_live_min        = 10
}

resource "azurerm_data_factory_managed_private_endpoint" "pdi_appkv" {
  name               = replace("${var.resource_prefix}-app-kv-privateendpoint", "-", "_")
  data_factory_id    = azurerm_data_factory.pdi.id
  target_resource_id = var.application_key_vault_id
  subresource_name   = "vault"

  lifecycle {
    ignore_changes = [
      fqdns
    ]
  }

  timeouts {}
}

resource "azurerm_data_factory_managed_private_endpoint" "pdi_datasa" {
  name               = replace("${var.resource_prefix}datasa-privateendpoint", "-", "_")
  data_factory_id    = azurerm_data_factory.pdi.id
  target_resource_id = var.sa_data_id
  subresource_name   = "blob"

  lifecycle {
    ignore_changes = [
      fqdns
    ]
  }

  timeouts {}
}

resource "azurerm_data_factory_linked_service_key_vault" "pdi_appkv" {
  name                = "${var.resource_prefix}_app_kv"
  resource_group_name = var.resource_group_name
  data_factory_id     = azurerm_data_factory.pdi.id
  key_vault_id        = var.application_key_vault_id
}

resource "azurerm_data_factory_linked_service_azure_blob_storage" "pdi_datasa" {
  name                     = "${var.resource_prefix}datastorage"
  resource_group_name      = var.resource_group_name
  data_factory_id          = azurerm_data_factory.pdi.id
  integration_runtime_name = azurerm_data_factory_integration_runtime_azure.pdi.name

  sas_uri = "https://${var.resource_prefix}datasa.blob.core.windows.net"
  key_vault_sas_token {
    linked_service_name = azurerm_data_factory_linked_service_key_vault.pdi_appkv.name
    secret_name         = var.adf_sa_sas_name
  }

  depends_on = [var.adf_sa_sas_id]
}

resource "azurerm_data_factory_linked_service_sftp" "vdh" {
  name                     = "vdhsftp"
  resource_group_name      = var.resource_group_name
  data_factory_id          = azurerm_data_factory.pdi.id
  authentication_type      = "Basic"
  host                     = "vdhsftp.vdh.virginia.gov"
  port                     = 22
  username                 = "USDS_CDC"
  password                 = var.vdhsftp_pass
  skip_host_key_validation = true
  integration_runtime_name = azurerm_data_factory_integration_runtime_azure.pdi.name
}

resource "azurerm_data_factory_dataset_binary" "pdi_datasa" {
  name                = "SFTPBinarySink"
  resource_group_name = var.resource_group_name
  data_factory_id     = azurerm_data_factory.pdi.id
  linked_service_name = azurerm_data_factory_linked_service_azure_blob_storage.pdi_datasa.name

  azure_blob_storage_location {
    container                = "bronze"
    dynamic_filename_enabled = false
    dynamic_path_enabled     = false
    path                     = "raw"
  }

  compression {
    level = "Fastest"
    type  = "ZipDeflate"
  }

  depends_on = [
    azurerm_data_factory_linked_service_azure_blob_storage.pdi_datasa
  ]
}

resource "azurerm_data_factory_dataset_binary" "pdi_datasa_mzn" {
  name                = "DestinationDataset_mzn"
  resource_group_name = var.resource_group_name
  data_factory_id     = azurerm_data_factory.pdi.id
  linked_service_name = azurerm_data_factory_linked_service_azure_blob_storage.pdi_datasa.name

  azure_blob_storage_location {
    container                = "bronze"
    dynamic_filename_enabled = false
    dynamic_path_enabled     = false
  }

  depends_on = [
    azurerm_data_factory_linked_service_azure_blob_storage.pdi_datasa
  ]
}

resource "azurerm_data_factory_dataset_binary" "vdh" {
  name                = "SFTPBinarySource"
  resource_group_name = var.resource_group_name
  data_factory_id     = azurerm_data_factory.pdi.id
  linked_service_name = azurerm_data_factory_linked_service_sftp.vdh.name

  sftp_server_location {
    path     = "/test_dir"
    filename = "*"
  }
}

resource "azurerm_data_factory_pipeline" "transfer_files" {
  name                = "transfer-files"
  resource_group_name = var.resource_group_name
  data_factory_id     = azurerm_data_factory.pdi.id
  annotations         = []
  concurrency         = 1
  parameters          = {}
  variables           = {}

  depends_on = [
    azurerm_data_factory_dataset_binary.vdh,
    azurerm_data_factory_linked_service_azure_blob_storage.pdi_datasa
  ]

  activities_json = jsonencode(
    [
      {
        dependsOn = []
        inputs = [
          {
            parameters    = {}
            referenceName = "SFTPBinarySource"
            type          = "DatasetReference"
          },
        ]
        name = "SFTP to Blob"
        outputs = [
          {
            parameters    = {}
            referenceName = "SFTPBinarySink"
            type          = "DatasetReference"
          },
        ]
        policy = {
          retry                  = 0
          retryIntervalInSeconds = 30
          secureInput            = false
          secureOutput           = false
          timeout                = "7.00:00:00"
        }
        type = "Copy"
        typeProperties = {
          enableStaging = false
          sink = {
            storeSettings = {
              type = "AzureBlobStorageWriteSettings"
            }
            type = "BinarySink"
          }
          source = {
            formatSettings = {
              compressionProperties = null
              type                  = "BinaryReadSettings"
            }
            storeSettings = {
              deleteFilesAfterCompletion = false
              maxConcurrentConnections   = 1
              wildcardFileName           = "*"
              wildcardFolderPath         = "OtherFiles"
              disableChunking            = false
              recursive                  = true
              type                       = "SftpReadSettings"
            }
            type = "BinarySource"
          }
        }
        userProperties = [
          {
            name  = "Source"
            value = "/OtherFiles/"
          },
          {
            name  = "Destination"
            value = "bronze/raw/VIIS"
          },
        ]
      },
    ]
  )
}
