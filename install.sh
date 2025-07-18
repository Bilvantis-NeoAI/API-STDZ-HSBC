#!/bin/bash

# API Genie - Global Git Hooks Installation Script
# This script installs the API validation hooks globally for all git repositories

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
APIGENIE_DIR="$HOME/.apigenie"
HOOKS_DIR="$APIGENIE_DIR/hooks"
VALIDATION_DIR="$APIGENIE_DIR/validation"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                        API GENIE                             ║"
echo "║              Global Git Hooks Installation                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect Python command
detect_python() {
    if command_exists python3; then
        echo "python3"
    elif command_exists python; then
        # Check if it's Python 3
        if python --version 2>&1 | grep -q "Python 3"; then
            echo "python"
        else
            echo ""
        fi
    else
        echo ""
    fi
}

# Function to backup existing global hooks path
backup_existing_hooks() {
    local current_hooks_path=$(git config --global --get core.hooksPath 2>/dev/null || echo "")
    if [ ! -z "$current_hooks_path" ]; then
        echo -e "${YELLOW}⚠️  Found existing global hooks path: $current_hooks_path${NC}"
        echo -e "${YELLOW}   This will be backed up to: $APIGENIE_DIR/backup_hooks_path.txt${NC}"
        
        # Create the directory if it doesn't exist
        mkdir -p "$APIGENIE_DIR"
        echo "$current_hooks_path" > "$APIGENIE_DIR/backup_hooks_path.txt"
    fi
}

# Function to create directory structure
create_directories() {
    echo -e "${BLUE}📁 Creating API Genie directory structure...${NC}"
    
    # Remove existing installation if it exists
    if [ -d "$APIGENIE_DIR" ]; then
        echo -e "${YELLOW}⚠️  Existing API Genie installation found. Removing...${NC}"
        rm -rf "$APIGENIE_DIR"
    fi
    
    # Create directories
    mkdir -p "$HOOKS_DIR"
    mkdir -p "$VALIDATION_DIR"
    mkdir -p "$VALIDATION_DIR/ui"
    mkdir -p "$VALIDATION_DIR/validators"
    
    echo -e "${GREEN}✅ Directory structure created${NC}"
}

# Function to copy validation files
copy_validation_files() {
    echo -e "${BLUE}📋 Copying validation system files...${NC}"
    
    # Get the script directory (where this install.sh is located)
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    
    # Copy validation package
    cp -r "$SCRIPT_DIR/validation/"* "$VALIDATION_DIR/"
    
    # Copy hooks
    cp "$SCRIPT_DIR/hooks/pre-commit" "$HOOKS_DIR/"
    cp "$SCRIPT_DIR/hooks/pre-push" "$HOOKS_DIR/"
    
    # Copy requirements and demo
    cp "$SCRIPT_DIR/requirements.txt" "$APIGENIE_DIR/"
    cp "$SCRIPT_DIR/demo_interactive.py" "$APIGENIE_DIR/"
    
    # Make hooks executable
    chmod +x "$HOOKS_DIR/pre-commit"
    chmod +x "$HOOKS_DIR/pre-push"
    
    echo -e "${GREEN}✅ Validation files copied${NC}"
}

# Function to create version info
create_version_info() {
    cat > "$APIGENIE_DIR/version.txt" << EOF
API Genie Version 1.0.0
Installation Date: $(date)
Installation Path: $APIGENIE_DIR
Git Hooks Path: $HOOKS_DIR
EOF
}

# Function to create uninstall script
create_uninstall_script() {
    cat > "$APIGENIE_DIR/uninstall.sh" << 'EOF'
#!/bin/bash

# API Genie - Global Git Hooks Uninstallation Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

APIGENIE_DIR="$HOME/.apigenie"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                        API GENIE                             ║"
echo "║             Global Git Hooks Uninstallation                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}This will remove the global API validation hooks.${NC}"
echo -e "${YELLOW}Your repositories will no longer have automatic API validation.${NC}"
echo ""
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Uninstallation cancelled.${NC}"
    exit 0
fi

echo -e "${BLUE}🔧 Removing global git hooks configuration...${NC}"

# Remove global hooks path
git config --global --unset core.hooksPath

# Restore backup if it exists
if [ -f "$APIGENIE_DIR/backup_hooks_path.txt" ]; then
    backup_path=$(cat "$APIGENIE_DIR/backup_hooks_path.txt")
    echo -e "${YELLOW}📁 Restoring previous hooks path: $backup_path${NC}"
    git config --global core.hooksPath "$backup_path"
fi

echo -e "${BLUE}🗑️  Removing API Genie directory...${NC}"
rm -rf "$APIGENIE_DIR"

echo -e "${GREEN}✅ API Genie has been successfully uninstalled!${NC}"
echo -e "${BLUE}ℹ️  Your git repositories will now use default or local hooks.${NC}"
EOF

    chmod +x "$APIGENIE_DIR/uninstall.sh"
    echo -e "${GREEN}✅ Uninstall script created${NC}"
}

# Function to update hook paths in copied files
update_hook_paths() {
    echo -e "${BLUE}🔧 Updating hook file paths...${NC}"
    
    # Update pre-commit hook
    sed -i.bak "s|PROJECT_ROOT=\"\$(dirname \"\$HOOK_DIR\")\"|PROJECT_ROOT=\"$APIGENIE_DIR\"|g" "$HOOKS_DIR/pre-commit"
    
    # Update pre-push hook  
    sed -i.bak "s|PROJECT_ROOT=\"\$(dirname \"\$HOOK_DIR\")\"|PROJECT_ROOT=\"$APIGENIE_DIR\"|g" "$HOOKS_DIR/pre-push"
    
    # Remove backup files
    rm -f "$HOOKS_DIR/pre-commit.bak" "$HOOKS_DIR/pre-push.bak"
    
    echo -e "${GREEN}✅ Hook paths updated${NC}"
}

# Function to check dependencies
check_dependencies() {
    echo -e "${BLUE}🔍 Checking dependencies...${NC}"
    
    # Detect Python command
    PYTHON_CMD=$(detect_python)
    if [ -z "$PYTHON_CMD" ]; then
        echo -e "${RED}❌ Python 3 is required but not installed${NC}"
        echo -e "${YELLOW}   Please install Python 3 (python3 or python command)${NC}"
        exit 1
    fi
    
    # Check Git
    if ! command_exists git; then
        echo -e "${RED}❌ Git is required but not installed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Python detected: $PYTHON_CMD${NC}"
    echo -e "${GREEN}✅ Dependencies checked${NC}"
}

# Function to configure git
configure_git() {
    echo -e "${BLUE}⚙️  Configuring global git hooks...${NC}"
    
    # Set global hooks path
    git config --global core.hooksPath "$HOOKS_DIR"
    
    echo -e "${GREEN}✅ Git configured to use API Genie hooks${NC}"
}

# Function to test installation
test_installation() {
    echo -e "${BLUE}🧪 Testing installation...${NC}"
    
    # Test API validator
    cd "$APIGENIE_DIR"
    if $PYTHON_CMD -m validation.api_validator --identify-only > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API validator is working${NC}"
    else
        echo -e "${YELLOW}⚠️  API validator test completed (this is normal for non-API repositories)${NC}"
    fi
    
    # Test demo (if in interactive environment)
    if [ -t 0 ] && [ -t 1 ] && command_exists $PYTHON_CMD; then
        echo -e "${BLUE}🎯 Installation complete! You can test the UI with:${NC}"
        echo -e "   ${CYAN}cd ~/.apigenie && $PYTHON_CMD demo_interactive.py${NC}"
    fi
}

# Function to display success message
display_success() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                   INSTALLATION COMPLETE!                    ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}🎉 API Genie has been successfully installed globally!${NC}"
    echo ""
    echo -e "${CYAN}📁 Installation Directory:${NC} $APIGENIE_DIR"
    echo -e "${CYAN}🪝 Git Hooks Directory:${NC} $HOOKS_DIR"
    echo ""
    echo -e "${YELLOW}📋 What happens now:${NC}"
    echo -e "   • All your git repositories will use API Genie hooks"
    echo -e "   • Only PCF and SHP/IKP repositories will be validated"
    echo -e "   • Other repositories will proceed normally"
    echo -e "   • Push operations with failures will show interactive UI"
    echo ""
    echo -e "${CYAN}🛠️  Management Commands:${NC}"
    echo -e "   • Test UI:        ${YELLOW}cd ~/.apigenie && $PYTHON_CMD demo_interactive.py${NC}"
    echo -e "   • Check version:  ${YELLOW}cat ~/.apigenie/version.txt${NC}"
    echo -e "   • Uninstall:      ${YELLOW}~/.apigenie/uninstall.sh${NC}"
    echo ""
    echo -e "${GREEN}🚀 Happy coding with validated APIs!${NC}"
}

# Main installation process
main() {
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        echo -e "${RED}❌ Please do not run this script as root${NC}"
        echo -e "${YELLOW}   Run it as your normal user to install in your home directory${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🚀 Starting API Genie installation...${NC}"
    echo ""
    
    # Installation steps
    check_dependencies
    backup_existing_hooks
    create_directories
    copy_validation_files
    update_hook_paths
    create_version_info
    create_uninstall_script
    configure_git
    test_installation
    display_success
}

# Run main function
main "$@" 