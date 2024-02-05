variable "subscription_id" {
  type = string
}

variable "tenant_id" {
  type = string
}

variable "client_id" {
  type = string
}

variable "client_secret" {
  type = string
}

variable "product_name" {
  type = string
}

variable "region_location" {
  type = string
}

variable "sql_admin" {
  type    = string
  default = "sqladmin"
}

variable "sql_admin_password" {
  type = string
}
