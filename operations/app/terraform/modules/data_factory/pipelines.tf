resource "azurerm_data_factory_pipeline" "transfer_files" {
  name                = "transfer-files"
  resource_group_name = var.resource_group_name
  data_factory_id     = azurerm_data_factory.pdi.id
  annotations         = []
  concurrency         = 1
  parameters          = {}

  depends_on = [
    azurerm_data_factory_dataset_binary.vdh,
    azurerm_data_factory_linked_service_azure_blob_storage.pdi_datasa
  ]

  variables = {
    "sink_base_path"   = "VIIS"
    "source_base_path" = "/"
  }

  activities_json = jsonencode(
    [
      {
        dependsOn = [
          {
            activity = "Set Source Base Path"
            dependencyConditions = [
              "Succeeded",
            ]
          },
          {
            activity = "Set Sink Base Path"
            dependencyConditions = [
              "Succeeded",
            ]
          },
        ]
        name = "Get Metadata1"
        policy = {
          retry                  = 0
          retryIntervalInSeconds = 30
          secureInput            = false
          secureOutput           = false
          timeout                = "7.00:00:00"
        }
        type = "GetMetadata"
        typeProperties = {
          dataset = {
            parameters = {
              base_path = {
                type  = "Expression"
                value = "@variables('source_base_path')"
              }
              file_name = "*"
            }
            referenceName = "SFTPBinarySource"
            type          = "DatasetReference"
          }
          fieldList = [
            "childItems",
          ]
          formatSettings = {
            compressionProperties = null
            type                  = "BinaryReadSettings"
          }
          storeSettings = {
            disableChunking          = false
            enablePartitionDiscovery = false
            recursive                = true
            type                     = "SftpReadSettings"
          }
        }
        userProperties = []
      },
      {
        dependsOn = [
          {
            activity = "Get Metadata1"
            dependencyConditions = [
              "Succeeded",
            ]
          },
        ]
        name = "For All Files in SFTP Server"
        type = "ForEach"
        typeProperties = {
          activities = [
            {
              dependsOn = []
              name      = "Check Existence of Raw Data in sink"
              policy = {
                retry                  = 0
                retryIntervalInSeconds = 30
                secureInput            = false
                secureOutput           = false
                timeout                = "7.00:00:00"
              }
              type = "GetMetadata"
              typeProperties = {
                dataset = {
                  parameters = {
                    base_path = "raw/@{variables('sink_base_path')}"
                    file_name = "@item().name"
                  }
                  referenceName = "SFTPBinarySink"
                  type          = "DatasetReference"
                }
                fieldList = [
                  "exists",
                ]
                formatSettings = {
                  compressionProperties = null
                  type                  = "BinaryReadSettings"
                }
                storeSettings = {
                  enablePartitionDiscovery = false
                  type                     = "AzureBlobStorageReadSettings"
                }
              }
              userProperties = []
            },
            {
              dependsOn = [
                {
                  activity = "Check Existence of Raw Data in sink"
                  dependencyConditions = [
                    "Succeeded",
                  ]
                },
              ]
              name = "If Raw Data Exists"
              type = "IfCondition"
              typeProperties = {
                expression = {
                  type  = "Expression"
                  value = "@activity('Check Existence of Raw Data in sink').output.exists"
                }
                ifFalseActivities = [
                  {
                    dependsOn = []
                    inputs = [
                      {
                        parameters = {
                          base_path = {
                            type  = "Expression"
                            value = "@variables('source_base_path')"
                          }
                          file_name = {
                            type  = "Expression"
                            value = "@item().name"
                          }
                        }
                        referenceName = "SFTPBinarySource"
                        type          = "DatasetReference"
                      },
                    ]
                    name = "Copy Raw Data"
                    outputs = [
                      {
                        parameters = {
                          base_path = {
                            type  = "Expression"
                            value = "raw/@{variables('sink_base_path')}"
                          }
                          file_name = "@item().name"
                        }
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
                          disableChunking = false
                          recursive       = true
                          type            = "SftpReadSettings"
                        }
                        type = "BinarySource"
                      }
                    }
                    userProperties = [
                      {
                        name  = "Source"
                        value = "@{variables('source_base_path')}/@{item().name}"
                      },
                      {
                        name  = "Destination"
                        value = "bronze/@{concat('raw/', variables('sink_base_path'))}/@{item().name}"
                      },
                    ]
                  },
                ]
              }
              userProperties = []
            },
            {
              dependsOn = [
                {
                  activity = "If Raw Data Exists"
                  dependencyConditions = [
                    "Succeeded",
                  ]
                },
              ]
              name = "Check existence of Decrypted Data in sink"
              policy = {
                retry                  = 0
                retryIntervalInSeconds = 30
                secureInput            = false
                secureOutput           = false
                timeout                = "7.00:00:00"
              }
              type = "GetMetadata"
              typeProperties = {
                dataset = {
                  parameters = {
                    base_path = "decrypted/@{variables('sink_base_path')}"
                    file_name = {
                      type  = "Expression"
                      value = "@item().name"
                    }
                  }
                  referenceName = "SFTPBinarySink"
                  type          = "DatasetReference"
                }
                fieldList = [
                  "exists",
                ]
                formatSettings = {
                  compressionProperties = null
                  type                  = "BinaryReadSettings"
                }
                storeSettings = {
                  enablePartitionDiscovery = false
                  type                     = "AzureBlobStorageReadSettings"
                }
              }
              userProperties = []
            },
            {
              dependsOn = [
                {
                  activity = "Check existence of Decrypted Data in sink"
                  dependencyConditions = [
                    "Succeeded",
                  ]
                },
              ]
              name = "If Decrypted Data exists"
              type = "IfCondition"
              typeProperties = {
                expression = {
                  type  = "Expression"
                  value = "@activity('Check existence of Decrypted Data in sink').output.exists"
                }
                ifFalseActivities = [
                  {
                    dependsOn = []
                    linkedServiceName = {
                      referenceName = "AzureFunction1"
                      type          = "LinkedServiceReference"
                    }
                    name = "Decrypt Data"
                    policy = {
                      retry                  = 0
                      retryIntervalInSeconds = 30
                      secureInput            = false
                      secureOutput           = false
                      timeout                = "7.00:00:00"
                    }
                    type = "AzureFunctionActivity"
                    typeProperties = {
                      body = {
                        type = "Expression"
                        value = jsonencode(
                          {
                            input  = "raw/@{variables('sink_base_path')}/@{item().name}"
                            output = "decrypted/@{variables('sink_base_path')}"
                          }
                        )
                      }
                      functionName = "DecryptFunction"
                      headers      = {}
                      method       = "POST"
                    }
                    userProperties = []
                  },
                ]
              }
              userProperties = []
            },
          ]
          items = {
            type  = "Expression"
            value = "@activity('Get Metadata1').output.childItems"
          }
        }
        userProperties = []
      },
      {
        dependsOn = []
        name      = "Set Source Base Path"
        type      = "SetVariable"
        typeProperties = {
          value        = "OtherFiles"
          variableName = "source_base_path"
        }
        userProperties = []
      },
      {
        dependsOn = []
        name      = "Set Sink Base Path"
        type      = "SetVariable"
        typeProperties = {
          value        = "VIIS"
          variableName = "sink_base_path"
        }
        userProperties = []
      },
    ]
  )
}
