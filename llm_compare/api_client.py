"""
Async API client for LLM interactions with retry logic and connection pooling.
"""

import asyncio
import time
from typing import AsyncIterator, List, Optional

from litellm import acompletion
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .cost_tracker import estimate_cost
from .types import ModelResponse
from .validators import validate_prompt


class LLMAPIClient:
    """Async API client for interacting with LLM models."""

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: int = 120,
    ):
        """
        Initialize API client.

        Args:
            max_retries: Maximum number of retries for failed requests
            retry_delay: Base delay for exponential backoff (in seconds)
            timeout: Request timeout in seconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout

    async def get_model_response(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        stream: bool = False,
    ) -> ModelResponse:
        """
        Get response from a specific model with timing and token counting.

        Args:
            model: Model identifier
            prompt: User prompt
            temperature: Response temperature (0-1)
            system_prompt: Optional system prompt to prepend
            stream: Whether to stream the response

        Returns:
            Model response with metrics and optional cost estimation
        """
        try:
            start_time = time.time()

            # Build messages list
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # Use retry decorator logic
            response = await self._call_llm_with_retry(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=stream,
            )

            if stream:
                # For streaming, we accumulate the response
                full_response = ""
                async for chunk in response:
                    if hasattr(chunk.choices[0], "delta") and hasattr(
                        chunk.choices[0].delta, "content"
                    ):
                        content = chunk.choices[0].delta.content
                        if content:
                            full_response += content

                end_time = time.time()
                response_time = end_time - start_time

                # For streaming, we don't get usage data in the chunks
                # This is a limitation of streaming responses
                return ModelResponse(
                    model=model,
                    response=full_response,
                    error=None,
                    response_time=response_time,
                    prompt_tokens=None,
                    completion_tokens=None,
                    total_tokens=None,
                    estimated_cost=None,
                )
            else:
                end_time = time.time()
                response_time = end_time - start_time

                # Extract token usage if available
                usage = response.usage if hasattr(response, "usage") else None
                prompt_tokens = usage.prompt_tokens if usage else None
                completion_tokens = usage.completion_tokens if usage else None
                total_tokens = usage.total_tokens if usage else None

                # Estimate cost
                estimated_cost = estimate_cost(model, prompt_tokens, completion_tokens)

                return ModelResponse(
                    model=model,
                    response=response.choices[0].message.content,
                    error=None,
                    response_time=response_time,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    estimated_cost=estimated_cost,
                )

        except Exception as e:
            return ModelResponse(
                model=model,
                response=None,
                error=str(e),
                response_time=None,
                prompt_tokens=None,
                completion_tokens=None,
                total_tokens=None,
                estimated_cost=None,
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True,
    )
    async def _call_llm_with_retry(
        self,
        model: str,
        messages: List[dict],
        temperature: float,
        stream: bool,
    ):
        """
        Call LLM API with retry logic.

        Args:
            model: Model identifier
            messages: List of message dicts
            temperature: Temperature parameter
            stream: Whether to stream

        Returns:
            LLM response or async iterator for streaming
        """
        return await acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=stream,
            timeout=self.timeout,
        )

    async def get_streaming_response(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Get streaming response from a model.

        Args:
            model: Model identifier
            prompt: User prompt
            temperature: Response temperature
            system_prompt: Optional system prompt

        Yields:
            Response chunks as they arrive
        """
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self._call_llm_with_retry(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )

            async for chunk in response:
                if hasattr(chunk.choices[0], "delta") and hasattr(
                    chunk.choices[0].delta, "content"
                ):
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content

        except Exception as e:
            yield f"\n❌ Error: {str(e)}"

    async def compare_models(
        self,
        prompt: str,
        models: List[str],
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        stream: bool = False,
    ) -> List[ModelResponse]:
        """
        Compare responses from multiple models in parallel.

        Args:
            prompt: User prompt
            models: List of model identifiers
            temperature: Response temperature
            system_prompt: Optional system prompt for all models
            stream: Whether to stream responses (only works for single model)

        Returns:
            List of model responses
        """
        # Validate inputs
        validate_prompt(prompt, "prompt")
        if system_prompt:
            validate_prompt(system_prompt, "system_prompt")

        # Create tasks for all models
        tasks = [
            self.get_model_response(
                model=model,
                prompt=prompt,
                temperature=temperature,
                system_prompt=system_prompt,
                stream=stream,
            )
            for model in models
        ]

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=False)

        return list(results)
