#!/bin/bash
#
# MailCow AI Filter - Container Management Script
#
# This script orchestrates all operations through Docker containers.
# No need for local Python venv - everything runs in containers!
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Container name
CONTAINER_NAME="mailcow-ai-filter"
IMAGE_NAME="mailcow-ai-filter:latest"

#==============================================================================
# Helper Functions
#==============================================================================

print_header() {
    echo -e "${BLUE}===============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===============================================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

#==============================================================================
# Container Management
#==============================================================================

build_container() {
    print_header "Building Docker Container"

    if docker images | grep -q "$IMAGE_NAME"; then
        echo "Container image already exists."
        read -p "Rebuild? (y/N): " rebuild
        if [[ ! "$rebuild" =~ ^[Yy]$ ]]; then
            print_info "Skipping rebuild"
            return 0
        fi
    fi

    print_info "Building container image..."
    $DOCKER_COMPOSE build
    print_success "Container built successfully"
}

check_container() {
    if ! docker images | grep -q "mailcow-ai-filter"; then
        print_warning "Container not built yet"
        build_container
    fi
}

#==============================================================================
# Main Operations
#==============================================================================

run_analysis() {
    print_header "Running Email Analysis"
    check_container

    print_info "Starting analysis in container..."
    print_info "This will:"
    echo "  1. Connect to your mailbox"
    echo "  2. Fetch up to 2000 emails"
    echo "  3. Generate AI-powered filter rules"
    echo "  4. Save to output/generated.sieve"
    echo ""

    read -p "Continue? (Y/n): " confirm
    if [[ "$confirm" =~ ^[Nn]$ ]]; then
        print_info "Cancelled"
        return 0
    fi

    # Run the main analysis
    $DOCKER_COMPOSE up

    if [ -f "output/generated.sieve" ]; then
        print_success "Analysis complete!"
        echo ""
        print_info "Generated filter saved to: output/generated.sieve"
        echo ""
        echo "Next steps:"
        echo "  • Review the filter: cat output/generated.sieve"
        echo "  • Create folders: $0 create-folders"
        echo "  • Upload filter: $0 upload-filter"
    else
        print_error "Analysis failed - no filter generated"
        echo "Check logs/ai-filter.log for details"
    fi
}

fetch_existing_filters() {
    print_header "Fetch Existing Sieve Filters"
    check_container

    print_info "Fetching your current Sieve filters..."

    docker run --rm \
        -v "$SCRIPT_DIR/config:/app/config:ro" \
        -v "$SCRIPT_DIR/output:/app/output" \
        -v "$SCRIPT_DIR/.env:/app/.env:ro" \
        --network host \
        "$IMAGE_NAME" \
        python fetch_existing_filters.py

    if [ -f "output/existing_filters.txt" ]; then
        print_success "Filters fetched successfully"
        echo ""
        print_info "Saved to: output/existing_filters.txt"
        echo ""
        read -p "View now? (Y/n): " view
        if [[ ! "$view" =~ ^[Nn]$ ]]; then
            less output/existing_filters.txt
        fi
    fi
}

create_folders() {
    print_header "Create Mail Folders"
    check_container

    print_info "This will create folders from your generated Sieve filter"

    if [ ! -f "output/generated.sieve" ]; then
        print_error "No generated filter found"
        echo "Run '$0 analyze' first"
        return 1
    fi

    # Run interactively with TTY
    docker run --rm -it \
        -v "$SCRIPT_DIR/config:/app/config:ro" \
        -v "$SCRIPT_DIR/output:/app/output:ro" \
        -v "$SCRIPT_DIR/.env:/app/.env:ro" \
        --network host \
        "$IMAGE_NAME" \
        python create_folders.py
}

upload_filter() {
    print_header "Upload Filter to MailCow"
    check_container

    if [ ! -f "output/generated.sieve" ]; then
        print_error "No generated filter found"
        echo "Run '$0 analyze' first"
        return 1
    fi

    print_info "This will upload the filter via MailCow API"
    echo ""
    print_warning "You will need your MailCow API key"
    echo "Get it from: https://mail.kekz.org/admin → System → API"
    echo ""

    # Run interactively with TTY
    docker run --rm -it \
        -v "$SCRIPT_DIR/config:/app/config:ro" \
        -v "$SCRIPT_DIR/output:/app/output:ro" \
        -v "$SCRIPT_DIR/.env:/app/.env:ro" \
        --network host \
        "$IMAGE_NAME" \
        python upload_filter_api.py
}

apply_filters_retroactive() {
    print_header "Apply Filters to Existing Emails"
    check_container

    if [ ! -f "output/generated.sieve" ]; then
        print_error "No generated filter found"
        echo "Run '$0 analyze' first"
        return 1
    fi

    print_info "This will apply your generated filters to existing emails in INBOX"
    echo ""
    print_warning "This modifies your existing emails!"
    echo "The script will:"
    echo "  1. Read your generated filter rules"
    echo "  2. Scan emails in INBOX"
    echo "  3. Move matching emails to their target folders"
    echo "  4. First run a DRY RUN to show what would happen"
    echo ""

    # Run interactively with TTY
    docker run --rm -it \
        -v "$SCRIPT_DIR/config:/app/config:ro" \
        -v "$SCRIPT_DIR/output:/app/output:ro" \
        -v "$SCRIPT_DIR/.env:/app/.env:ro" \
        --network host \
        "$IMAGE_NAME" \
        python apply_filters_retroactive.py
}

view_filter() {
    print_header "View Generated Filter"

    if [ ! -f "output/generated.sieve" ]; then
        print_error "No generated filter found"
        echo "Run '$0 analyze' first"
        return 1
    fi

    less output/generated.sieve
}

view_logs() {
    print_header "View Logs"

    if [ ! -f "logs/ai-filter.log" ]; then
        print_warning "No log file found"
        return 1
    fi

    tail -f logs/ai-filter.log
}

clean_containers() {
    print_header "Clean Up Containers"

    print_info "Removing stopped containers..."
    $DOCKER_COMPOSE down 2>/dev/null || true

    print_info "Removing old images..."
    docker images | grep mailcow-ai-filter | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true

    print_success "Cleanup complete"
}

#==============================================================================
# Interactive Menu
#==============================================================================

show_menu() {
    clear
    print_header "MailCow AI Filter - Container Manager"
    echo ""
    echo "Main Operations:"
    echo "  1) Analyze emails and generate filter"
    echo "  2) Fetch existing Sieve filters"
    echo "  3) Create mail folders (IMAP)"
    echo "  4) Upload filter to MailCow (API)"
    echo "  5) Apply filters to existing emails (retroactive)"
    echo ""
    echo "Utilities:"
    echo "  6) View generated filter"
    echo "  7) View logs (tail -f)"
    echo "  8) Build/rebuild container"
    echo "  9) Clean up containers"
    echo ""
    echo "  0) Exit"
    echo ""
    read -p "Select option: " choice

    case $choice in
        1) run_analysis ;;
        2) fetch_existing_filters ;;
        3) create_folders ;;
        4) upload_filter ;;
        5) apply_filters_retroactive ;;
        6) view_filter ;;
        7) view_logs ;;
        8) build_container ;;
        9) clean_containers ;;
        0) exit 0 ;;
        *) print_error "Invalid option" ;;
    esac

    echo ""
    read -p "Press Enter to continue..."
}

#==============================================================================
# Command-line Interface
#==============================================================================

show_help() {
    cat << EOF
MailCow AI Filter - Container Management Script

USAGE:
    $0 [command]

COMMANDS:
    analyze              Run email analysis and generate filter
    fetch-filters        Fetch existing Sieve filters from server
    create-folders       Create mail folders via IMAP
    upload-filter        Upload filter to MailCow via API
    apply-retroactive    Apply filters to existing emails in INBOX

    view-filter          View generated Sieve filter
    logs                 View logs (tail -f)
    build                Build/rebuild Docker container
    clean                Clean up Docker containers and images

    menu                 Show interactive menu (default)
    help                 Show this help message

EXAMPLES:
    # Interactive menu
    $0

    # Run analysis
    $0 analyze

    # Create folders and upload filter
    $0 create-folders
    $0 upload-filter

    # View results
    $0 view-filter
    cat output/generated.sieve

DOCKER:
    All operations run inside Docker containers.
    No local Python environment needed!

    Configuration: config/config.yml
    Output:        output/generated.sieve
    Logs:          logs/ai-filter.log

MORE INFO:
    README.md           - Project overview
    EXISTING_FILTERS.md - Filter integration guide
    LOCAL_MODELS.md     - Local LLM setup
EOF
}

#==============================================================================
# Main Entry Point
#==============================================================================

main() {
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found"
        echo "Please install Docker first: https://docs.docker.com/get-docker/"
        exit 1
    fi

    # Check for docker-compose or docker compose
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    elif docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
    else
        print_error "docker-compose not found"
        echo "Please install docker-compose or use Docker with compose plugin"
        exit 1
    fi

    # Handle command-line arguments
    case "${1:-menu}" in
        analyze|run)
            run_analysis
            ;;
        fetch-filters|fetch)
            fetch_existing_filters
            ;;
        create-folders|folders)
            create_folders
            ;;
        upload-filter|upload)
            upload_filter
            ;;
        apply-retroactive|retroactive|apply)
            apply_filters_retroactive
            ;;
        view-filter|view)
            view_filter
            ;;
        logs|log)
            view_logs
            ;;
        build)
            build_container
            ;;
        clean|cleanup)
            clean_containers
            ;;
        menu|interactive)
            while true; do
                show_menu
            done
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
