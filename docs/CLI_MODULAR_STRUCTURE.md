# CLI Modular Structure

## Overview

The CLI has been successfully refactored from a monolithic 1,460-line file into a modular, maintainable structure with proper separation of concerns.

## Directory Structure

```
cli/
├── __init__.py                 # Package initialization
├── main.py                     # New main entry point
├── commands.py                 # Legacy compatibility layer
├── core/                       # Core CLI utilities
│   ├── __init__.py
│   ├── colors.py              # ANSI color codes and formatting
│   ├── status.py              # Status bars and progress indicators
│   └── terminal.py            # Terminal utilities and helpers
├── utils/                      # System utilities
│   ├── __init__.py
│   └── system.py              # System info, environment validation
├── parsers/                    # Argument parsing
│   ├── __init__.py
│   └── args.py                # Command-line argument setup
└── handlers/                   # Command implementations
    ├── __init__.py
    ├── run.py                 # Run command
    ├── launch.py              # Launch command
    ├── connect.py             # Connect command
    ├── profiles.py            # Profiles command
    ├── diagnose.py            # Diagnose command
    ├── clean.py               # Clean command
    ├── config.py              # Config command
    ├── debug.py               # Debug command
    ├── version.py             # Version command
    └── help.py                # Help command
```

## Module Responsibilities

### core/

- **colors.py**: ANSI color codes, formatting functions
- **status.py**: Status bars, progress indicators, success/error messages
- **terminal.py**: Terminal utilities, banner display, user interaction

### utils/

- **system.py**: System information gathering, environment validation, dependency checking

### parsers/

- **args.py**: Complete argument parser setup with all commands and options

### handlers/

- **Individual command files**: Each command has its own dedicated file for better maintainability

## Usage

### New Entry Point

```bash
# Use the new modular CLI
uv run main.py [command] [options]
```

### Backward Compatibility

```bash
# Legacy compatibility still works
uv run cli/commands.py [command] [options]
```

## Benefits

1. **Maintainability**: Each module has a single responsibility
2. **Testability**: Individual components can be tested in isolation
3. **Scalability**: Easy to add new commands or modify existing ones
4. **Readability**: Code is organized logically with clear separation
5. **Reusability**: Core utilities can be shared across commands

## Import Structure

All modules use absolute imports for better reliability:

```python
from cli.core import print_colored, Colors
from cli.utils import get_system_info
```

## Migration Notes

- Original `cli/commands.py` preserved as compatibility layer
- All functionality maintained with identical behavior
- No breaking changes to existing CLI interface
- Better error handling and import resolution

## Development Guidelines

1. **Adding new commands**: Create new file in `handlers/` directory
2. **Shared utilities**: Add to appropriate module in `core/` or `utils/`
3. **Import style**: Always use absolute imports (`cli.core`, not `..core`)
4. **Testing**: Test both new entry point and backward compatibility
