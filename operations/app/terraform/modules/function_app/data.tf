locals {
  function_apps = {
    default : {
      runtime                             = "python",
      version                             = "~4",
      mi_blobServiceName                  = "",
      mi_blobServiceUri                   = null,
      mi_queueServiceName                 = "",
      mi_queueServiceUri                  = null,
      mi_accountName                      = "",
      mi_accountValue                     = null,
      SCM_DO_BUILD_DURING_DEPLOYMENT      = true,
      ENABLE_ORYX_BUILD                   = null,
      fhir_url                            = null,
      AzureWebJobs_convertToFhir_Disabled = 0,
      always_on                           = false,
      WEBSITE_RUN_FROM_PACKAGE            = null
    },
    python : {
      runtime                             = "python",
      version                             = "~4",
      mi_blobServiceName                  = "",
      mi_blobServiceUri                   = null,
      mi_queueServiceName                 = "",
      mi_queueServiceUri                  = null,
      mi_accountName                      = "",
      mi_accountValue                     = null,
      SCM_DO_BUILD_DURING_DEPLOYMENT      = true,
      ENABLE_ORYX_BUILD                   = true,
      fhir_url                            = null,
      AzureWebJobs_convertToFhir_Disabled = 0,
      always_on                           = true,
      WEBSITE_RUN_FROM_PACKAGE            = null
    },
    infra : {
      runtime                             = "python",
      version                             = "~4",
      mi_blobServiceName                  = "",
      mi_blobServiceUri                   = null,
      mi_queueServiceName                 = "",
      mi_queueServiceUri                  = null,
      mi_accountName                      = "",
      mi_accountValue                     = null,
      SCM_DO_BUILD_DURING_DEPLOYMENT      = true,
      ENABLE_ORYX_BUILD                   = null,
      fhir_url                            = null,
      AzureWebJobs_convertToFhir_Disabled = 0,
      always_on                           = false,
      WEBSITE_RUN_FROM_PACKAGE            = null
    },
  }
}
