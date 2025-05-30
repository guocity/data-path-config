import os
import pathlib
import logging
from typing import Optional
from dotenv import load_dotenv

class DataPathConfig:
    """
    A class to manage data and log directory paths for projects and subprojects.
    Reads from constructor arguments, .env, .zshrc, .profile, or environment variables,
    with fallback defaults. Ensures compatibility with cron and virtual environments.
    """
    def __init__(
        self,
        project_name: str,
        data_dir: Optional[str] = None,
        log_dir: Optional[str] = None,
        data_env_var: str = "DATA_DIR",
        log_env_var: str = "LOG_DIR",
        default_data_dir: str = "~/data",
        default_log_dir: str = "~/logs",
        subproject: Optional[str] = None,
        create_dirs: bool = True
    ):
        """
        Initialize PathConfig with project details and path settings.

        Args:
            project_name (str): Name of the project (used in path construction).
            data_dir (Optional[str]): Direct data directory path (overrides env vars).
            log_dir (Optional[str]): Direct log directory path (overrides env vars).
            data_env_var (str): Environment variable name for data directory.
            log_env_var (str): Environment variable name for log directory.
            default_data_dir (str): Fallback data directory if not specified.
            default_log_dir (str): Fallback log directory if not specified.
            subproject (Optional[str]): Subproject name for nested folder structure.
            create_dirs (bool): Whether to create project/subproject directories if they don't exist.
        """
        self.project_name = project_name
        self.subproject = subproject
        self.data_dir_arg = data_dir
        self.log_dir_arg = log_dir
        self.data_env_var = data_env_var
        self.log_env_var = log_env_var
        self.default_data_dir = default_data_dir
        self.default_log_dir = default_log_dir
        self.create_dirs = create_dirs

        # Set up logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Load configuration files if data_dir or log_dir not provided
        if self.data_dir_arg is None or self.log_dir_arg is None:
            self._load_env()

    def _load_env(self) -> None:
        """Load environment variables from .env if it exists."""
        env_path = pathlib.Path(".env")
        if env_path.exists():
            try:
                load_dotenv(dotenv_path=env_path)
                self.logger.info(f"Loaded .env file from {env_path}")
            except Exception as e:
                self.logger.warning(f"Failed to load .env file: {e}")
        else:
            self.logger.debug("No .env file found in current directory")

    def _resolve_path(self, path_source: Optional[str], env_var: str, default_path: str, base_only: bool = False, include_subproject: bool = True) -> pathlib.Path:
        """
        Resolve a path from a provided path, environment variable, or default.

        Args:
            path_source (Optional[str]): Direct path provided in constructor.
            env_var (str): Environment variable to check if path_source is None.
            default_path (str): Default path if neither path_source nor env_var is set.
            base_only (bool): If True, return the base path without project/subproject.
            include_subproject (bool): If False, exclude subproject from path (used when base_only is False).

        Returns:
            pathlib.Path: Resolved absolute path.

        Raises:
            FileNotFoundError: If the base path does not exist.
            NotADirectoryError: If the resolved path is not a directory.
            RuntimeError: For other path resolution errors.
        """
        path_str = path_source if path_source is not None else os.getenv(env_var, default_path)
        try:
            # Expand ~ and environment variables in the path
            path_str = os.path.expanduser(os.path.expandvars(path_str))
            path = pathlib.Path(path_str)

            # For base_only, check existence and return without project/subproject
            if base_only:
                if not path.exists():
                    self.logger.error(f"Base path {path} does not exist")
                    raise FileNotFoundError(f"Base path {path} does not exist")
                if not path.is_dir():
                    self.logger.error(f"Base path {path} is not a directory")
                    raise NotADirectoryError(f"Base path {path} is not a directory")
                return path.resolve()

            # Append project and subproject if specified
            if self.project_name:
                path = path / self.project_name
            if include_subproject and self.subproject:
                path = path / self.subproject

            # Resolve to absolute path
            path = path.resolve()

            # Create directory if it doesn't exist and create_dirs is True
            if self.create_dirs and not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"Created directory: {path}")
                except Exception as e:
                    self.logger.error(f"Failed to create directory {path}: {e}")
                    raise RuntimeError(f"Cannot create directory {path}: {e}")

            # Verify path is a directory
            if not path.is_dir():
                self.logger.error(f"Path {path} is not a directory")
                raise NotADirectoryError(f"Path {path} is not a directory")

            return path
        except Exception as e:
            self.logger.error(f"Error resolving path for {env_var or path_str}: {e}")
            raise RuntimeError(f"Failed to resolve path for {env_var or path_str}: {e}")

    def data_dir(self) -> pathlib.Path:
        """
        Return the base data directory path (without project or subproject).

        Returns:
            pathlib.Path: Absolute path to the base data directory.

        Raises:
            FileNotFoundError: If the base data directory does not exist.
        """
        return self._resolve_path(self.data_dir_arg, self.data_env_var, self.default_data_dir, base_only=True)

    def project_dir(self) -> pathlib.Path:
        """
        Return the base data directory path for the project (excludes subproject).

        Returns:
            pathlib.Path: Absolute path to the project data directory.
        """
        return self._resolve_path(self.data_dir_arg, self.data_env_var, self.default_data_dir, base_only=False, include_subproject=False)

    def sub_project_dir(self) -> pathlib.Path:
        """
        Return the data directory path for the subproject.

        Returns:
            pathlib.Path: Absolute path to the subproject data directory.

        Raises:
            ValueError: If no subproject is specified.
        """
        if not self.subproject:
            self.logger.error("No subproject specified for sub_project_dir")
            raise ValueError("No subproject specified")
        return self._resolve_path(self.data_dir_arg, self.data_env_var, self.default_data_dir, base_only=False, include_subproject=True)

    def log_dir(self) -> pathlib.Path:
        """
        Return the base log directory path (without project or subproject).

        Returns:
            pathlib.Path: Absolute path to the base log directory.

        Raises:
            FileNotFoundError: If the base log directory does not exist.
        """
        return self._resolve_path(self.log_dir_arg, self.log_env_var, self.default_log_dir, base_only=True)

    def project_log_dir(self) -> pathlib.Path:
        """
        Return the base log directory path for the project (excludes subproject).

        Returns:
            pathlib.Path: Absolute path to the project log directory.
        """
        return self._resolve_path(self.log_dir_arg, self.log_env_var, self.default_log_dir, base_only=False, include_subproject=False)

    def sub_project_log_dir(self) -> pathlib.Path:
        """
        Return the log directory path for the subproject.

        Returns:
            pathlib.Path: Absolute path to the subproject log directory.

        Raises:
            ValueError: If no subproject is specified.
        """
        if not self.subproject:
            self.logger.error("No subproject specified for sub_project_log_dir")
            raise ValueError("No subproject specified")
        return self._resolve_path(self.log_dir_arg, self.log_env_var, self.default_log_dir, base_only=False, include_subproject=True)

    @staticmethod
    def get_env_var(var_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve an environment variable directly.

        Args:
            var_name (str): Name of the environment variable.
            default (Optional[str]): Default value if variable is not set.

        Returns:
            Optional[str]: Value of the environment variable or default.
        """
        return os.getenv(var_name, default)