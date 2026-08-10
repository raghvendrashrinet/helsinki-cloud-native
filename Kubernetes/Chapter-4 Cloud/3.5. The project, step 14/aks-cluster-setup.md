
## 1. Create AKS Cluster

| Bash | PowerShell | CMD |
|------|------------|-----|
| RESOURCE_GROUP="rg1"<br>AKS_NAME="myAKSCluster"<br>LOCATION="eastus" | $RESOURCE_GROUP = "rg1" <br>$AKS_NAME = "myAKSCluster"<br>$LOCATION = "eastus" | set RESOURCE_GROUP="rg1" <br>set AKS_NAME=myAKSCluster<br>set LOCATION=eastus |

```
# Create resource group
az group create --name myResourceGroup --location eastus       -- Bash
az group create --name $RESOURCE_GROUP --location $LOCATION    -- Powershell
az group create --name %RESOURCE_GROUP% --location %LOCATION%  -- CMD


# Create AKS cluster
az aks create --resource-group $RESOURCE_GROUP --name $AKS_NAME --node-count 1 --node-vm-size Standard_B2s --generate-ssh-keys


# Get cluster credentials
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_NAME
```

