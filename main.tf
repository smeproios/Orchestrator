# SMEPro Orchestrator - Azure Infrastructure
# Platform-First Architecture for Lamar University
# Terraform v1.5+

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.75"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.45"
    }
  }
  
  backend "azurerm" {
    resource_group_name  = "rg-smepro-terraform"
    storage_account_name = "smeprotfstate"
    container_name       = "tfstate"
    key                  = "smepro-orchestrator.tfstate"
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
  subscription_id = var.azure_subscription_id
  tenant_id       = var.azure_tenant_id
}

# Resource Group
resource "azurerm_resource_group" "smepro" {
  name     = "rg-smepro-${var.environment}"
  location = var.azure_region
  
  tags = {
    Environment = var.environment
    Project     = "SMEPro-Orchestrator"
    Owner       = "Lamar-University-LCOB"
    CostCenter  = "LCOB-IT"
  }
}

# Virtual Network
resource "azurerm_virtual_network" "smepro" {
  name                = "vnet-smepro-${var.environment}"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.smepro.location
  resource_group_name = azurerm_resource_group.smepro.name
}

resource "azurerm_subnet" "aks" {
  name                 = "snet-aks"
  resource_group_name  = azurerm_resource_group.smepro.name
  virtual_network_name = azurerm_virtual_network.smepro.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_subnet" "database" {
  name                 = "snet-database"
  resource_group_name  = azurerm_resource_group.smepro.name
  virtual_network_name = azurerm_virtual_network.smepro.name
  address_prefixes     = ["10.0.2.0/24"]
  service_endpoints    = ["Microsoft.Sql", "Microsoft.AzureCosmosDB"]
}

# Azure Kubernetes Service
resource "azurerm_kubernetes_cluster" "smepro" {
  name                = "aks-smepro-${var.environment}"
  location            = azurerm_resource_group.smepro.location
  resource_group_name = azurerm_resource_group.smepro.name
  dns_prefix          = "smepro-${var.environment}"
  kubernetes_version  = "1.28"

  default_node_pool {
    name                = "system"
    node_count          = 2
    vm_size             = "Standard_D4s_v3"
    type                = "VirtualMachineScaleSets"
    zones               = [1, 2, 3]
    vnet_subnet_id      = azurerm_subnet.aks.id
    
    node_labels = {
      "node-type" = "system"
    }
    
    tags = {
      Environment = var.environment
      NodeType    = "system"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    network_policy    = "calico"
    load_balancer_sku = "standard"
  }

  azure_policy_enabled = true
  
  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.smepro.id
  }

  key_vault_secrets_provider {
    secret_rotation_enabled = true
  }

  tags = {
    Environment = var.environment
    Project     = "SMEPro-Orchestrator"
  }
}

# User node pool for workloads
resource "azurerm_kubernetes_cluster_node_pool" "workloads" {
  name                  = "workloads"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.smepro.id
  vm_size               = "Standard_D8s_v3"
  node_count            = 3
  zones                 = [1, 2, 3]
  vnet_subnet_id        = azurerm_subnet.aks.id
  
  node_labels = {
    "node-type" = "workloads"
    "workload"  = "smepro-apps"
  }

  node_taints = []

  tags = {
    Environment = var.environment
    NodeType    = "workloads"
  }
}

# Azure Container Registry
resource "azurerm_container_registry" "smepro" {
  name                = "crsmepro${var.environment}"
  resource_group_name = azurerm_resource_group.smepro.name
  location            = azurerm_resource_group.smepro.location
  sku                 = "Premium"
  admin_enabled       = false
  
  network_rule_set {
    default_action = "Deny"
    ip_rule = [
      {
        action   = "Allow"
        ip_range = var.allowed_ip_ranges
      }
    ]
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = var.environment
    Project     = "SMEPro-Orchestrator"
  }
}

# ACR pull role for AKS
resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.smepro.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_kubernetes_cluster.smepro.kubelet_identity[0].object_id
}

# Azure OpenAI Service
resource "azurerm_cognitive_account" "openai" {
  name                = "oai-smepro-${var.environment}"
  location            = "eastus"  # OpenAI available regions
  resource_group_name = azurerm_resource_group.smepro.name
  kind                = "OpenAI"
  sku_name            = "S0"
  
  custom_subdomain_name = "smepro-openai-${var.environment}"
  
  network_acls {
    default_action = "Deny"
    ip_rules       = var.allowed_ip_ranges
    virtual_network_rules {
      subnet_id = azurerm_subnet.aks.id
    }
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = var.environment
    Project     = "SMEPro-Orchestrator"
  }
}

# GPT-4 Deployment
resource "azurerm_cognitive_deployment" "gpt4" {
  name                 = "gpt-4"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  
  model {
    format  = "OpenAI"
    name    = "gpt-4"
    version = "0613"
  }

  scale {
    type     = "Standard"
    capacity = 120
  }
}

# GPT-3.5-Turbo Deployment
resource "azurerm_cognitive_deployment" "gpt35" {
  name                 = "gpt-35-turbo"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  
  model {
    format  = "OpenAI"
    name    = "gpt-35-turbo"
    version = "0613"
  }

  scale {
    type     = "Standard"
    capacity = 240
  }
}

# Azure SQL Server
resource "azurerm_mssql_server" "smepro" {
  name                         = "sql-smepro-${var.environment}"
  resource_group_name          = azurerm_resource_group.smepro.name
  location                     = azurerm_resource_group.smepro.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_username
  administrator_login_password = var.sql_admin_password
  
  minimum_tls_version          = "1.2"
  public_network_access_enabled = false

  azuread_administrator {
    login_username = "AzureAD Admin"
    object_id      = var.azuread_admin_object_id
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = var.environment
    Project     = "SMEPro-Orchestrator"
  }
}

# Azure SQL Database
resource "azurerm_mssql_database" "smepro" {
  name                = "smepro-db"
  server_id           = azurerm_mssql_server.smepro.id
  sku_name            = "GP_Gen5_4"
  collation           = "SQL_Latin1_General_CP1_CI_AS"
  max_size_gb         = 250
  
  zone_redundant      = true
  
  short_term_retention_policy {
    retention_days = 35
  }

  long_term_retention_policy {
    weekly_retention  = "P4W"
    monthly_retention = "P12M"
    yearly_retention  = "P5Y"
  }

  tags = {
    Environment = var.environment
    Project     = "SMEPro-Orchestrator"
  }
}

# SQL Server private endpoint
resource "azurerm_private_endpoint" "sql" {
  name                = "pe-sql-smepro"
  location            = azurerm_resource_group.smepro.location
  resource_group_name = azurerm_resource_group.smepro.name
  subnet_id           = azurerm_subnet.database.id

  private_service_connection {
    name                           = "psc-sql"
    private_connection_resource_id = azurerm_mssql_server.smepro.id
    subresource_names              = ["sqlServer"]
    is_manual_connection           = false
  }
}

# Cosmos DB Account
resource "azurerm_cosmosdb_account" "smepro" {
  name                = "cosmos-smepro-${var.environment}"
  location            = azurerm_resource_group.smepro.location
  resource_group_name = azurerm_resource_group.smepro.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  enable_free_tier    = false
  enable_multiple_write_locations = true

  consistency_policy {
    consistency_level       = "Session"
    max_interval_in_seconds = 5
    max_staleness_prefix    = 100
  }

  geo_location {
    location          = azurerm_resource_group.smepro.location
    failover_priority = 0
    zone_redundant    = true
  }

  geo_location {
    location          = "eastus"
    failover_priority = 1
    zone_redundant    = false
  }

  capabilities {
    name = "EnableServerless"
  }

  virtual_network_rule {
    id = azurerm_subnet.database.id
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = var.environment
    Project     = "SMEPro-Orchestrator"
  }
}

# Cosmos DB Database
resource "azurerm_cosmosdb_sql_database" "smepro" {
  name                = "smepro-ontology"
  resource_group_name = azurerm_resource_group.smepro.name
  account_name        = azurerm_cosmosdb_account.smepro.name
}

# Cosmos DB Containers
resource "azurerm_cosmosdb_sql_container" "cip_naics_mappings" {
  name                  = "cip_naics_mappings"
  resource_group_name   = azurerm_resource_group.smepro.name
  account_name          = azurerm_cosmosdb_account.smepro.name
  database_name         = azurerm_cosmosdb_sql_database.smepro.name
  partition_key_path    = "/cip_code"
  partition_key_version = 2

  indexing_policy {
    indexing_mode = "consistent"
    
    included_path {
      path = "/*"
    }
  }
}

resource "azurerm_cosmosdb_sql_container" "logic_templates" {
  name                  = "logic_templates"
  resource_group_name   = azurerm_resource_group.smepro.name
  account_name          = azurerm_cosmosdb_account.smepro.name
  database_name         = azurerm_cosmosdb_sql_database.smepro.name
  partition_key_path    = "/naics_code"
  partition_key_version = 2
}

resource "azurerm_cosmosdb_sql_container" "user_sessions" {
  name                  = "user_sessions"
  resource_group_name   = azurerm_resource_group.smepro.name
  account_name          = azurerm_cosmosdb_account.smepro.name
  database_name         = azurerm_cosmosdb_sql_database.smepro.name
  partition_key_path    = "/user_id"
  partition_key_version = 2
  
  default_ttl = 86400  # 24 hours
}

# Azure Storage Account
resource "azurerm_storage_account" "smepro" {
  name                     = "stsmepro${var.environment}"
  resource_group_name      = azurerm_resource_group.smepro.name
  location                 = azurerm_resource_group.smepro.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  
  min_tls_version                 = "TLS1_2"
  enable_https_traffic_only       = true
  allow_nested_items_to_be_public = false
  
  network_rules {
    default_action             = "Deny"
    ip_rules                   = var.allowed_ip_ranges
    virtual_network_subnet_ids = [azurerm_subnet.aks.id]
    bypass                     = ["AzureServices"]
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = var.environment
    Project     = "SMEPro-Orchestrator"
  }
}

# Storage Containers
resource "azurerm_storage_container" "reports" {
  name                  = "reports"
  storage_account_name  = azurerm_storage_account.smepro.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "app_artifacts" {
  name                  = "app-artifacts"
  storage_account_name  = azurerm_storage_account.smepro.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "datasets" {
  name                  = "datasets"
  storage_account_name  = azurerm_storage_account.smepro.name
  container_access_type = "private"
}

# Azure Front Door (CDN)
resource "azurerm_cdn_profile" "smepro" {
  name                = "fd-smepro-${var.environment}"
  location            = "Global"
  resource_group_name = azurerm_resource_group.smepro.name
  sku                 = "Premium_Verizon"

  tags = {
    Environment = var.environment
    Project     = "SMEPro-Orchestrator"
  }
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "smepro" {
  name                = "law-smepro-${var.environment}"
  location            = azurerm_resource_group.smepro.location
  resource_group_name = azurerm_resource_group.smepro.name
  sku                 = "PerGB2018"
  retention_in_days   = 90

  tags = {
    Environment = var.environment
    Project     = "SMEPro-Orchestrator"
  }
}

# Application Insights
resource "azurerm_application_insights" "smepro" {
  name                = "appi-smepro-${var.environment}"
  location            = azurerm_resource_group.smepro.location
  resource_group_name = azurerm_resource_group.smepro.name
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.smepro.id

  tags = {
    Environment = var.environment
    Project     = "SMEPro-Orchestrator"
  }
}

# Key Vault
resource "azurerm_key_vault" "smepro" {
  name                = "kv-smepro-${var.environment}"
  location            = azurerm_resource_group.smepro.location
  resource_group_name = azurerm_resource_group.smepro.name
  tenant_id           = var.azure_tenant_id
  sku_name            = "premium"
  
  soft_delete_retention_days = 90
  purge_protection_enabled   = true
  
  network_acls {
    default_action = "Deny"
    ip_rules       = var.allowed_ip_ranges
    virtual_network_rules {
      id = azurerm_subnet.aks.id
    }
  }

  tags = {
    Environment = var.environment
    Project     = "SMEPro-Orchestrator"
  }
}

# Key Vault Access Policy for AKS
resource "azurerm_key_vault_access_policy" "aks" {
  key_vault_id = azurerm_key_vault.smepro.id
  tenant_id    = var.azure_tenant_id
  object_id    = azurerm_kubernetes_cluster.smepro.kubelet_identity[0].object_id

  secret_permissions = ["Get", "List"]
}

# Azure Redis Cache
resource "azurerm_redis_cache" "smepro" {
  name                = "redis-smepro-${var.environment}"
  location            = azurerm_resource_group.smepro.location
  resource_group_name = azurerm_resource_group.smepro.name
  capacity            = 2
  family              = "P"
  sku_name            = "Premium"
  
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"
  
  redis_configuration {
    maxmemory_reserved = 400
    maxmemory_delta    = 200
    maxmemory_policy   = "allkeys-lru"
  }

  subnet_id = azurerm_subnet.database.id

  tags = {
    Environment = var.environment
    Project     = "SMEPro-Orchestrator"
  }
}

# Outputs
output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.smepro.name
}

output "aks_cluster_endpoint" {
  value = azurerm_kubernetes_cluster.smepro.kube_config.0.host
}

output "openai_endpoint" {
  value = azurerm_cognitive_account.openai.endpoint
}

output "sql_server_fqdn" {
  value = azurerm_mssql_server.smepro.fully_qualified_domain_name
}

output "cosmos_endpoint" {
  value = azurerm_cosmosdb_account.smepro.endpoint
}

output "storage_account_name" {
  value = azurerm_storage_account.smepro.name
}
