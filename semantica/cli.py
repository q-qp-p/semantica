"""
Semantica CLI Entry Point

This module provides the command-line interface for the Semantica framework,
enabling users to interact with the framework via terminal commands.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Sequence

import yaml

import click
from rich.console import Console
from rich.table import Table

from . import __version__
from .core.config_manager import Config, ConfigManager
from .utils.exceptions import SemanticaError
from .utils.logging import setup_logging

if TYPE_CHECKING:
    from .core.orchestrator import Semantica

console = Console()


@dataclass
class CLIContext:
    """Shared runtime context for all CLI commands."""

    config_path: Optional[str]
    config: Config
    log_level: str
    log_level_override: Optional[str] = None
    framework: Optional["Semantica"] = None


def _run_with_error_handling(action: Callable[[], None]) -> None:
    """Run a CLI action with consistent user-facing error formatting."""
    try:
        action()
    except click.ClickException:
        raise
    except SemanticaError as exc:
        raise click.ClickException(str(exc)) from exc
    except Exception as exc:  # pragma: no cover - fallback guard
        raise click.ClickException(f"Unexpected error: {exc}") from exc


def _load_config_data(file_path: Path) -> Dict[str, Any]:
    """Load and validate raw YAML/JSON config data."""
    suffix = file_path.suffix.lower()
    try:
        if suffix in (".yaml", ".yml"):
            with file_path.open("r", encoding="utf-8") as handle:
                config_data = yaml.safe_load(handle)
        elif suffix == ".json":
            with file_path.open("r", encoding="utf-8") as handle:
                config_data = json.load(handle)
        else:
            raise click.ClickException(
                "Unsupported configuration file format: "
                f"{suffix}. Supported formats: .yaml, .yml, .json"
            )
    except (json.JSONDecodeError, yaml.YAMLError, UnicodeDecodeError) as exc:
        raise click.ClickException(
            f"Failed to parse configuration file '{file_path}': {exc}"
        ) from exc

    if not isinstance(config_data, dict):
        raise click.ClickException(
            "Configuration file must contain a mapping/object at the root."
        )

    return config_data


def _build_runtime_config(
    config_path: Optional[str],
    log_level: Optional[str],
) -> Config:
    """Resolve CLI config from file plus global flag overrides."""
    config_manager = ConfigManager()

    if config_path:
        config_data = _load_config_data(Path(config_path))
    else:
        config_data = {}

    if log_level:
        config_data.setdefault("logging", {})["level"] = log_level.upper()

    # Keep validation disabled at CLI bootstrap to avoid blocking unrelated commands.
    return config_manager.load_from_dict(config_data, validate=False)


def _get_framework(cli_ctx: CLIContext) -> "Semantica":
    """Lazily initialize framework only when a command needs it."""
    if cli_ctx.framework is None:
        from .core.orchestrator import Semantica

        cli_ctx.framework = Semantica(config=cli_ctx.config.to_dict())
    return cli_ctx.framework


def _run_build(cli_ctx: CLIContext, sources: Sequence[str]) -> None:
    """Thin wrapper around existing build orchestration flow."""
    if not sources:
        raise click.UsageError(
            "At least one source is required. Use --source/-s one or more times."
        )

    framework = _get_framework(cli_ctx)
    console.print(f"Initializing Semantica with {len(sources)} sources...")
    result = framework.build_knowledge_base(sources=list(sources))

    stats = result.get("statistics", {}) if isinstance(result, dict) else {}
    processed = stats.get("sources_processed")
    if processed is not None:
        console.print(
            "[bold green]Success:[/bold green] Knowledge base build completed "
            f"for {processed} source(s)."
        )
    else:
        console.print(
            "[bold green]Success:[/bold green] Knowledge base build completed."
        )


def _run_build_command(
    cli_ctx: CLIContext,
    source: Sequence[str],
    command_config_path: Optional[str],
) -> None:
    """Execute build command path with optional command-level config override."""
    if command_config_path:
        command_ctx = CLIContext(
            config_path=command_config_path,
            config=_build_runtime_config(
                command_config_path, cli_ctx.log_level_override
            ),
            log_level=cli_ctx.log_level,
        )
        _run_build(command_ctx, source)
    else:
        _run_build(cli_ctx, source)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__)
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=str),
    default=None,
    help="Path to YAML/JSON config file.",
)
@click.option(
    "--log-level",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        case_sensitive=False,
    ),
    default=None,
    help="Override logging level for this CLI invocation.",
)
@click.pass_context
def main(ctx: click.Context, config_path: Optional[str], log_level: Optional[str]):
    """Semantica - Semantic Layer & Knowledge Engineering Framework"""
    try:
        config = _build_runtime_config(config_path=config_path, log_level=log_level)
        setup_logging(config=config.get("logging", {}))
        effective_log_level = config.get("logging.level", "INFO")
        ctx.obj = CLIContext(
            config_path=config_path,
            config=config,
            log_level=effective_log_level,
            log_level_override=log_level.upper() if log_level else None,
        )
    except click.ClickException:
        raise
    except SemanticaError as exc:
        raise click.ClickException(str(exc)) from exc
    except Exception as exc:
        raise click.ClickException(f"Failed to initialize CLI: {exc}") from exc


@main.group(invoke_without_command=True)
@click.pass_context
def kg(ctx: click.Context) -> None:
    """Knowledge graph and semantic build commands."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.group(invoke_without_command=True)
@click.pass_context
def pipeline(ctx: click.Context) -> None:
    """Pipeline command group (foundation placeholder)."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.group(invoke_without_command=True)
@click.pass_context
def serve(ctx: click.Context) -> None:
    """Service command group (foundation placeholder)."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.group(name="config", invoke_without_command=True)
@click.pass_context
def config_group(ctx: click.Context) -> None:
    """Configuration command group."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.pass_obj
def info(cli_ctx: CLIContext):
    """Display information about Semantica."""

    def _action() -> None:
        console.print(f"[bold blue]Semantica Framework[/bold blue] v{__version__}")
        console.print(
            "A comprehensive Python framework for transforming unstructured data "
            "into semantic layers."
        )

        table = Table(title="Framework Components")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")

        table.add_row("Core Orchestrator", "Active")
        table.add_row("Knowledge Graph Engine", "Active")
        table.add_row("Pipeline Execution", "Active")
        table.add_row("Vector Store Integration", "Active")
        table.add_row("CLI Config File", cli_ctx.config_path or "(none)")
        table.add_row("CLI Log Level", cli_ctx.log_level)

        console.print(table)

    _run_with_error_handling(_action)


@kg.command("build")
@click.option("--source", "-s", multiple=True, help="Data sources to process.")
@click.option(
    "-c",
    "--config",
    "command_config_path",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=str),
    default=None,
    help="Path to YAML/JSON config file.",
)
@click.pass_obj
def kg_build(
    cli_ctx: CLIContext,
    source: Sequence[str],
    command_config_path: Optional[str],
):
    """Build a knowledge base from sources."""

    def _action() -> None:
        _run_build_command(cli_ctx, source, command_config_path)

    _run_with_error_handling(_action)


@main.command("build", hidden=True)
@click.option("--source", "-s", multiple=True, help="Data sources to process.")
@click.option(
    "-c",
    "--config",
    "command_config_path",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=str),
    default=None,
    help="Path to YAML/JSON config file.",
)
@click.pass_obj
def build_alias(
    cli_ctx: CLIContext,
    source: Sequence[str],
    command_config_path: Optional[str],
):
    """Backward-compatible alias for 'kg build'."""

    def _action() -> None:
        _run_build_command(cli_ctx, source, command_config_path)

    _run_with_error_handling(_action)


if __name__ == "__main__":
    main()
