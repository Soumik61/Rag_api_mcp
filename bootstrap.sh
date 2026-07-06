#!/bin/bash
# Run this ONCE to set up Terraform remote state and Service Principal
# After this, everything is automated via CI/CD

set -e

RESOURCE_GROUP="terraform-state-rg"
STORAGE_ACCOUNT="tfstateragapi"
CONTAINER_NAME="tfstate"
LOCATION="eastus"
SP_NAME="github-actions-rag-api"

echo "Creating resource group for Terraform state..."
az group create --name $RESOURCE_GROUP --location $LOCATION

echo "Creating storage account..."
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --sku Standard_LRS

echo "Creating storage container..."
az storage container create \
  --name $CONTAINER_NAME \
  --account-name $STORAGE_ACCOUNT

echo "Creating Service Principal..."
az ad sp create-for-rbac \
  --name $SP_NAME \
  --role contributor \
  --scopes /subscriptions/$(az account show --query id -o tsv) \
  --sdk-auth

echo ""
echo "✅ Bootstrap complete!"
echo "Next steps:"
echo "  1. Add Service Principal JSON output as AZURE_CREDENTIALS in GitHub Secrets"
echo "  2. Add Service Principal to Azure DevOps Service Connection"
echo "  3. Run: cd terraform && terraform init -migrate-state"