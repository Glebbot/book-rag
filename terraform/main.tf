terraform {
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
    }
  }
  backend "s3" {
    endpoints = {
      s3 = "https://storage.yandexcloud.net"
    }
    bucket = "terraform-devops"
    region = "ru-central1"
    key    = "terraform/terraform.tfstate"
    skip_region_validation      = true
    skip_credentials_validation = true
    skip_requesting_account_id  = true
    skip_s3_checksum            = true

  }
}

variable "yc_cloud_id" {}
variable "yc_folder_id" {}
variable "ssh_key_pub" {}

provider "yandex" {
  cloud_id  = var.yc_cloud_id
  folder_id = var.yc_folder_id
  zone      = "ru-central1-a"
}

resource "yandex_vpc_network" "default" {
  name = "book-rag-network"
}

resource "yandex_vpc_subnet" "default" {
  name           = "book-rag-subnet"
  zone           = "ru-central1-a"
  network_id     = yandex_vpc_network.default.id
  v4_cidr_blocks = ["10.0.1.0/24"]
}

resource "yandex_vpc_security_group" "ssh_allow" {
  name        = "allow-ssh-sg"
  network_id  = yandex_vpc_network.default.id

  ingress {
    protocol       = "ANY"
    port           = 22
    v4_cidr_blocks    = ["0.0.0.0/0"]
  }

  egress {
    protocol       = "ANY"
    v4_cidr_blocks    = ["0.0.0.0/0"]
  }
}

data "yandex_compute_image" "ubuntu" {
  family = "ubuntu-2204-lts"
}

resource "yandex_compute_instance" "vm" {
  name        = "book-rag"
  platform_id = "standard-v3"

  resources {
    cores  = 4
    memory = 4
  }

  network_interface {
    subnet_id          = yandex_vpc_subnet.default.id
    nat                = true
    security_group_ids = [yandex_vpc_security_group.ssh_allow.id]
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu.image_id
      type     = "network-hdd"
      size     = 15
    }
  }

  metadata = {
    ssh-keys = "ubuntu:${var.ssh_key_pub}"
  }
}

output "external_ip" {
  value = yandex_compute_instance.vm.network_interface.0.nat_ip_address
}