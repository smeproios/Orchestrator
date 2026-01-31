# SMEPro Orchestrator - Terraform Variables

variable "azure_subscription_id" {
  description = "Azure Subscription ID"
  type        = string
  sensitive   = true
}

variable "azure_tenant_id" {
  description = "Azure AD Tenant ID"
  type        = string
  sensitive   = true
}

variable "azure_region" {
  description = "Azure region for resources"
  type        = string
  default     = "southcentralus"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "sql_admin_username" {
  description = "SQL Server administrator username"
  type        = string
  default     = "smeproadmin"
}

variable "sql_admin_password" {
  description = "SQL Server administrator password"
  type        = string
  sensitive   = true
}

variable "azuread_admin_object_id" {
  description = "Object ID of Azure AD admin for SQL"
  type        = string
}

variable "allowed_ip_ranges" {
  description = "List of allowed IP ranges for firewall rules"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project    = "SMEPro-Orchestrator"
    Owner      = "Lamar-University-LCOB"
    CostCenter = "LCOB-IT"
  }
}
