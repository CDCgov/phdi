resource "azurerm_data_factory_dataset_binary" "pdi_datasa" {
  name                = "SFTPBinarySink"
  resource_group_name = var.resource_group_name
  data_factory_id     = azurerm_data_factory.pdi.id
  linked_service_name = azurerm_data_factory_linked_service_azure_blob_storage.pdi_datasa.name

  azure_blob_storage_location {
    container                = "bronze/additional-records"
    dynamic_filename_enabled = true
    dynamic_path_enabled     = true
    path                     = "@dataset().base_path"
    filename                 = "@dataset().file_name"
  }

  parameters = {
    base_path = "/",
    file_name = ""
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
    dynamic_filename_enabled = true
    dynamic_path_enabled     = true
    path                     = "@dataset().base_path"
    filename                 = "@dataset().file_name"
  }

  parameters = {
    base_path = "/",
    file_name = ""
  }
}
