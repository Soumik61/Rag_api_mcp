variable "resource_group_name" { 
    default = "rag-api-rg"
}

variable "location" {
    default = "eastus"
}

variable "acr_name" {
    default = "ragapiacr"
}

variable "aks_cluster_name" {
    default = "rag-api-aks"
}

variable "node_count" {
    default = 2
}