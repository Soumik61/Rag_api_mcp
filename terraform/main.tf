terraform {
    required_providers {
        azurerm = {
            source = "hashicorp/azurerm"
            version = "~> 3.0"
        }
    }
}

provider "azurerm" {
    features {}
}

resource "azurerm_resource_group" "rg" {
    name        = var.resource_group_name
    location    = var.location
}

resource "azurerm_container_registry" "acr" {
    name                = var.acr_name
    resource_group_name = azurerm_resource_group.rg.name
    location            = azurerm_resource_group.rg.location
    sku                 = "Basic"
    admin_enabled       = true
}

resource "azurerm_kubernetes_cluster" "aks" {
    name                = var.aks_cluster_name
    location            = azurerm_resource_group.rg.location
    resource_group_name = azurerm_resource_group.rg.name
    dns_prefix         = "ragapi"

    default_node_pool {
        name       = "default"
        node_count = var.node_count
        vm_size    = "Standard_d2s_v7"
    }

    identity {
        type = "SystemAssigned"
    }
}

resource "azurerm_role_assignment" "aks_acr" {
    principal_id = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
    role_definition_name = "AcrPull"
    scope = azurerm_container_registry.acr.id
    skip_service_principal_aad_check = true
  
}