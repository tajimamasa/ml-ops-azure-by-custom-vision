resource "azurerm_storage_account" "storage" {
  name                            = var.storage_account_name
  resource_group_name             = var.resource_group_name
  location                        = var.region_location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  allow_nested_items_to_be_public = false

  tags = {
    environment = "staging"
  }
  lifecycle {
    prevent_destroy = true
  }
}

resource "azurerm_storage_container" "learning-data" {
  name                  = "learning-data"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "model-data" {
  name                  = "model-data"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "image-data" {
  name                  = "image-data"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}

