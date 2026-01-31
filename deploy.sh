#!/bin/bash
# SMEPro Orchestrator - Deployment Script
# Platform-First Infrastructure Setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${ENVIRONMENT:-"prod"}
AZURE_REGION=${AZURE_REGION:-"southcentralus"}
TF_STATE_RG="rg-smepro-terraform"
TF_STATE_STORAGE="smeprotfstate"
TF_STATE_CONTAINER="tfstate"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    command -v az >/dev/null 2>&1 || { log_error "Azure CLI not found. Install: https://aka.ms/installazurecli"; exit 1; }
    command -v terraform >/dev/null 2>&1 || { log_error "Terraform not found. Install: https://terraform.io/downloads"; exit 1; }
    command -v kubectl >/dev/null 2>&1 || { log_error "kubectl not found. Install: https://kubernetes.io/docs/tasks/tools/"; exit 1; }
    command -v helm >/dev/null 2>&1 || { log_error "Helm not found. Install: https://helm.sh/docs/intro/install/"; exit 1; }
    
    log_success "All prerequisites met"
}

# Login to Azure
azure_login() {
    log_info "Checking Azure authentication..."
    
    if ! az account show >/dev/null 2>&1; then
        log_info "Please login to Azure..."
        az login
    fi
    
    SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
    log_success "Authenticated to Azure subscription: $SUBSCRIPTION_NAME"
}

# Setup Terraform backend
setup_tf_backend() {
    log_info "Setting up Terraform backend..."
    
    # Check if resource group exists
    if ! az group show --name $TF_STATE_RG >/dev/null 2>&1; then
        log_info "Creating Terraform resource group..."
        az group create --name $TF_STATE_RG --location $AZURE_REGION
    fi
    
    # Check if storage account exists
    if ! az storage account show --name $TF_STATE_STORAGE --resource-group $TF_STATE_RG >/dev/null 2>&1; then
        log_info "Creating Terraform storage account..."
        az storage account create \
            --name $TF_STATE_STORAGE \
            --resource-group $TF_STATE_RG \
            --location $AZURE_REGION \
            --sku Standard_GRS \
            --encryption-services blob
    fi
    
    # Check if container exists
    STORAGE_KEY=$(az storage account keys list --account-name $TF_STATE_STORAGE --resource-group $TF_STATE_RG --query '[0].value' -o tsv)
    
    if ! az storage container show --name $TF_STATE_CONTAINER --account-name $TF_STATE_STORAGE --account-key $STORAGE_KEY >/dev/null 2>&1; then
        log_info "Creating Terraform state container..."
        az storage container create \
            --name $TF_STATE_CONTAINER \
            --account-name $TF_STATE_STORAGE \
            --account-key $STORAGE_KEY
    fi
    
    log_success "Terraform backend ready"
}

# Deploy infrastructure with Terraform
deploy_infrastructure() {
    log_info "Deploying Azure infrastructure with Terraform..."
    
    cd ../terraform
    
    # Initialize Terraform
    log_info "Initializing Terraform..."
    terraform init
    
    # Validate configuration
    log_info "Validating Terraform configuration..."
    terraform validate
    
    # Plan deployment
    log_info "Planning Terraform deployment..."
    terraform plan -out=tfplan
    
    # Apply deployment
    log_info "Applying Terraform deployment..."
    terraform apply tfplan
    
    # Export outputs
    log_info "Exporting Terraform outputs..."
    terraform output -json > ../config/terraform-outputs.json
    
    log_success "Infrastructure deployed successfully"
}

# Configure kubectl
configure_kubectl() {
    log_info "Configuring kubectl..."
    
    AKS_NAME=$(terraform output -raw aks_cluster_name)
    RG_NAME="rg-smepro-$ENVIRONMENT"
    
    az aks get-credentials \
        --name $AKS_NAME \
        --resource-group $RG_NAME \
        --overwrite-existing
    
    log_success "kubectl configured for cluster: $AKS_NAME"
}

# Deploy Kubernetes resources
deploy_kubernetes() {
    log_info "Deploying Kubernetes resources..."
    
    cd ../kubernetes
    
    # Create namespaces
    log_info "Creating namespaces..."
    kubectl apply -f namespace.yaml
    
    # Create secrets
    log_info "Creating Kubernetes secrets..."
    create_secrets
    
    # Deploy core services
    log_info "Deploying SMEPro Orchestrator..."
    kubectl apply -f orchestrator-deployment.yaml
    
    # Deploy ingress
    log_info "Configuring ingress..."
    kubectl apply -f ingress.yaml
    
    # Wait for deployment
    log_info "Waiting for deployment to be ready..."
    kubectl rollout status deployment/smepro-orchestrator -n smepro --timeout=300s
    
    log_success "Kubernetes resources deployed"
}

# Create Kubernetes secrets
create_secrets() {
    log_info "Creating Kubernetes secrets from Terraform outputs..."
    
    cd ../config
    
    # Parse Terraform outputs
    OPENAI_ENDPOINT=$(cat terraform-outputs.json | jq -r '.openai_endpoint.value')
    SQL_FQDN=$(cat terraform-outputs.json | jq -r '.sql_server_fqdn.value')
    COSMOS_ENDPOINT=$(cat terraform-outputs.json | jq -r '.cosmos_endpoint.value')
    STORAGE_NAME=$(cat terraform-outputs.json |jq -r '.storage_account_name.value')
    
    # Get secrets from Key Vault
    KV_NAME="kv-smepro-$ENVIRONMENT"
    
    OPENAI_KEY=$(az keyvault secret show --name openai-key --vault-name $KV_NAME --query value -o tsv)
    SQL_PASSWORD=$(az keyvault secret show --name sql-admin-password --vault-name $KV_NAME --query value -o tsv)
    COSMOS_KEY=$(az keyvault secret show --name cosmos-key --vault-name $KV_NAME --query value -o tsv)
    STORAGE_KEY=$(az keyvault secret show --name storage-key --vault-name $KV_NAME --query value -o tsv)
    REDIS_HOST=$(az keyvault secret show --name redis-host --vault-name $KV_NAME --query value -o tsv)
    REDIS_PASSWORD=$(az keyvault secret show --name redis-password --vault-name $KV_NAME --query value -o tsv)
    
    # Create Kubernetes secret
    kubectl create secret generic smepro-secrets \
        --namespace=smepro \
        --from-literal=openai-endpoint="$OPENAI_ENDPOINT" \
        --from-literal=openai-key="$OPENAI_KEY" \
        --from-literal=sql-connection-string="Server=$SQL_FQDN;Database=smepro-db;User Id=smeproadmin;Password=$SQL_PASSWORD;Encrypt=true;" \
        --from-literal=cosmos-endpoint="$COSMOS_ENDPOINT" \
        --from-literal=cosmos-key="$COSMOS_KEY" \
        --from-literal=storage-account-name="$STORAGE_NAME" \
        --from-literal=storage-account-key="$STORAGE_KEY" \
        --from-literal=redis-host="$REDIS_HOST" \
        --from-literal=redis-password="$REDIS_PASSWORD" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Kubernetes secrets created"
}

# Install monitoring stack
install_monitoring() {
    log_info "Installing monitoring stack..."
    
    # Add Helm repositories
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo update
    
    # Install Prometheus
    log_info "Installing Prometheus..."
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace smepro-monitoring \
        --create-namespace \
        --set grafana.enabled=true \
        --set grafana.adminPassword=admin \
        --wait
    
    log_success "Monitoring stack installed"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check pods
    log_info "Pod status:"
    kubectl get pods -n smepro
    
    # Check services
    log_info "Service status:"
    kubectl get svc -n smepro
    
    # Check ingress
    log_info "Ingress status:"
    kubectl get ingress -n smepro
    
    # Test health endpoint
    log_info "Testing health endpoint..."
    kubectl port-forward svc/smepro-orchestrator 8080:80 -n smepro &
    PF_PID=$!
    sleep 3
    
    if curl -s http://localhost:8080/health | grep -q "healthy"; then
        log_success "Health check passed"
    else
        log_warning "Health check failed or not yet ready"
    fi
    
    kill $PF_PID 2>/dev/null || true
    
    log_success "Deployment verification complete"
}

# Print deployment summary
print_summary() {
    echo ""
    echo "=========================================="
    echo -e "${GREEN}SMEPro Orchestrator Deployment Complete${NC}"
    echo "=========================================="
    echo ""
    echo "Environment: $ENVIRONMENT"
    echo "Region: $AZURE_REGION"
    echo ""
    echo "API Endpoint: https://api.smepro.lamar.edu"
    echo "App Builder: https://apps.smepro.lamar.edu"
    echo "Grafana: https://grafana.smepro.lamar.edu"
    echo ""
    echo "Useful commands:"
    echo "  kubectl get pods -n smepro"
    echo "  kubectl logs -f deployment/smepro-orchestrator -n smepro"
    echo "  az aks browse --name aks-smepro-$ENVIRONMENT --resource-group rg-smepro-$ENVIRONMENT"
    echo ""
    echo "=========================================="
}

# Main deployment flow
main() {
    echo "=========================================="
    echo -e "${BLUE}SMEPro Orchestrator - Platform-First Deployment${NC}"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    azure_login
    setup_tf_backend
    deploy_infrastructure
    configure_kubectl
    deploy_kubernetes
    install_monitoring
    verify_deployment
    print_summary
}

# Run main function
main "$@"
