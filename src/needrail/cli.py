"""NeedRail CLI."""
from __future__ import annotations

import typer
from rich import print as rprint

app = typer.Typer(name="needrail-cli", help="NeedRail — agent-native needs coordination")


@app.command()
def version() -> None:
    rprint("[bold]NeedRail[/bold] 0.1.0")


@app.command()
def status() -> None:
    rprint({"service": "needrail", "version": "0.1.0", "mcp": True, "api": True, "sdk": True})


@app.command("list-needs")
def list_needs() -> None:
    rprint({"needs": [], "mode": "mock"})


def main() -> None:
    app()


if __name__ == "__main__":
    main()
