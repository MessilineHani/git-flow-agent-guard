"""Tests for git-flow-agent-guard shared utilities."""
import os
import sys
import tempfile
import shutil
from pathlib import Path
import pytest

# Add scripts/lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "lib"))

from guard import (
    run_cmd, ensure_log_dir, load_config, get_git_diff_stat, get_changed_files,
    calculate_revert_cost, calculate_risk_scores, calculate_blast_radius,
    auto_merge_allowed, write_log, run_verification_commands
)


class TestCalculateRiskScores:
    """Tests for risk score calculation."""

    def test_low_risk_few_files(self):
        dev_risk, main_risk = calculate_risk_scores(1)
        assert dev_risk == 1
        assert main_risk == 2

    def test_medium_risk(self):
        dev_risk, main_risk = calculate_risk_scores(6)
        assert dev_risk == 3
        assert main_risk == 4

    def test_high_risk_many_files(self):
        dev_risk, main_risk = calculate_risk_scores(15)
        assert dev_risk == 5
        assert main_risk == 5  # capped at 5

    def test_risk_bounds(self):
        # Test lower bound
        dev_risk, _ = calculate_risk_scores(0)
        assert dev_risk == 1

        # Test upper bound
        dev_risk, main_risk = calculate_risk_scores(100)
        assert dev_risk == 5
        assert main_risk == 5


class TestCalculateBlastRadius:
    """Tests for blast radius calculation."""

    def test_low_blast_radius(self):
        assert calculate_blast_radius(1) == "LOW"
        assert calculate_blast_radius(4) == "LOW"

    def test_medium_blast_radius(self):
        assert calculate_blast_radius(5) == "MEDIUM"
        assert calculate_blast_radius(10) == "MEDIUM"

    def test_high_blast_radius(self):
        assert calculate_blast_radius(11) == "HIGH"
        assert calculate_blast_radius(50) == "HIGH"


class TestAutoMergeAllowed:
    """Tests for auto-merge decision matrix."""

    def test_dev_risk_1_3_allows_merge(self):
        for risk in [1, 2, 3]:
            assert auto_merge_allowed(risk, "HIGH", "HIGH", "dev") is True

    def test_dev_risk_4_low_blast_low_revert_allows(self):
        assert auto_merge_allowed(4, "LOW", "LOW", "dev") is True

    def test_dev_risk_4_medium_blast_blocks(self):
        assert auto_merge_allowed(4, "MEDIUM", "LOW", "dev") is False

    def test_dev_risk_4_high_revert_blocks(self):
        assert auto_merge_allowed(4, "LOW", "HIGH", "dev") is False

    def test_dev_risk_5_always_blocks(self):
        assert auto_merge_allowed(5, "LOW", "LOW", "dev") is False

    def test_main_branch_never_allows(self):
        assert auto_merge_allowed(1, "LOW", "LOW", "main") is False
        assert auto_merge_allowed(2, "LOW", "LOW", "main") is False


class TestCalculateRevertCost:
    """Tests for revert cost calculation from file patterns."""

    def test_high_cost_migrations(self):
        config = {
            "risk": {
                "revert_cost_patterns": {
                    "HIGH": ["migration", "*.sql", "*.prisma"],
                    "MEDIUM": []
                }
            }
        }
        assert calculate_revert_cost(["db/migration_001.sql"], config) == "HIGH"
        assert calculate_revert_cost(["schema.prisma"], config) == "HIGH"

    def test_medium_cost_configs(self):
        config = {
            "risk": {
                "revert_cost_patterns": {
                    "HIGH": [],
                    "MEDIUM": ["config*", "*.yaml", "*.yml"]
                }
            }
        }
        assert calculate_revert_cost(["config.yaml"], config) == "MEDIUM"
        assert calculate_revert_cost(["settings.yml"], config) == "MEDIUM"

    def test_low_cost_default(self):
        config = {
            "risk": {
                "revert_cost_patterns": {
                    "HIGH": [],
                    "MEDIUM": []
                }
            }
        }
        assert calculate_revert_cost(["src/main.py"], config) == "LOW"
        assert calculate_revert_cost([], config) == "LOW"

    def test_high_priority_over_medium(self):
        config = {
            "risk": {
                "revert_cost_patterns": {
                    "HIGH": ["*.sql"],
                    "MEDIUM": ["*.sql"]  # Same pattern in both
                }
            }
        }
        assert calculate_revert_cost(["data.sql"], config) == "HIGH"


class TestRunCmd:
    """Tests for run_cmd utility."""

    def test_success(self):
        result = run_cmd("echo hello")
        assert result == "hello"

    def test_failure_raises(self):
        with pytest.raises(RuntimeError):
            run_cmd("exit 1")


class TestEnsureLogDir:
    """Tests for log directory creation."""

    def test_creates_dir(self, tmp_path):
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            log_dir = ensure_log_dir()
            assert log_dir.exists()
            assert log_dir.name == "logs"
            assert log_dir.parent.name == ".agent-guard"
        finally:
            os.chdir(original_cwd)


class TestWriteLog:
    """Tests for log writing."""

    def test_writes_file(self, tmp_path):
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            log_dir = ensure_log_dir()
            path = write_log(log_dir, "TEST.md", "# Test\n\nContent")
            assert path.exists()
            content = path.read_text()
            assert "# Test" in content
            assert "Content" in content
        finally:
            os.chdir(original_cwd)


class TestLoadConfig:
    """Tests for config loading."""

    def test_loads_existing(self, tmp_path):
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            config_data = {"test": "value", "num": 42}
            import json
            with open(".agent-guard.json", "w") as f:
                json.dump(config_data, f)
            loaded = load_config()
            assert loaded == config_data
        finally:
            os.chdir(original_cwd)

    def test_returns_empty_for_missing(self, tmp_path):
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            loaded = load_config()
            assert loaded == {}
        finally:
            os.chdir(original_cwd)


class TestRunVerificationCommands:
    """Tests for verification command execution."""

    def test_all_pass(self, tmp_path):
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            config = {
                "verification": {
                    "lint_command": "echo lint",
                    "typecheck_command": "echo typecheck",
                    "test_command": "echo test",
                    "build_command": "echo build"
                }
            }
            results = run_verification_commands(config)
            assert all(results.values())
            assert results["lint_command"] is True
        finally:
            os.chdir(original_cwd)

    def test_failure_blocks(self, tmp_path):
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            config = {
                "verification": {
                    "lint_command": "exit 1",
                    "test_command": "echo test"
                }
            }
            results = run_verification_commands(config)
            assert results["lint_command"] is False
            assert results["test_command"] is True
        finally:
            os.chdir(original_cwd)

    def test_empty_command_skips(self, tmp_path):
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            config = {
                "verification": {
                    "lint_command": "",
                    "test_command": "echo test"
                }
            }
            results = run_verification_commands(config)
            assert results["lint_command"] is True  # Skipped
            assert results["test_command"] is True
        finally:
            os.chdir(original_cwd)