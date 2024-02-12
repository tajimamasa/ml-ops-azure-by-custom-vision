
variable "storage_account_name" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "region_location" {
  type = string
}

variable "model-source-directory" {
  default = "../data/"
}

variable "model-data" {
  type = list(string)
  default = [
    "camera000/model.onnx",
    "camera001/model.onnx",
    "camera002/model.onnx",
  ]
}

variable "image-source-directory" {
  default = "../image/"
}

variable "image-data" {
  type = list(string)
  default = [
    "tag.json",
    "img_000.png",
    "img_001.png",
    "img_002.png",
    "img_003.png",
    "img_004.png",
    "img_005.png",
    "img_006.png",
    "img_007.png",
    "img_008.png",
    "img_009.png",
    "img_010.png",
    "img_011.png",
    "img_012.png",
    "img_013.png",
    "img_014.png",
  ]
}
