import pytest
from click.testing import CliRunner

import semantica.cli as cli_module


@pytest.fixture
def runner():
    return CliRunner()


def test_root_help_shows_expected_groups(runner):
    result = runner.invoke(cli_module.main, ["--help"])

    assert result.exit_code == 0
    assert "Semantica - Semantic Layer & Knowledge Engineering Framework" in result.output
    assert "kg" in result.output
    assert "pipeline" in result.output
    assert "serve" in result.output


def test_kg_group_help_shows_build_command(runner):
    result = runner.invoke(cli_module.main, ["kg", "--help"])

    assert result.exit_code == 0
    assert "Knowledge graph and semantic build commands." in result.output
    assert "build" in result.output


def test_kg_build_help_shows_source_and_config_flags(runner):
    result = runner.invoke(cli_module.main, ["kg", "build", "--help"])

    assert result.exit_code == 0
    assert "--source" in result.output
    assert "-s" in result.output
    assert "--config" in result.output
    assert "-c" in result.output


@pytest.mark.parametrize(
    "argv",
    [
        ["kg", "build", "-s", "README.md"],
        ["build", "-s", "README.md"],
    ],
)
def test_build_paths_invoke_shared_wrapper(runner, monkeypatch, argv):
    captured = {}

    def fake_run_build(cli_ctx, sources):
        captured["config_path"] = cli_ctx.config_path
        captured["sources"] = list(sources)

    monkeypatch.setattr(cli_module, "_run_build", fake_run_build)

    result = runner.invoke(cli_module.main, argv)

    assert result.exit_code == 0
    assert captured["sources"] == ["README.md"]


@pytest.mark.parametrize(
    "argv",
    [
        ["kg", "build", "-s", "README.md", "-c", "cfg.yml"],
        ["kg", "build", "-s", "README.md", "--config", "cfg.yml"],
        ["build", "-s", "README.md", "-c", "cfg.yml"],
        ["build", "-s", "README.md", "--config", "cfg.yml"],
    ],
)
def test_build_config_short_and_long_flags_are_compatible(runner, monkeypatch, argv):
    captured = {}

    def fake_run_build(cli_ctx, sources):
        captured["config_path"] = cli_ctx.config_path
        captured["sources"] = list(sources)

    monkeypatch.setattr(cli_module, "_run_build", fake_run_build)

    with runner.isolated_filesystem():
        with open("cfg.yml", "w", encoding="utf-8") as handle:
            handle.write("logging:\n  level: INFO\n")

        result = runner.invoke(cli_module.main, argv)

    assert result.exit_code == 0
    assert captured["sources"] == ["README.md"]
    assert captured["config_path"] is not None


@pytest.mark.parametrize(
    "argv",
    [
        ["kg", "build"],
        ["build"],
    ],
)
def test_missing_input_errors_are_clean_and_click_safe(runner, argv):
    result = runner.invoke(cli_module.main, argv)

    assert result.exit_code != 0
    assert "At least one source is required" in result.output
    assert "Traceback" not in result.output


def test_invalid_root_config_error_is_clean_and_click_safe(runner):
    with runner.isolated_filesystem():
        with open("bad.md", "w", encoding="utf-8") as handle:
            handle.write("not-a-config")

        result = runner.invoke(cli_module.main, ["--config", "bad.md", "info"])

    assert result.exit_code != 0
    assert "Unsupported configuration file format" in result.output
    assert "Traceback" not in result.output


def test_invalid_command_config_error_is_clean_and_click_safe(runner):
    with runner.isolated_filesystem():
        with open("bad.md", "w", encoding="utf-8") as handle:
            handle.write("not-a-config")

        result = runner.invoke(
            cli_module.main,
            ["kg", "build", "-s", "README.md", "-c", "bad.md"],
        )

    assert result.exit_code != 0
    assert "Unsupported configuration file format" in result.output
    assert "Traceback" not in result.output


@pytest.mark.parametrize(
    "argv",
    [
        ["--help"],
        ["kg", "--help"],
        ["kg", "build", "--help"],
        ["build", "--help"],
    ],
)
def test_help_calls_do_not_initialize_framework(runner, monkeypatch, argv):
    def fail_get_framework(_):
        raise AssertionError("framework initialization must not happen on help")

    monkeypatch.setattr(cli_module, "_get_framework", fail_get_framework)

    result = runner.invoke(cli_module.main, argv)

    assert result.exit_code == 0


def test_runtime_errors_are_click_safe_without_traceback(runner, monkeypatch):
    def boom(_cli_ctx, _sources):
        raise RuntimeError("boom")

    monkeypatch.setattr(cli_module, "_run_build", boom)

    result = runner.invoke(cli_module.main, ["kg", "build", "-s", "README.md"])

    assert result.exit_code != 0
    assert "Unexpected error: boom" in result.output
    assert "Traceback" not in result.output
