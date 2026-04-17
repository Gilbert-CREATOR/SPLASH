#!/bin/bash

# SPLASH POS - Maintenance Script
# Uso: ./scripts/maintenance.sh [option]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "manage.py not found. Please run this script from the project root."
    exit 1
fi

# Function to show help
show_help() {
    echo "SPLASH POS - Maintenance Script"
    echo ""
    echo "Usage: $0 [option]"
    echo ""
    echo "Options:"
    echo "  check      - Check system health"
    echo "  backup     - Create system backup"
    echo "  cleanup    - Clean temporary files"
    echo "  optimize   - Optimize database"
    echo "  fix        - Fix file permissions"
    echo "  full       - Run complete maintenance"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 check      # Check system health"
    echo "  $0 backup     # Create backup"
    echo "  $0 full       # Run complete maintenance"
}

# Function to run system check
run_check() {
    print_info "Running system health check..."
    python3 manage.py check_system
}

# Function to create backup
run_backup() {
    print_info "Creating system backup..."
    python3 manage.py backup_system
}

# Function to cleanup
run_cleanup() {
    print_info "Cleaning up system..."
    python3 manage.py cleanup_system
}

# Function to optimize database
run_optimize() {
    print_info "Optimizing database..."
    python3 manage.py optimize_database
}

# Function to fix permissions
run_fix_permissions() {
    print_info "Fixing file permissions..."
    python3 manage.py fix_permissions
}

# Function to run complete maintenance
run_full_maintenance() {
    print_info "Starting complete system maintenance..."
    echo ""
    
    print_info "Step 1/5: System Health Check"
    run_check
    echo ""
    
    print_info "Step 2/5: Creating Backup"
    run_backup
    echo ""
    
    print_info "Step 3/5: Cleaning System"
    run_cleanup
    echo ""
    
    print_info "Step 4/5: Optimizing Database"
    run_optimize
    echo ""
    
    print_info "Step 5/5: Fixing Permissions"
    run_fix_permissions
    echo ""
    
    print_status "Complete maintenance finished successfully!"
    print_info "System is now optimized and ready for use."
}

# Main script logic
case "${1:-help}" in
    "check")
        run_check
        ;;
    "backup")
        run_backup
        ;;
    "cleanup")
        run_cleanup
        ;;
    "optimize")
        run_optimize
        ;;
    "fix")
        run_fix_permissions
        ;;
    "full")
        run_full_maintenance
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown option: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
