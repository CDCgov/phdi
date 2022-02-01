# Migrating reportstream terraform

Modules deleted:

This includes deleting the modules themselves as well as the references from
`vars/test/*`:

* `container_registry`
* `database`
* `front_door`
* `metabase`
* `sftp_container`

Capabilities deleted:

* `application_insights`
    * Removed all alerts and PagerDuty reference
* `storage`
    * Removed references to web container and public site
    * Removed references to partner account
    * Removed references to candidate slot
    * Removed 30 day retention limit

# Process

1. Make all the above changes
2. Run `terraform init` in `app/terraform/vars/test`.
    * Define the necessary variables for the [`azurerm`
      backend](https://www.terraform.io/language/settings/backends/azurerm) --
      storage account, container name, key. Keep at it until you see a success
      message like:
```
Initializing modules...

Initializing the backend...

Successfully configured the backend "azurerm"! Terraform will automatically
use this backend unless the backend configuration changes.

Initializing provider plugins...
- Finding hashicorp/azurerm versions matching ">= 2.61.0"...
- Installing hashicorp/azurerm v2.90.0...
- Installed hashicorp/azurerm v2.90.0 (signed by HashiCorp)

Terraform has created a lock file .terraform.lock.hcl to record the provider
selections it made above. Include this file in your version control repository
so that Terraform can guarantee to make the same selections by default when
you run "terraform init" in the future.

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.
```
3. Create the key vault if necessary. If we're storing any secrets for the
   database, integration keys (like PagerDuty), or others they'll be in
   `vars/{environment}/secrets.tf`. If any secrets are there you'll need to
   create the key vault (using the name in `variables.tf @ tf_secrets_vault`),
   pre-populate the secrets with the names match up with the ones in
   `secrets.tf`.
4. Comment out everything in `vars/test/main.tf` after `"nat_gateway"`.
5. Run `terraform plan` to see what will happen.


## Questions

* `modules/vnet/main.tf` - Removed the `dns_servers` entry and the VNet now has
  'Default (Azure-provided)' right now, which is probably fine (?)

