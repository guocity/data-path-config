# Data Path Config

A Python utility for managing data and log directory paths in projects and subprojects. This package provides a clean interface for handling path configurations across different environments.

## Features

- Configurable data and log directories
- Environment variable support
- .env file integration
- Support for project and subproject structures
- Automatic directory creation
- Path validation

## Installation

```bash
pip install data-path-config
pip install --upgrade data-path-config
```

## Usage

```python
from data_path_config import dpc

# Basic usage
config = dpc(project_name="my_project")
data_dir = config.data_dir()
log_dir = config.log_dir()

# With subproject
config = dpc(
    project_name="my_project",
    subproject="sub1",
    data_dir="/custom/data/path",
    log_dir="/custom/log/path"
)

# Get directories
project_data = config.project_dir()
subproject_data = config.sub_project_dir()
project_logs = config.project_log_dir()
subproject_logs = config.sub_project_log_dir()
```

## License

MIT License

## Python Path Configuration

### Default env variable 
# DATA_DIR
### Default log variable 
# LOG_DIR

## When DATA_DIR doesn't exist, it will throw error

The `pathconfig` package is a Python utility designed to simplify the management of directory paths for data and logs in your projects. It provides a structured way to define, override, and access these paths using constructor arguments, environment variables, or default settings. This ensures consistency and flexibility across different environments, such as local development, production, or cron jobs.

### Key Features
- **Environment Variable Integration**: Reads paths from `.env`, `.zshrc`, or `.profile` files.
- **Constructor Overrides**: Allows explicit path definitions via constructor arguments.
- **Default Paths**: Falls back to sensible defaults (`~/data`, `~/logs`) when no other configuration is provided.
- **Subproject Support**: Easily manage paths for subprojects or experiments.
- **Cron Compatibility**: Ensures paths are resolved correctly in scheduled tasks.
- **Security**: Encourages secure handling of configuration files.

This package is ideal for developers who need a consistent and configurable way to manage project directories, especially in environments with varying configurations.

### Usage Examples

```python
from data_path_config import dpc

# Initialize with explicit data and log directories
config = dpc(
    project_name="my_project",
    data_dir="/custom/data/path",
    log_dir="/custom/log/path",
    subproject="experiment1"
)

# Base directory methods (do not append project/subproject, must exist)
try:
    print(f"Base data dir: {config.data_dir()}")  # /custom/data/path
    print(f"Base log dir: {config.log_dir()}")   # /custom/log/path
except FileNotFoundError as e:
    print(f"Error: {e}")

# Project and subproject directory methods (create if not exist)
print(f"Project data dir: {config.project_dir()}")   # /custom/data/path/my_project
print(f"Subproject data dir: {config.sub_project_dir()}")  # /custom/data/path/my_project/experiment1
print(f"Project log dir: {config.project_log_dir()}")  # /custom/log/path/my_project
print(f"Subproject log dir: {config.sub_project_log_dir()}")  # /custom/log/path/my_project/experiment1

# Initialize without subproject
config_no_sub = PathConfig(
    project_name="my_project",
    data_dir="/custom/data/path",
    log_dir="/custom/log/path"
)
print(f"Base data dir: {config_no_sub.data_dir()}")  # /custom/data/path
print(f"Project data dir: {config_no_sub.project_dir()}")  # /custom/data/path/my_project
try:
    print(config_no_sub.sub_project_dir())  # Raises ValueError
except ValueError as e:
    print(f"Error: {e}")

# Using environment variables or defaults
env_config = PathConfig(project_name="my_project", subproject="experiment1")
try:
    print(f"Base data dir from env: {env_config.data_dir()}")  # e.g., /path/to/data from DATA_DIR
except FileNotFoundError as e:
    print(f"Error: {e}")

# Get an environment variable directly
value = PathConfig.get_env_var("MY_CUSTOM_VAR", "default_value")
print(f"Custom env var: {value}")
```

---

### Configuration Files

#### `.env` (Current Directory)
```plaintext
DATA_DIR=/path/to/data
LOG_DIR=/path/to/logs
MY_CUSTOM_VAR=something
```

#### `.zshrc` or `.profile` (Home Directory)
```plaintext
export DATA_DIR=/path/to/data
export LOG_DIR=/path/to/logs
export MY_CUSTOM_VAR=something
```

---

### Path Resolution Priority
1. Constructor arguments (`data_dir`, `log_dir`).
2. Environment variables (`DATA_DIR`, `LOG_DIR`) from:
   - `.env` (current directory).
   - `~/.zshrc` or `~/.profile` (home directory).
3. Default paths (`~/data`, `~/logs`).

---

### Additional Notes
- **Cron Compatibility**: Works in cron by prioritizing constructor arguments. Ensure `.zshrc` or `.profile` is sourced:
  ```bash
  * * * * * source ~/.zshrc && python /path/to/script.py
  ```
- **Virtual Environments**: Fully compatible.
- **Installation**: Requires `python-dotenv` (`pip install python-dotenv`).
- **Security**: Restrict permissions on configuration files (e.g., `chmod 600 ~/.zshrc`).
- **Testing**: Verify explicit overrides and fallback behavior in clean environments.