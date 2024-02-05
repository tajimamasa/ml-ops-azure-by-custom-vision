variable "server_name" {
  type = string
}

variable "database_name" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "resource_region" {
  type = string
}

variable "administrator_login" {
  type    = string
  default = "sqladmin"
}

variable "administrator_login_password" {
  type = string
}
