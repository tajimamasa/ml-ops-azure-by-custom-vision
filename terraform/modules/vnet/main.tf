data "azurerm_storage_account" "storage" {
  name                = var.storage_account_name
  resource_group_name = var.resource_group_name
}

data "azurerm_sql_server" "sql_server" {
  name                = var.sql_server_name
  resource_group_name = var.resource_group_name
}

# Virtual Network
resource "azurerm_virtual_network" "vnet" {
  name                = "vnet-${var.product_name}"
  address_space       = ["10.0.0.0/16"]
  location            = data.azurerm_storage_account.storage.location
  resource_group_name = data.azurerm_storage_account.storage.resource_group_name
}

# Subnet for Azure Functions
resource "azurerm_subnet" "functions_subnet" {
  name                 = "functions-subnet-${var.product_name}"
  resource_group_name  = data.azurerm_storage_account.storage.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]

  delegation {
    name = "functiondelegation"
    service_delegation {
      name    = "Microsoft.Web/serverFarms"
      actions = ["Microsoft.Network/virtualNetworks/subnets/action"]
    }
  }
}

# Subnet for Private Endpoints
resource "azurerm_subnet" "private_endpoint_subnet" {
  name                 = "private-endpoint-subnet-${var.product_name}"
  resource_group_name  = data.azurerm_storage_account.storage.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.2.0/24"]

}


# Private Endpoint for Azure SQL Database
resource "azurerm_private_endpoint" "sql_private_endpoint" {
  name                = "sql-private-endpoint-${var.product_name}"
  location            = data.azurerm_storage_account.storage.location
  resource_group_name = data.azurerm_storage_account.storage.resource_group_name
  subnet_id           = azurerm_subnet.private_endpoint_subnet.id

  private_service_connection {
    name                           = "sql-connection"
    private_connection_resource_id = data.azurerm_sql_server.sql_server.id
    is_manual_connection           = false
    subresource_names              = ["sqlServer"]
  }
}

# Private Endpoint for Azure Storage Account
resource "azurerm_private_endpoint" "storage_private_endpoint" {
  name                = "storage-private-endpoint-${var.product_name}"
  location            = data.azurerm_storage_account.storage.location
  resource_group_name = data.azurerm_storage_account.storage.resource_group_name
  subnet_id           = azurerm_subnet.private_endpoint_subnet.id

  private_service_connection {
    name                           = "storage-connection"
    private_connection_resource_id = data.azurerm_storage_account.storage.id
    is_manual_connection           = false
    subresource_names              = ["blob"]
  }
}
