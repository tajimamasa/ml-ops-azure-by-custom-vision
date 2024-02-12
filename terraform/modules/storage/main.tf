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

// 初期のモデル
resource "azurerm_storage_blob" "model-data" {
  count                  = length(var.model-data)
  name                   = var.model-data[count.index]
  storage_account_name   = azurerm_storage_account.storage.name
  storage_container_name = azurerm_storage_container.model-data.name
  type                   = "Block"
  source                 = "${var.model-source-directory}${var.model-data[count.index]}"
}

// ノイズ付加前の画像
resource "azurerm_storage_blob" "image-data" {
  count                  = length(var.image-data)
  name                   = "ideal/${var.image-data[count.index]}"
  storage_account_name   = azurerm_storage_account.storage.name
  storage_container_name = azurerm_storage_container.learning-data.name
  type                   = "Block"
  source                 = "${var.image-source-directory}${var.image-data[count.index]}"
}
