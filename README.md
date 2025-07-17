# API Validation Git Hooks

This project provides git hooks for validating code against API rules. The hooks use Python-native validation logic with shell script wrappers and feature an **interactive UI for handling validation failures during push operations**.

## 🌟 Key Features

- **Smart Repository Detection**: Only validates PCF and SHP/IKP repos
- **20 Compliance Rules**: Comprehensive validation against standardized API rules
- **Interactive UI**: Tkinter-based dialog for handling validation failures during push
- **Audit Trail**: Automatic commit message updates when proceeding despite failures
- **Graceful Fallback**: Console mode when GUI is not available

## Interactive Validation Workflow

### Developer-Friendly Approach
- **Commits**: Always allowed with friendly reminders for API projects
- **Push**: Full validation with interactive UI for handling failures

When pushing code with validation failures, the system provides an interactive experience:

### 1. **Validation Dialog** 🔍
- Displays all validation errors and warnings
- Shows affected api.meta files
- Provides clear, actionable error messages
- Lists compliance rules for reference

### 2. **User Choice** ⚖️
- **Cancel Push & Fix Issues**: Safely cancel to address problems
- **Proceed Despite Failures**: Continue with mandatory justification

### 3. **Justification Required** 📝
- Prompts for detailed justification message
- Validates justification quality (minimum length, meaningful content)
- Example: "Emergency hotfix for production issue. Will address validation failures in follow-up commit."

### 4. **Audit Trail** 📋
- Automatically appends justification to commit message
- Includes all validation failures for audit purposes
- Creates permanent record of override decision

## Project Structure

```
├── hooks/                          # Git hook shell scripts
│   ├── pre-commit                   # Pre-commit validation hook
│   └── pre-push                     # Pre-push comprehensive validation hook
├── validation/                      # Python validation package
│   ├── __init__.py                  # Package initialization
│   ├── api_validator.py             # Main validation orchestrator
│   ├── api_identifier.py            # API type identification logic
│   ├── config_loader.py             # Configuration management
│   ├── meta_file_finder.py          # Meta file discovery and parsing
│   ├── git_utils.py                 # Git operations for commit message updates
│   ├── ui/                          # Interactive UI components
│   │   ├── __init__.py
│   │   └── validation_dialog.py     # Tkinter validation dialog
│   └── validators/                  # Specific validator modules
│       ├── __init__.py
│       ├── base_validator.py        # Base validator class
│       └── meta_validator.py        # Compliance rules validator
├── setup_hooks.sh                   # Local repository hook setup script
├── install.sh                       # 🌟 Global installation script
├── uninstall.sh                     # Global uninstallation script
├── status.sh                        # Installation status checker
├── demo_interactive.py              # Demo script for testing UI
└── README.md                        # This file
```

## API Type Identification

The system automatically identifies the API type based on these rules:

### PCF (Platform Control Framework) Projects
- **Condition 1**: No folder named `SHP` or `IKP` exists in the root directory
- **Condition 2**: Repository name contains `-decision-service-`

**Example**: `rp-ccs-decision-services-am-sa-hk-hbar`

### SHP/IKP Projects
- **Condition 1**: Folder named `SHP` or `IKP` exists in the root directory
- **Condition 2**: Repository name contains `-ds-`

**Example**: `rp-cos-ds-ao-sa=gb-hbeu` (with SHP folder)

## Compliance Rules

The system validates `api.meta` files against 20 compliance rules. Both PCF and SHP/IKP projects use the same rules:

### Required Fields and Values

1. **metaDataVersion**: Must be ≥ 6.0.0
2. **assetName**: Must match pattern `^[a-z]+(?:-?[a-z0-9]+)*$`
3. **assetVersion**: Must start with `1.0.0` (allows `1.0.0.*`)
4. **autoIncrementAssetVersion**: Must be `true`
5. **contractFileName**: Must not be missing
6. **ignore**: Must be `false`
7. **API.layer**: Must be one of `[xAPI, sAPI, eAPI]`
8. **API.audience**: Must be one of `[internal, external]`
9. **API.version.contractVersion**: Must match pattern `^[vV]?[0-9]+(?:\.[0-9]+){1,2}$`
10. **API.version.status**: Must be one of `[develop, test, prelive, live, deprecated, demised]`
11. **API.version.privateAPI**: Must not be missing
12. **API.version.apiStyle**: Must be one of `[HYDROGEN, DOMAIN_PAPI, ORIGINATIONS, BANKING 2.0, FIRST_DIRECT, BERLIN, STET, OBIE, OTHER]`
13. **API.version.architecturalStyle**: Must be one of `[REST, GRAPHQL, SOAP, RPC]`
14. **API.version.businessModels**: Required when `API.layer` is `xAPI` (must not be empty)
15. **API.version.dataClassification**: Must be one of `[public, internal, confidential, restricted, secret]`
16. **GBGF**: Must be one of `[CMB, Central-Architecture, Corporate-Functions, Group-Data, FCR, GBM, GPB, Cyber-Security, ITID, OSS, Payments, RBWM, HBFR, Risk, DAO, WSIT, WPB, Compliance, CTO, Enterprise Technology, GOA]` (can be in `API.contract.GBGF` or `contractOwner.GBGF`)
17. **serviceLine**: Must not be missing (can be in `API.contractOwner.serviceLine` or `contractOwner.serviceLine`)
18. **teamName**: Must not be missing (can be in `API.contractOwner.teamName` or `contractOwner.teamName`)
19. **teamEmailAddress**: Must not be missing (can be in `API.contractOwner.teamEmailAddress` or `contractOwner.teamEmailAddress`)
20. **API.version.transactionNames**: Required when `API.layer` is `sAPI` (must not be empty)

## 🚀 Installation

### Option 1: Global Installation (Recommended)

Install API Genie globally to work with all your git repositories:

```bash
# Clone or download this repository first
git clone <repository-url>
cd API\ Standardization

# Install globally
./install.sh
```

This will:
- Create `~/.apigenie` directory with all validation files
- Set git global `core.hooksPath` to use API Genie hooks
- Apply to ALL git repositories on your system
- Only validate PCF and SHP/IKP repositories (others proceed normally)

**Global Installation Structure:**
```
~/.apigenie/
├── hooks/                          # Global git hooks
│   ├── pre-commit                   # Pre-commit validation hook
│   └── pre-push                     # Interactive pre-push hook
├── validation/                      # Complete validation system
│   ├── api_validator.py
│   ├── ui/validation_dialog.py      # Interactive UI
│   └── validators/meta_validator.py # Compliance rules
├── demo_interactive.py              # UI demo script
├── version.txt                      # Installation info
├── uninstall.sh                     # Uninstaller
└── requirements.txt                 # Dependencies
```

### Option 2: Local Installation (Per Repository)

Install hooks in a specific repository only:

```bash
# In your git repository
chmod +x setup_hooks.sh
./setup_hooks.sh
```

### Management Commands

```bash
# Check installation status
./status.sh

# Test the interactive UI
cd ~/.apigenie && python3 demo_interactive.py

# Uninstall (removes global hooks)
./uninstall.sh
```

## Usage

### Automatic Validation
- **Pre-commit**: Runs automatically when you commit, validating staged files
- **Pre-push**: Runs automatically when you push, with **interactive UI for failures**
- **Smart Skip**: Only validates PCF and SHP/IKP repos, other repos proceed normally

### Manual Validation
```bash
# Validate specific files
python3 -m validation.api_validator --files file1.py file2.json

# Validate staged files
python3 -m validation.api_validator --staged-files

# Validate commit range (interactive mode)
python3 -m validation.api_validator --commit-range main..feature-branch --interactive

# Just identify API type
python3 -m validation.api_validator --identify-only

# Find and display all api.meta files
python3 -m validation.api_validator --find-meta

# Run compliance validation only
python3 -m validation.api_validator --compliance-only
```

## Example: Commit Message with Override

When a user proceeds despite validation failures, the commit message is automatically updated:

```
Original commit message

==================================================
⚠️  VALIDATION OVERRIDE NOTICE
==================================================

JUSTIFICATION:
  Emergency hotfix for production issue. Will address validation failures in follow-up commit.

VALIDATION ERRORS (3):
  • test_api/api.meta - assetVersion "2.0.0" should start with "1.0.0"
  • test_api/api.meta - API.layer "pAPI" is not in allowed values
  • test_api/api.meta - GBGF "INVALID_GBGF" is not in allowed values

This commit was pushed despite validation failures.
Review and address these issues in a follow-up commit.
==================================================
```

### API Meta File Discovery
The system automatically finds `api.meta` files throughout the repository and uses them for validation:

**Supported formats:**
- `api.meta` (YAML/Properties)
- `api.meta.yaml` / `api.meta.yml` (YAML)
- `api.meta.json` (JSON)
- `API.meta` / `API.META` (case variations)

**Discovery features:**
- Recursive search through all directories
- Smart directory skipping (ignores `.git`, `node_modules`, etc.)
- Multiple format parsing (JSON, YAML, properties) - uses built-in parsers
- Closest meta file matching for validation

## Configuration

The system looks for configuration files in this order:
- `api_validation.yaml`
- `api_validation.yml`
- `api_validation.json`
- `.api_validation.yaml`
- `.api_validation.yml`
- `.api_validation.json`

Create a default configuration file:
```bash
python3 -c "from validation.config_loader import ConfigLoader; ConfigLoader().save_default_config()"
```

## Extending Validation Rules

The validation logic is designed to be extended. Currently, the system:

1. **Identifies API type** (PCF vs SHP/IKP)
2. **Validates api.meta files** against 20 compliance rules
3. **Provides placeholder methods** for type-specific validation:
   - `_validate_pcf_file()` - for PCF projects
   - `_validate_shp_ikp_file()` - for SHP/IKP projects

### Adding Custom Validators

1. Create a new validator class inheriting from `BaseValidator`
2. Implement the `validate_file()` method
3. Add the validator to the `APIValidator` initialization

## File Type Support

By default, the system validates these file types:
- `.py` (Python)
- `.yaml`, `.yml` (YAML)
- `.json` (JSON)

Ignored patterns:
- `__pycache__`, `.git`, `node_modules`
- `.pytest_cache`, `venv`, `.venv`
- `target`, `build`, `dist`

## Development

### Testing the Setup

**After Global Installation:**
```bash
# Check installation status
./status.sh

# Test the interactive UI
cd ~/.apigenie && python3 demo_interactive.py

# Test API identification (from any git repository)
cd ~/.apigenie && python3 -m validation.api_validator --identify-only

# Test compliance validation
cd ~/.apigenie && python3 -m validation.api_validator --compliance-only
```

**For Local Installation:**
```bash
# Test in a git repository
./setup_hooks.sh

# Test API identification
python3 -m validation.api_validator --identify-only

# Demo interactive UI
python3 demo_interactive.py
```

### Hook Behavior

**Global Installation (Recommended):**
- Works automatically in ALL git repositories
- Only validates PCF and SHP/IKP repositories
- Other repositories proceed without validation
- No per-repository setup needed

**Hook Actions:**
- **Pre-commit**: Validates only staged files, fails commit if validation fails
- **Pre-push**: Shows interactive UI for validation failures, allows override with justification
- **Exit codes**: 0 = success or user-approved override, 1 = validation failed or user cancelled

## Compliance Validation Results

When running compliance validation, you'll see results like:

```bash
🔍 Validating 2 api.meta file(s) against compliance rules...
  📄 Validating meta file: api.meta
    ✅ Compliance validation passed for api.meta

📋 Compliance Validation Summary:
Meta files validated: 1
Compliance errors: 0
Compliance warnings: 0
✅ All compliance rules passed!
```

## Troubleshooting

### Global Installation Issues
```bash
# Check if API Genie is properly installed
./status.sh

# Verify git configuration
git config --global --get core.hooksPath
# Should show: /Users/yourname/.apigenie/hooks

# Test in a PCF/SHP/IKP repository
cd ~/.apigenie && python3 -m validation.api_validator --identify-only
```

### Common Problems

**Hooks not running:**
- Check: `git config --global --get core.hooksPath`
- Reinstall: `./install.sh`

**GUI not working:**
- System falls back to console mode automatically
- Install tkinter: `python3 -m pip install tk --user`

**Permission errors:**
- Make scripts executable: `chmod +x ~/.apigenie/hooks/*`
- Check Python permissions for temp files

**Python import errors:**
- Install dependencies: `cd ~/.apigenie && python3 -m pip install -r requirements.txt --user`
- Check Python path in hooks

### Reset Everything
```bash
# Complete reset
./uninstall.sh
./install.sh
```

## Next Steps

This system provides comprehensive API validation with:
- ✅ **Global installation system with ~/.apigenie**
- ✅ **All 20 compliance rules implemented**
- ✅ **Interactive UI for validation failures**
- ✅ **Automatic commit message updates for overrides**
- ✅ **Graceful fallback to console mode**
- ✅ **Complete audit trail for all validation decisions**

The validation logic can be further customized based on specific project requirements. 