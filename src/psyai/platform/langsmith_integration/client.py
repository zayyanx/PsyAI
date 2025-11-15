"""
LangSmith client wrapper for observability and evaluation.

This module provides a centralized client for LangSmith operations including
tracing, dataset management, and evaluation.
"""

from typing import Any, Dict, List, Optional

from langsmith import Client

from psyai.core.config import settings
from psyai.core.exceptions import ExternalServiceError
from psyai.core.logging import get_logger

logger = get_logger(__name__)


class LangSmithClient:
    """
    Wrapper for LangSmith client with error handling.

    This class provides a centralized interface for LangSmith operations
    including tracing, datasets, and evaluations.

    Example:
        >>> client = LangSmithClient()
        >>> client.create_dataset("my-dataset", "Test dataset")
        >>> run = client.create_run(name="test-run", inputs={"query": "test"})
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        project_name: Optional[str] = None,
        endpoint: Optional[str] = None,
    ):
        """
        Initialize LangSmith client.

        Args:
            api_key: LangSmith API key (defaults to settings)
            project_name: Project name (defaults to settings)
            endpoint: API endpoint (defaults to settings)
        """
        self.api_key = api_key or settings.langsmith_api_key
        self.project_name = project_name or settings.langsmith_project
        self.endpoint = endpoint or settings.langsmith_endpoint

        if not self.api_key:
            logger.warning("langsmith_api_key_not_set")

        self._client = self._create_client()

        logger.info(
            "langsmith_client_initialized",
            project=self.project_name,
            endpoint=self.endpoint,
        )

    def _create_client(self) -> Client:
        """
        Create LangSmith client instance.

        Returns:
            LangSmith Client instance

        Raises:
            ExternalServiceError: If client creation fails
        """
        try:
            client = Client(
                api_key=self.api_key,
                api_url=self.endpoint,
            )
            return client
        except Exception as e:
            logger.error("langsmith_client_creation_failed", error=str(e))
            raise ExternalServiceError(
                "LangSmith",
                f"Failed to create LangSmith client: {str(e)}",
            )

    @property
    def client(self) -> Client:
        """Get the underlying LangSmith client."""
        return self._client

    def create_dataset(
        self,
        dataset_name: str,
        description: Optional[str] = None,
        data_type: str = "kv",
    ) -> Dict[str, Any]:
        """
        Create a new dataset.

        Args:
            dataset_name: Name of the dataset
            description: Optional description
            data_type: Type of data ("kv" or "llm")

        Returns:
            Dataset information

        Raises:
            ExternalServiceError: If dataset creation fails

        Example:
            >>> dataset = client.create_dataset(
            ...     "evals-dataset",
            ...     "Dataset for evaluations"
            ... )
        """
        try:
            logger.debug("creating_dataset", name=dataset_name)

            dataset = self._client.create_dataset(
                dataset_name=dataset_name,
                description=description,
                data_type=data_type,
            )

            logger.info("dataset_created", name=dataset_name, id=str(dataset.id))

            return {
                "id": str(dataset.id),
                "name": dataset.name,
                "description": dataset.description,
                "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
            }

        except Exception as e:
            logger.error("dataset_creation_failed", error=str(e))
            raise ExternalServiceError(
                "LangSmith",
                f"Failed to create dataset: {str(e)}",
            )

    def get_dataset(self, dataset_name: str) -> Optional[Dict[str, Any]]:
        """
        Get dataset by name.

        Args:
            dataset_name: Name of the dataset

        Returns:
            Dataset information or None if not found

        Example:
            >>> dataset = client.get_dataset("evals-dataset")
        """
        try:
            dataset = self._client.read_dataset(dataset_name=dataset_name)

            return {
                "id": str(dataset.id),
                "name": dataset.name,
                "description": dataset.description,
                "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
            }

        except Exception as e:
            logger.warning("dataset_not_found", name=dataset_name, error=str(e))
            return None

    def create_example(
        self,
        dataset_name: str,
        inputs: Dict[str, Any],
        outputs: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create an example in a dataset.

        Args:
            dataset_name: Name of the dataset
            inputs: Input data
            outputs: Expected output data
            metadata: Optional metadata

        Returns:
            Example information

        Raises:
            ExternalServiceError: If example creation fails

        Example:
            >>> example = client.create_example(
            ...     "evals-dataset",
            ...     inputs={"query": "What is PsyAI?"},
            ...     outputs={"answer": "PsyAI is..."}
            ... )
        """
        try:
            logger.debug("creating_example", dataset=dataset_name)

            example = self._client.create_example(
                dataset_name=dataset_name,
                inputs=inputs,
                outputs=outputs,
                metadata=metadata,
            )

            logger.info("example_created", dataset=dataset_name, id=str(example.id))

            return {
                "id": str(example.id),
                "dataset_id": str(example.dataset_id),
                "inputs": example.inputs,
                "outputs": example.outputs,
                "metadata": example.metadata,
            }

        except Exception as e:
            logger.error("example_creation_failed", error=str(e))
            raise ExternalServiceError(
                "LangSmith",
                f"Failed to create example: {str(e)}",
            )

    def list_datasets(self) -> List[Dict[str, Any]]:
        """
        List all datasets.

        Returns:
            List of dataset information

        Example:
            >>> datasets = client.list_datasets()
            >>> for dataset in datasets:
            ...     print(dataset["name"])
        """
        try:
            datasets = list(self._client.list_datasets())

            return [
                {
                    "id": str(d.id),
                    "name": d.name,
                    "description": d.description,
                    "created_at": d.created_at.isoformat() if d.created_at else None,
                }
                for d in datasets
            ]

        except Exception as e:
            logger.error("list_datasets_failed", error=str(e))
            return []

    def delete_dataset(self, dataset_name: str) -> bool:
        """
        Delete a dataset.

        Args:
            dataset_name: Name of the dataset to delete

        Returns:
            True if successful, False otherwise

        Example:
            >>> client.delete_dataset("old-dataset")
        """
        try:
            self._client.delete_dataset(dataset_name=dataset_name)
            logger.info("dataset_deleted", name=dataset_name)
            return True

        except Exception as e:
            logger.error("dataset_deletion_failed", name=dataset_name, error=str(e))
            return False

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a run by ID.

        Args:
            run_id: Run ID

        Returns:
            Run information or None if not found

        Example:
            >>> run = client.get_run("run-id-123")
        """
        try:
            run = self._client.read_run(run_id=run_id)

            return {
                "id": str(run.id),
                "name": run.name,
                "inputs": run.inputs,
                "outputs": run.outputs,
                "error": run.error,
                "start_time": run.start_time.isoformat() if run.start_time else None,
                "end_time": run.end_time.isoformat() if run.end_time else None,
            }

        except Exception as e:
            logger.warning("run_not_found", run_id=run_id, error=str(e))
            return None


# Singleton instance
_langsmith_client: Optional[LangSmithClient] = None


def get_langsmith_client(
    api_key: Optional[str] = None,
    project_name: Optional[str] = None,
    force_new: bool = False,
) -> LangSmithClient:
    """
    Get or create a LangSmith client instance.

    By default, returns a singleton instance. Set force_new=True to create a new instance.

    Args:
        api_key: Optional API key override
        project_name: Optional project name override
        force_new: Force creation of new instance

    Returns:
        LangSmithClient instance

    Example:
        >>> client = get_langsmith_client()
        >>> dataset = client.create_dataset("my-dataset")
    """
    global _langsmith_client

    if force_new or _langsmith_client is None:
        _langsmith_client = LangSmithClient(
            api_key=api_key,
            project_name=project_name,
        )

    return _langsmith_client
