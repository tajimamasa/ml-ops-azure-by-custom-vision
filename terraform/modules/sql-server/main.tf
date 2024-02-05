# Azure SQL Database
resource "azurerm_sql_server" "sql_server" {
  name                         = var.server_name
  resource_group_name          = var.resource_group_name
  location                     = var.resource_region
  version                      = "12.0"
  administrator_login          = var.administrator_login
  administrator_login_password = var.administrator_login_password

  lifecycle {
    prevent_destroy = true
  }
}

resource "azurerm_sql_database" "sql_database" {
  name                = var.database_name
  resource_group_name = var.resource_group_name
  location            = var.resource_region
  server_name         = azurerm_sql_server.sql_server.name
  edition             = "Basic"
}
