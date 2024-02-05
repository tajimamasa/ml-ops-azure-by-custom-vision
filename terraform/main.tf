terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
}

provider "azurerm" {
  features {}

  tenant_id       = var.tenant_id
  subscription_id = var.subscription_id
  client_id       = var.client_id
  client_secret   = var.client_secret
}

resource "azurerm_resource_group" "rg" {
  name     = "${var.product_name}-rg"
  location = var.region_location
}

module "storage" {
  source               = "./modules/storage"
  storage_account_name = "${replace(var.product_name, "-", "")}storage"
  resource_group_name  = azurerm_resource_group.rg.name
  region_location      = azurerm_resource_group.rg.location

  depends_on = [azurerm_resource_group.rg]
}

module "sql_server" {
  source                       = "./modules/sql-server"
  server_name                  = "${var.product_name}-sql"
  database_name                = "${var.product_name}-db"
  resource_group_name          = azurerm_resource_group.rg.name
  resource_region              = azurerm_resource_group.rg.location
  administrator_login          = var.sql_admin
  administrator_login_password = var.sql_admin_password

  depends_on = [azurerm_resource_group.rg]
}

module "functions" {
  source                = "./modules/functions"
  app_service_plan_name = "${var.product_name}-asp"
  function_app_name     = "${var.product_name}-functions"
  storage_account_name  = "${replace(var.product_name, "-", "")}storage"
  resource_group_name   = azurerm_resource_group.rg.name

  depends_on = [module.storage]
}

module "vnet" {
  source               = "./modules/vnet"
  product_name         = var.product_name
  resource_group_name  = azurerm_resource_group.rg.name
  storage_account_name = "${replace(var.product_name, "-", "")}storage"
  sql_server_name      = "${var.product_name}-sql"

  depends_on = [module.storage, module.sql_server]
}
