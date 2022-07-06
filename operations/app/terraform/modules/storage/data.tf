# storage account data containers and permissions
# see docs/security/data-access.md for additional notes
locals {
  data_containers = ["bronze", "bronze-additional-records", "fhir-exports", "silver", "gold"]
  data_ace_access = [
    { permissions = "---", id = null, type = "other", scope = "access" },
    { permissions = "---", id = null, type = "other", scope = "default" },
    { permissions = "r-x", id = null, type = "group", scope = "access" },
    { permissions = "r-x", id = null, type = "group", scope = "default" },
    { permissions = "rwx", id = null, type = "user", scope = "access" },
    { permissions = "rwx", id = null, type = "user", scope = "default" },
    { permissions = "rwx", id = null, type = "mask", scope = "access" },
    { permissions = "rwx", id = null, type = "mask", scope = "default" },
    { permissions = "rwx", id = var.adf_uuid, type = "user", scope = "access" },
    { permissions = "rwx", id = var.adf_uuid, type = "user", scope = "default" },
    { permissions = "rwx", id = var.python_function_app_uuid, type = "user", scope = "access" },
    { permissions = "rwx", id = var.python_function_app_uuid, type = "user", scope = "default" }
  ]
}

# storage account data directories
locals {
  bronze_root_dirs = [
    "decrypted",
    "raw"
  ]
  bronze_sub_dirs = [
    "",
    "/eICR",
    "/ELR",
    "/OtherFiles",
    "/VEDSS",
    "/VIIS",
    "/VXU"
  ]
  # Nested loop over both lists, and flatten the result.
  bronze_mapping = distinct(flatten([
    for bronze_root_dir in local.bronze_root_dirs : [
      for bronze_sub_dir in local.bronze_sub_dirs : {
        bronze_sub_dir  = bronze_sub_dir
        bronze_root_dir = bronze_root_dir
      }
    ]
  ]))
  silver_root_dirs = ["temp"]
  silver_sub_dirs = [
    ""
  ]
  # Nested loop over both lists, and flatten the result.
  silver_mapping = distinct(flatten([
    for silver_root_dir in local.silver_root_dirs : [
      for silver_sub_dir in local.silver_sub_dirs : {
        silver_sub_dir  = silver_sub_dir
        silver_root_dir = silver_root_dir
      }
    ]
  ]))
  gold_root_dirs = ["temp"]
  gold_sub_dirs = [
    ""
  ]
  # Nested loop over both lists, and flatten the result.
  gold_mapping = distinct(flatten([
    for gold_root_dir in local.gold_root_dirs : [
      for gold_sub_dir in local.gold_sub_dirs : {
        gold_sub_dir  = gold_sub_dir
        gold_root_dir = gold_root_dir
      }
    ]
  ]))
}
