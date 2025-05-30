import os
import pathlib
import pytest
import shutil
from data_path_config.path import PathConfig

@pytest.fixture
def clean_env(monkeypatch):
    # Remove environment variables for isolation
    monkeypatch.delenv("DATA_DIR", raising=False)
    monkeypatch.delenv("LOG_DIR", raising=False)

def print_green(msg):
    print(f"\033[92m{msg}\033[0m")

def test_data_dir_base(tmp_path, clean_env):
    print_green("Running test_data_dir_base...")
    # Use /tmp/data and /tmp/log for testing
    data_root = pathlib.Path("/tmp/data")
    log_root = pathlib.Path("/tmp/log")
    data_root.mkdir(parents=True, exist_ok=True)
    log_root.mkdir(parents=True, exist_ok=True)
    pc = PathConfig(
        project_name="projA",
        data_dir=str(data_root),
        log_dir=str(log_root),
        subproject="subA"
    )
    assert pc.data_dir() == data_root.resolve()
    assert pc.project_dir() == (data_root / "projA").resolve()
    assert pc.sub_project_dir() == (data_root / "projA" / "subA").resolve()
    print_green("test_data_dir_base passed.")
    # Cleanup
    shutil.rmtree(data_root, ignore_errors=True)
    shutil.rmtree(log_root, ignore_errors=True)

def test_log_dir_base(tmp_path, clean_env):
    print_green("Running test_log_dir_base...")
    data_root = pathlib.Path("/tmp/data")
    log_root = pathlib.Path("/tmp/log")
    data_root.mkdir(parents=True, exist_ok=True)
    log_root.mkdir(parents=True, exist_ok=True)
    pc = PathConfig(
        project_name="projB",
        data_dir=str(data_root),
        log_dir=str(log_root),
        subproject="subB"
    )
    assert pc.log_dir() == log_root.resolve()
    assert pc.project_log_dir() == (log_root / "projB").resolve()
    assert pc.sub_project_log_dir() == (log_root / "projB" / "subB").resolve()
    print_green("test_log_dir_base passed.")
    # Cleanup
    shutil.rmtree(data_root, ignore_errors=True)
    shutil.rmtree(log_root, ignore_errors=True)

def test_no_subproject_raises(tmp_path, clean_env):
    print_green("Running test_no_subproject_raises...")
    data_root = pathlib.Path("/tmp/data")
    log_root = pathlib.Path("/tmp/log")
    data_root.mkdir(parents=True, exist_ok=True)
    log_root.mkdir(parents=True, exist_ok=True)
    pc = PathConfig(
        project_name="projC",
        data_dir=str(data_root),
        log_dir=str(log_root),
        subproject=None
    )
    with pytest.raises(ValueError):
        pc.sub_project_dir()
    with pytest.raises(ValueError):
        pc.sub_project_log_dir()
    print_green("test_no_subproject_raises passed.")
    # Cleanup
    shutil.rmtree(data_root, ignore_errors=True)
    shutil.rmtree(log_root, ignore_errors=True)

def test_env_var(monkeypatch, tmp_path):
    print_green("Running test_env_var...")
    data_env = pathlib.Path("/tmp/data_env")
    log_env = pathlib.Path("/tmp/log_env")
    data_env.mkdir(parents=True, exist_ok=True)
    log_env.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("DATA_DIR", str(data_env))
    monkeypatch.setenv("LOG_DIR", str(log_env))
    pc = PathConfig(
        project_name="projD",
        data_dir=None,
        log_dir=None,
        subproject="subD"
    )
    assert pc.data_dir() == data_env.resolve()
    assert pc.project_dir() == (data_env / "projD").resolve()
    assert pc.sub_project_dir() == (data_env / "projD" / "subD").resolve()
    assert pc.log_dir() == log_env.resolve()
    assert pc.project_log_dir() == (log_env / "projD").resolve()
    assert pc.sub_project_log_dir() == (log_env / "projD" / "subD").resolve()
    print_green("test_env_var passed.")
    # Cleanup
    shutil.rmtree(data_env, ignore_errors=True)
    shutil.rmtree(log_env, ignore_errors=True)

def test_get_env_var(monkeypatch):
    print_green("Running test_get_env_var...")
    monkeypatch.setenv("FOO_BAR", "baz")
    assert PathConfig.get_env_var("FOO_BAR") == "baz"
    assert PathConfig.get_env_var("NOT_SET", "default") == "default"
    print_green("test_get_env_var passed.")
