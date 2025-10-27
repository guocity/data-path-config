import os
import pathlib
import logging
import sys
from typing import Optional
from datetime import date

class DataPathConfig:
    """
    A class to manage data and log directory paths for projects and subprojects.
    Reads from constructor arguments with fallback defaults.
    Ensures compatibility with cron and virtual environments.
    """
    # Static logger for early logging before instance logger is set
    _static_logger = logging.getLogger("DataPathConfig_static")
    _static_logger.setLevel(logging.INFO)
    if not _static_logger.handlers:
        _static_handler = logging.StreamHandler()
        _static_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        _static_logger.addHandler(_static_handler)

    def __init__(
        self,
        project_name: str,
        data_dir: Optional[str] = None,
        log_dir: Optional[str] = None,
        default_data_dir: str = "~/data",
        default_log_dir: str = "~/logs",
        subproject: Optional[str] = None,
        create_dirs: bool = True,
        log_level: int = logging.INFO,
        propagate: bool = False  # <-- add this line
    ):
        """
        Initialize PathConfig with project details and path settings.

        Args:
            project_name (str): Name of the project (used in path construction).
            data_dir (Optional[str]): Direct data directory path.
            log_dir (Optional[str]): Direct log directory path.
            default_data_dir (str): Fallback data directory if not specified.
            default_log_dir (str): Fallback log directory if not specified.
            subproject (Optional[str]): Subproject name for nested folder structure.
            create_dirs (bool): Whether to create project/subproject directories if they don't exist.
        """
        self.project_name = project_name
        self.subproject = subproject
        self.data_dir_arg = data_dir
        self.log_dir_arg = log_dir
        self.default_data_dir = default_data_dir
        self.default_log_dir = default_log_dir
        self.create_dirs = create_dirs

        # Check if running in an Airflow environment by checking for AIRFLOW_HOME
        if "AIRFLOW_HOME" in os.environ:
            airflow_data_dir = "/opt/airflow/data"
            airflow_log_dir = "/opt/airflow/logs"
            self.default_data_dir = airflow_data_dir
            self.default_log_dir = airflow_log_dir
            if self.data_dir_arg is None:
                self.data_dir_arg = airflow_data_dir
            if self.log_dir_arg is None:
                self.log_dir_arg = airflow_log_dir

        # Set up project-specific logger first
        self.logger = self.get_logger(level=log_level, propagate=propagate)

    def get_logger(self, level: int = logging.INFO, propagate: bool = False) -> logging.Logger:
        """
        Returns a project-specific logger writing to the project log directory.
        Allows control of propagation to the root logger.
        """
        logger_name = f"{self.project_name}_logger"
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        logger.propagate = propagate
        logger.handlers.clear()

        log_path = self.project_log_dir()
        logfile = str(log_path / f"{self.project_name}.log")
        file_handler = logging.FileHandler(logfile, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(file_handler)
        return logger

    def _resolve_path(self, path_source: Optional[str], default_path: str, base_only: bool = False, include_subproject: bool = True) -> pathlib.Path:
        """
        Resolve a path from a provided path or default.

        Args:
            path_source (Optional[str]): Direct path provided.
            default_path (str): Default path if path_source is not set.
            base_only (bool): If True, return the base path without project/subproject.
            include_subproject (bool): If False, exclude subproject from path (used when base_only is False).

        Returns:
            pathlib.Path: Resolved absolute path.

        Raises:
            FileNotFoundError: If the base path does not exist.
            NotADirectoryError: If the resolved path is not a directory.
            RuntimeError: For other path resolution errors.
        """
        path_str = path_source if path_source is not None else default_path
        logger = getattr(self, "logger", DataPathConfig._static_logger)
        try:
            # Expand ~ and environment variables in the path
            path_str = os.path.expanduser(os.path.expandvars(path_str))
            path = pathlib.Path(path_str)

            # For base_only, check existence and return without project/subproject
            if base_only:
                if not path.exists():
                    logger.error(f"Base path {path} does not exist")
                    raise FileNotFoundError(f"Base path {path} does not exist")
                if not path.is_dir():
                    logger.error(f"Base path {path} is not a directory")
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
                    logger.info(f"Created directory: {path}")
                except Exception as e:
                    logger.error(f"Failed to create directory {path}: {e}")
                    raise RuntimeError(f"Cannot create directory {path}: {e}")

            # Verify path is a directory
            if not path.is_dir():
                logger.error(f"Path {path} is not a directory")
                raise NotADirectoryError(f"Path {path} is not a directory")

            return path
        except Exception as e:
            logger.error(f"Error resolving path for {path_str}: {e}")
            raise RuntimeError(f"Failed to resolve path for {path_str}: {e}")

    def data_dir(self) -> pathlib.Path:
        """
        Return the base data directory path (without project or subproject).

        Returns:
            pathlib.Path: Absolute path to the base data directory.

        Raises:
            FileNotFoundError: If the base data directory does not exist.
        """
        return self._resolve_path(self.data_dir_arg, self.default_data_dir, base_only=True)

    def project_dir(self) -> pathlib.Path:
        """
        Return the base data directory path for the project (excludes subproject).

        Returns:
            pathlib.Path: Absolute path to the project data directory.
        """
        return self._resolve_path(self.data_dir_arg, self.default_data_dir, base_only=False, include_subproject=False)

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
        return self._resolve_path(self.data_dir_arg, self.default_data_dir, base_only=False, include_subproject=True)

    def log_dir(self) -> pathlib.Path:
        """
        Return the base log directory path (without project or subproject).

        Returns:
            pathlib.Path: Absolute path to the base log directory.

        Raises:
            FileNotFoundError: If the base log directory does not exist.
        """
        return self._resolve_path(self.log_dir_arg, self.default_log_dir, base_only=True)

    def project_log_dir(self) -> pathlib.Path:
        """
        Return the base log directory path for the project (excludes subproject).

        Returns:
            pathlib.Path: Absolute path to the project log directory.
        """
        return self._resolve_path(self.log_dir_arg, self.default_log_dir, base_only=False, include_subproject=False)

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
        return self._resolve_path(self.log_dir_arg, self.default_log_dir, base_only=False, include_subproject=True)

    def get_project_today_file_name(self, filetype: str = "json") -> pathlib.Path:
        """
        Generate a filename with today's date in the project directory.

        Args:
            filetype (str): File extension (default: "json").

        Returns:
            pathlib.Path: Full path to the date-stamped file in the project directory.
        """
        if self.subproject:
            file_path = self.sub_project_dir() / f"{self.project_name}_{self.subproject}_{date.today()}.{filetype}"
        else:
            file_path = self.project_dir() / f"{self.project_name}_{date.today()}.{filetype}"
        return file_path