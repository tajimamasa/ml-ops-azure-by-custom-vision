
data "azurerm_storage_account" "storage" {
  name                = var.storage_account_name
  resource_group_name = var.resource_group_name
}

resource "azurerm_app_service_plan" "asp" {
  name                = var.app_service_plan_name
  location            = data.azurerm_storage_account.storage.location
  resource_group_name = data.azurerm_storage_account.storage.resource_group_name

  sku {
    tier = "Standard"
    size = "S1"
  }
}

resource "azurerm_function_app" "function" {
  name                       = var.function_app_name
  location                   = data.azurerm_storage_account.storage.location
  resource_group_name        = data.azurerm_storage_account.storage.resource_group_name
  storage_account_name       = data.azurerm_storage_account.storage.name
  storage_account_access_key = data.azurerm_storage_account.storage.primary_access_key
  app_service_plan_id        = azurerm_app_service_plan.asp.id
  os_type                    = "linux"


  app_settings = {
    "FUNCTIONS_WORKER_RUNTIME" = "python"
    "AzureWebJobsStorage"      = data.azurerm_storage_account.storage.primary_connection_string
    "WEBSITE_RUN_FROM_PACKAGE" = "1"
  }
}
