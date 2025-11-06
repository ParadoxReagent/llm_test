"""
Analytics and comparison statistics for model responses.
"""

from typing import List, Optional

from .types import ModelResponse


class ComparisonAnalytics:
    """Analyze and provide statistics for model comparison results."""

    def __init__(self, results: List[ModelResponse]):
        """
        Initialize analytics with results.

        Args:
            results: List of model responses
        """
        self.results = results

    def get_fastest_model(self) -> Optional[str]:
        """
        Get the model with the fastest response time.

        Returns:
            Model name or None if no successful responses
        """
        successful_results = [
            r for r in self.results if r["response_time"] is not None and not r["error"]
        ]
        if not successful_results:
            return None

        fastest = min(successful_results, key=lambda r: r["response_time"])  # type: ignore
        return fastest["model"]

    def get_slowest_model(self) -> Optional[str]:
        """
        Get the model with the slowest response time.

        Returns:
            Model name or None if no successful responses
        """
        successful_results = [
            r for r in self.results if r["response_time"] is not None and not r["error"]
        ]
        if not successful_results:
            return None

        slowest = max(successful_results, key=lambda r: r["response_time"])  # type: ignore
        return slowest["model"]

    def get_average_response_time(self) -> Optional[float]:
        """
        Get average response time across all successful models.

        Returns:
            Average response time in seconds or None
        """
        times = [
            r["response_time"]
            for r in self.results
            if r["response_time"] is not None and not r["error"]
        ]
        if not times:
            return None

        return sum(times) / len(times)

    def get_most_token_efficient(self) -> Optional[str]:
        """
        Get the model that used the fewest total tokens.

        Returns:
            Model name or None
        """
        successful_results = [
            r for r in self.results if r["total_tokens"] is not None and not r["error"]
        ]
        if not successful_results:
            return None

        most_efficient = min(successful_results, key=lambda r: r["total_tokens"])  # type: ignore
        return most_efficient["model"]

    def get_least_expensive(self) -> Optional[str]:
        """
        Get the model with the lowest estimated cost.

        Returns:
            Model name or None
        """
        successful_results = [
            r for r in self.results if r["estimated_cost"] is not None and not r["error"]
        ]
        if not successful_results:
            return None

        cheapest = min(successful_results, key=lambda r: r["estimated_cost"])  # type: ignore
        return cheapest["model"]

    def get_total_cost(self) -> Optional[float]:
        """
        Get total estimated cost across all models.

        Returns:
            Total cost in USD or None
        """
        costs = [
            r["estimated_cost"]
            for r in self.results
            if r["estimated_cost"] is not None and not r["error"]
        ]
        if not costs:
            return None

        return sum(costs)

    def get_success_rate(self) -> float:
        """
        Get percentage of successful responses.

        Returns:
            Success rate as percentage (0-100)
        """
        if not self.results:
            return 0.0

        successful = sum(1 for r in self.results if not r["error"])
        return (successful / len(self.results)) * 100

    def get_summary(self) -> str:
        """
        Get a formatted summary of the analytics.

        Returns:
            Formatted summary string
        """
        lines = ["\n📊 Comparison Analytics:", "─" * 80]

        # Success rate
        success_rate = self.get_success_rate()
        lines.append(f"Success Rate: {success_rate:.1f}% ({sum(1 for r in self.results if not r['error'])}/{len(self.results)} models)")

        # Response times
        avg_time = self.get_average_response_time()
        if avg_time:
            lines.append(f"Average Response Time: {avg_time:.2f}s")

        fastest = self.get_fastest_model()
        if fastest:
            fastest_time = next(
                r["response_time"] for r in self.results if r["model"] == fastest
            )
            lines.append(f"⚡ Fastest Model: {fastest} ({fastest_time:.2f}s)")

        slowest = self.get_slowest_model()
        if slowest:
            slowest_time = next(
                r["response_time"] for r in self.results if r["model"] == slowest
            )
            lines.append(f"🐌 Slowest Model: {slowest} ({slowest_time:.2f}s)")

        # Token efficiency
        most_efficient = self.get_most_token_efficient()
        if most_efficient:
            efficient_tokens = next(
                r["total_tokens"] for r in self.results if r["model"] == most_efficient
            )
            lines.append(f"📝 Most Token Efficient: {most_efficient} ({efficient_tokens} tokens)")

        # Cost analysis
        total_cost = self.get_total_cost()
        if total_cost is not None:
            lines.append(f"💰 Total Cost: ${total_cost:.6f}")

        cheapest = self.get_least_expensive()
        if cheapest:
            cheapest_cost = next(
                r["estimated_cost"] for r in self.results if r["model"] == cheapest
            )
            lines.append(f"💵 Cheapest Model: {cheapest} (${cheapest_cost:.6f})")

        lines.append("─" * 80)
        return "\n".join(lines)
