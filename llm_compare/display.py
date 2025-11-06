"""
Display and formatting utilities using rich library.
"""

from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

from .cost_tracker import format_cost
from .types import ModelResponse

console = Console()


class DisplayManager:
    """Manages display and formatting of results."""

    def __init__(self):
        """Initialize display manager."""
        self.console = console

    def print_header(
        self, prompt: str, system_prompt: Optional[str] = None, model_count: int = 1
    ) -> None:
        """
        Print comparison header.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model_count: Number of models being compared
        """
        self.console.print("\n" + "=" * 80)
        self.console.print(f"[bold cyan]Prompt:[/bold cyan] {prompt}")
        if system_prompt:
            self.console.print(f"[bold cyan]System Prompt:[/bold cyan] {system_prompt}")
        self.console.print("=" * 80 + "\n")
        self.console.print(
            f"[bold]Querying {model_count} model{'s' if model_count > 1 else ''} in parallel...[/bold]\n"
        )

    def create_progress_bar(self, total: int) -> Progress:
        """
        Create a progress bar for tracking model responses.

        Args:
            total: Total number of tasks

        Returns:
            Progress instance
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
        )

    def display_results(self, results: List[ModelResponse]) -> None:
        """
        Display comparison results in a formatted manner.

        Args:
            results: List of model responses
        """
        self.console.print(f"\n{'=' * 80}")
        self.console.print("[bold green]RESULTS[/bold green]")
        self.console.print(f"{'=' * 80}\n")

        for i, result in enumerate(results, 1):
            self._display_single_result(i, result)

    def _display_single_result(self, index: int, result: ModelResponse) -> None:
        """
        Display a single model result.

        Args:
            index: Result index
            result: Model response
        """
        self.console.print(f"\n{'─' * 80}")
        self.console.print(f"[bold]Model {index}:[/bold] [cyan]{result['model']}[/cyan]")

        # Display performance metrics
        metrics = []
        if result.get("response_time") is not None:
            metrics.append(f"Time: {result['response_time']:.2f}s")
        if result.get("total_tokens") is not None:
            metrics.append(
                f"Tokens: {result['total_tokens']} "
                f"(prompt: {result.get('prompt_tokens', 'N/A')}, "
                f"completion: {result.get('completion_tokens', 'N/A')})"
            )
        if result.get("estimated_cost") is not None:
            cost_str = format_cost(result["estimated_cost"])
            metrics.append(f"Cost: {cost_str}")

        if metrics:
            self.console.print(f"[dim]📊 {' | '.join(metrics)}[/dim]")
        self.console.print(f"{'─' * 80}")

        if result["error"]:
            self.console.print(f"\n[red]❌ Error: {result['error']}[/red]\n")
        else:
            self.console.print(f"\n{result['response']}\n")

    def display_progress_update(
        self, completed: int, total: int, model: str, success: bool, details: str = ""
    ) -> None:
        """
        Display progress update for a single model.

        Args:
            completed: Number of completed models
            total: Total number of models
            model: Model name
            success: Whether the request was successful
            details: Additional details (time, tokens, etc.)
        """
        status_icon = "✓" if success else "❌"
        status_color = "green" if success else "red"

        self.console.print(
            f"[{status_color}][{completed}/{total}] {model}: {status_icon}[/{status_color}] {details}"
        )

    def display_streaming_header(self, model: str) -> None:
        """
        Display header for streaming response.

        Args:
            model: Model name
        """
        self.console.print(f"\n{'─' * 80}")
        self.console.print(f"[bold cyan]Streaming from:[/bold cyan] {model}")
        self.console.print(f"{'─' * 80}\n")

    def display_streaming_chunk(self, chunk: str) -> None:
        """
        Display a streaming chunk.

        Args:
            chunk: Text chunk
        """
        self.console.print(chunk, end="")

    def display_comparison_table(self, results: List[ModelResponse]) -> None:
        """
        Display results in a table format.

        Args:
            results: List of model responses
        """
        table = Table(title="Model Comparison Summary", show_header=True, header_style="bold cyan")
        table.add_column("Model", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column("Time (s)", justify="right")
        table.add_column("Tokens", justify="right")
        table.add_column("Cost", justify="right")

        for result in results:
            status = "✓" if not result["error"] else "❌"
            time_str = (
                f"{result['response_time']:.2f}" if result["response_time"] else "N/A"
            )
            tokens_str = str(result["total_tokens"]) if result["total_tokens"] else "N/A"
            cost_str = format_cost(result.get("estimated_cost"))

            status_style = "green" if not result["error"] else "red"

            table.add_row(
                result["model"],
                Text(status, style=status_style),
                time_str,
                tokens_str,
                cost_str,
            )

        self.console.print("\n")
        self.console.print(table)
        self.console.print("\n")

    def display_error(self, message: str) -> None:
        """
        Display an error message.

        Args:
            message: Error message
        """
        self.console.print(f"[red]{message}[/red]")

    def display_info(self, message: str) -> None:
        """
        Display an info message.

        Args:
            message: Info message
        """
        self.console.print(f"[blue]{message}[/blue]")

    def display_success(self, message: str) -> None:
        """
        Display a success message.

        Args:
            message: Success message
        """
        self.console.print(f"[green]{message}[/green]")

    def display_welcome(self, models: List[str], system_prompt: Optional[str] = None) -> None:
        """
        Display welcome message for interactive mode.

        Args:
            models: List of models
            system_prompt: Optional system prompt
        """
        welcome_text = f"""
[bold cyan]🤖 LLM Model Comparison Tool[/bold cyan]

[bold]Comparing models:[/bold]
{chr(10).join(f"  • {model}" for model in models)}

{f'[bold]System prompt:[/bold] {system_prompt}' if system_prompt else ''}

[dim]Enter your prompts (or 'quit' to exit)[/dim]
        """
        self.console.print(Panel(welcome_text, border_style="cyan"))
