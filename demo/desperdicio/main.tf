# Cria recursos "esquecidos" e baratos para a demo de caça ao desperdício.
# Custo aproximado: menos de US$ 3 em quatro dias. Destrua depois da palestra: terraform destroy.

terraform {
  required_version = ">= 1.6"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

locals {
  tags = {
    owner       = var.owner
    environment = "demo"
    project     = "mvpconf-2026-finops"
  }
}

# RG com expires-at no passado: aparece em 08-ambientes-vencidos.kql
resource "azurerm_resource_group" "demo" {
  name     = "rg-finops-demo-desperdicio"
  location = var.location
  tags     = merge(local.tags, { "expires-at" = "2026-09-20T00:00:00Z" })
}

# Disco de uma VM que já foi apagada: 01-discos-orfaos.kql
resource "azurerm_managed_disk" "orfao" {
  name                 = "disk-vm-antiga-os"
  resource_group_name  = azurerm_resource_group.demo.name
  location             = azurerm_resource_group.demo.location
  storage_account_type = "Standard_LRS"
  create_option        = "Empty"
  disk_size_gb         = 32
  tags                 = local.tags
}

# IP público que sobrou de um teste: 02-ips-publicos-sem-uso.kql
resource "azurerm_public_ip" "sem_uso" {
  name                = "pip-teste-que-ficou"
  resource_group_name = azurerm_resource_group.demo.name
  location            = azurerm_resource_group.demo.location
  allocation_method   = "Static"
  sku                 = "Standard"
  tags                = local.tags
}

resource "azurerm_virtual_network" "demo" {
  name                = "vnet-finops-demo"
  resource_group_name = azurerm_resource_group.demo.name
  location            = azurerm_resource_group.demo.location
  address_space       = ["10.42.0.0/16"]
  tags                = local.tags
}

resource "azurerm_subnet" "demo" {
  name                 = "snet-demo"
  resource_group_name  = azurerm_resource_group.demo.name
  virtual_network_name = azurerm_virtual_network.demo.name
  address_prefixes     = ["10.42.1.0/24"]
}

# NIC sem VM e sem tags (de propósito): 03-nics-orfas.kql e 07-recursos-sem-tags.kql
resource "azurerm_network_interface" "orfa" {
  name                = "nic-sem-vm"
  resource_group_name = azurerm_resource_group.demo.name
  location            = azurerm_resource_group.demo.location

  ip_configuration {
    name                          = "ipconfig1"
    subnet_id                     = azurerm_subnet.demo.id
    private_ip_address_allocation = "Dynamic"
  }
}

# Plano de um projeto cancelado, sem nenhum app: 04-app-service-plans-vazios.kql
resource "azurerm_service_plan" "vazio" {
  name                = "asp-projeto-cancelado"
  resource_group_name = azurerm_resource_group.demo.name
  location            = azurerm_resource_group.demo.location
  os_type             = "Linux"
  sku_name            = "B1"
  tags                = local.tags
}
