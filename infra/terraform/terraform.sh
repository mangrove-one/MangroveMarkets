#!/usr/bin/env bash
# MangroveMarkets Terraform Helper Script
# Ensures consistent usage of Terraform with proper project configuration

set -euo pipefail

PROJECT_ID="mangrove-markets"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

usage() {
    cat <<EOF
MangroveMarkets Terraform Helper

Usage: $0 <command> <environment> [terraform-args]

Commands:
  init        Initialize Terraform with backend config
  plan        Run Terraform plan
  apply       Run Terraform apply
  destroy     Run Terraform destroy
  output      Show Terraform outputs
  validate    Validate Terraform configuration
  fmt         Format Terraform files

Environments:
  dev         Development environment
  prod        Production environment

Examples:
  $0 init dev
  $0 plan dev
  $0 apply prod
  $0 output dev

Note: All gcloud commands use --project=${PROJECT_ID} flag to prevent
      accidental changes to global gcloud configuration.
EOF
    exit 1
}

check_prerequisites() {
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed. Please install Terraform >= 1.5"
        exit 1
    fi

    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed"
        exit 1
    fi

    log_info "Checking GCP authentication..."
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" --project="${PROJECT_ID}" &> /dev/null; then
        log_error "Not authenticated to GCP. Run: gcloud auth application-default login"
        exit 1
    fi
}

check_state_bucket() {
    log_info "Checking Terraform state bucket..."
    if ! gsutil ls -p "${PROJECT_ID}" gs://mangrove-markets-terraform-state &> /dev/null; then
        log_warn "Terraform state bucket does not exist. Creating it..."
        gsutil mb -p "${PROJECT_ID}" -l us-central1 gs://mangrove-markets-terraform-state
        gsutil versioning set on gs://mangrove-markets-terraform-state
        log_info "State bucket created successfully"
    fi
}

validate_environment() {
    local env=$1
    if [[ "$env" != "dev" && "$env" != "prod" ]]; then
        log_error "Invalid environment: $env. Must be 'dev' or 'prod'"
        usage
    fi
}

cmd_init() {
    local env=$1
    validate_environment "$env"

    log_info "Initializing Terraform for ${env} environment..."
    check_state_bucket

    cd "$SCRIPT_DIR"
    terraform init -backend-config="backend-${env}.hcl" "${@:2}"
}

cmd_plan() {
    local env=$1
    validate_environment "$env"

    log_info "Planning Terraform changes for ${env} environment..."
    cd "$SCRIPT_DIR"
    terraform plan -var-file="environment-${env}.tfvars" "${@:2}"
}

cmd_apply() {
    local env=$1
    validate_environment "$env"

    log_warn "This will apply changes to ${env} environment!"
    read -p "Are you sure? (yes/no): " confirm

    if [[ "$confirm" != "yes" ]]; then
        log_info "Apply cancelled"
        exit 0
    fi

    log_info "Applying Terraform changes for ${env} environment..."
    cd "$SCRIPT_DIR"
    terraform apply -var-file="environment-${env}.tfvars" "${@:2}"
}

cmd_destroy() {
    local env=$1
    validate_environment "$env"

    log_error "WARNING: This will DESTROY all infrastructure in ${env} environment!"
    read -p "Type the environment name to confirm: " confirm

    if [[ "$confirm" != "$env" ]]; then
        log_info "Destroy cancelled"
        exit 0
    fi

    log_info "Destroying Terraform resources for ${env} environment..."
    cd "$SCRIPT_DIR"
    terraform destroy -var-file="environment-${env}.tfvars" "${@:2}"
}

cmd_output() {
    local env=$1
    validate_environment "$env"

    log_info "Fetching Terraform outputs for ${env} environment..."
    cd "$SCRIPT_DIR"
    terraform output "${@:2}"
}

cmd_validate() {
    log_info "Validating Terraform configuration..."
    cd "$SCRIPT_DIR"
    terraform validate
}

cmd_fmt() {
    log_info "Formatting Terraform files..."
    cd "$SCRIPT_DIR"
    terraform fmt -recursive "${@:2}"
}

# Main
if [ $# -lt 1 ]; then
    usage
fi

COMMAND=$1

case "$COMMAND" in
    init|plan|apply|destroy|output)
        if [ $# -lt 2 ]; then
            log_error "Environment argument required for $COMMAND"
            usage
        fi
        check_prerequisites
        "cmd_${COMMAND}" "${@:2}"
        ;;
    validate|fmt)
        check_prerequisites
        "cmd_${COMMAND}" "${@:2}"
        ;;
    *)
        log_error "Unknown command: $COMMAND"
        usage
        ;;
esac
