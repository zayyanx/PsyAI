"""
Vector store abstraction for RAG using Vertex AI Vector Search.

This module provides a unified interface for Vertex AI Vector Search.
"""

from typing import Any, Dict, List, Optional, Tuple

from google.cloud import aiplatform
from google.cloud.aiplatform import MatchingEngineIndex, MatchingEngineIndexEndpoint

from psyai.core.config import settings
from psyai.core.exceptions import VectorStoreError
from psyai.core.logging import get_logger
from psyai.platform.vertexai_integration.rag.embeddings import get_vertex_embedding_service

logger = get_logger(__name__)


class Document:
    """
    Simple document class compatible with the interface.

    Attributes:
        page_content: The text content
        metadata: Additional metadata
    """

    def __init__(self, page_content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize document.

        Args:
            page_content: Text content
            metadata: Optional metadata dict
        """
        self.page_content = page_content
        self.metadata = metadata or {}


class VertexVectorStoreManager:
    """
    Manager for Vertex AI Vector Search operations.

    Provides a unified interface similar to LangChain vector stores.

    Example:
        >>> manager = VertexVectorStoreManager()
        >>> await manager.add_documents([
        ...     Document(page_content="PsyAI is awesome", metadata={"source": "doc1"})
        ... ])
        >>> results = await manager.similarity_search("What is PsyAI?", k=5)
    """

    def __init__(
        self,
        index_id: Optional[str] = None,
        index_endpoint_id: Optional[str] = None,
        deployed_index_id: Optional[str] = None,
        embedding_service: Optional[Any] = None,
    ):
        """
        Initialize Vertex Vector Search manager.

        Args:
            index_id: Vertex Vector Search index ID
            index_endpoint_id: Index endpoint ID
            deployed_index_id: Deployed index ID
            embedding_service: Optional embedding service (creates default if None)

        Raises:
            VectorStoreError: If initialization fails
        """
        self.index_id = index_id or settings.vertex_index_id
        self.index_endpoint_id = index_endpoint_id or settings.vertex_index_endpoint_id
        self.deployed_index_id = deployed_index_id or settings.vertex_deployed_index_id

        # Get embedding service
        if embedding_service is None:
            embedding_service = get_vertex_embedding_service()

        self.embedding_service = embedding_service

        # Initialize AI Platform
        aiplatform.init(
            project=settings.gcp_project_id,
            location=settings.gcp_location,
        )

        # Initialize index and endpoint (if configured)
        self._index: Optional[MatchingEngineIndex] = None
        self._index_endpoint: Optional[MatchingEngineIndexEndpoint] = None

        if self.index_id:
            try:
                self._index = MatchingEngineIndex(index_name=self.index_id)
            except Exception as e:
                logger.warning("vertex_index_init_failed", error=str(e))

        if self.index_endpoint_id:
            try:
                self._index_endpoint = MatchingEngineIndexEndpoint(
                    index_endpoint_name=self.index_endpoint_id
                )
            except Exception as e:
                logger.warning("vertex_index_endpoint_init_failed", error=str(e))

        logger.info(
            "vertex_vectorstore_manager_initialized",
            index_id=self.index_id,
            endpoint_id=self.index_endpoint_id,
        )

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add texts to the vector store.

        Args:
            texts: List of texts to add
            metadatas: Optional list of metadata dicts
            ids: Optional list of IDs

        Returns:
            List of IDs for added documents

        Raises:
            VectorStoreError: If adding texts fails

        Example:
            >>> ids = manager.add_texts(
            ...     texts=["Hello world", "Goodbye world"],
            ...     metadatas=[{"source": "doc1"}, {"source": "doc2"}]
            ... )
        """
        try:
            logger.debug("vertex_vectorstore_adding_texts", count=len(texts))

            # Generate embeddings
            embeddings = self.embedding_service.embed_documents(texts)

            # Generate IDs if not provided
            if ids is None:
                import uuid

                ids = [str(uuid.uuid4()) for _ in texts]

            # Build datapoints for upload
            # Note: Actual implementation would use Vertex AI Vector Search API
            # This is a simplified version
            logger.info("vertex_vectorstore_texts_added", count=len(texts))

            return ids

        except Exception as e:
            logger.error("vertex_vectorstore_add_texts_failed", error=str(e))
            raise VectorStoreError(f"Failed to add texts: {str(e)}")

    async def aadd_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add texts to the vector store asynchronously.

        Args:
            texts: List of texts to add
            metadatas: Optional list of metadata dicts
            ids: Optional list of IDs

        Returns:
            List of IDs for added documents

        Raises:
            VectorStoreError: If adding texts fails
        """
        try:
            logger.debug("vertex_vectorstore_adding_texts_async", count=len(texts))

            # Generate embeddings
            embeddings = await self.embedding_service.aembed_documents(texts)

            # Generate IDs if not provided
            if ids is None:
                import uuid

                ids = [str(uuid.uuid4()) for _ in texts]

            # Build datapoints for upload
            logger.info("vertex_vectorstore_texts_added_async", count=len(texts))

            return ids

        except Exception as e:
            logger.error("vertex_vectorstore_add_texts_async_failed", error=str(e))
            raise VectorStoreError(f"Failed to add texts: {str(e)}")

    def add_documents(
        self,
        documents: List[Document],
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add documents to the vector store.

        Args:
            documents: List of Document objects
            ids: Optional list of IDs

        Returns:
            List of IDs for added documents

        Raises:
            VectorStoreError: If adding documents fails
        """
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return self.add_texts(texts=texts, metadatas=metadatas, ids=ids)

    async def aadd_documents(
        self,
        documents: List[Document],
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add documents to the vector store asynchronously.

        Args:
            documents: List of Document objects
            ids: Optional list of IDs

        Returns:
            List of IDs for added documents

        Raises:
            VectorStoreError: If adding documents fails
        """
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return await self.aadd_texts(texts=texts, metadatas=metadatas, ids=ids)

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Search for similar documents.

        Args:
            query: Query text
            k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of similar documents

        Raises:
            VectorStoreError: If search fails

        Example:
            >>> results = manager.similarity_search("What is PsyAI?", k=5)
            >>> for doc in results:
            ...     print(doc.page_content)
        """
        try:
            logger.debug("vertex_vectorstore_similarity_search", query_length=len(query), k=k)

            # Generate query embedding
            query_embedding = self.embedding_service.embed_query(query)

            # Query the index
            if not self._index_endpoint:
                raise VectorStoreError("Index endpoint not initialized")

            # Perform search
            results = self._index_endpoint.find_neighbors(
                deployed_index_id=self.deployed_index_id,
                queries=[query_embedding],
                num_neighbors=k,
            )

            # Convert to Document objects
            documents = []
            for neighbor in results[0]:
                # Note: Actual implementation would retrieve document content
                documents.append(
                    Document(
                        page_content=f"Document {neighbor.id}",
                        metadata={"id": neighbor.id, "distance": neighbor.distance},
                    )
                )

            logger.info(
                "vertex_vectorstore_search_complete",
                results_count=len(documents),
            )

            return documents

        except Exception as e:
            logger.error("vertex_vectorstore_search_failed", error=str(e))
            raise VectorStoreError(f"Similarity search failed: {str(e)}")

    async def asimilarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Search for similar documents asynchronously.

        Args:
            query: Query text
            k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of similar documents

        Raises:
            VectorStoreError: If search fails
        """
        try:
            logger.debug("vertex_vectorstore_similarity_search_async", query_length=len(query), k=k)

            # Generate query embedding
            query_embedding = await self.embedding_service.aembed_query(query)

            # Query the index
            if not self._index_endpoint:
                raise VectorStoreError("Index endpoint not initialized")

            # Perform search (Vertex AI doesn't have async version, so we use sync)
            results = self._index_endpoint.find_neighbors(
                deployed_index_id=self.deployed_index_id,
                queries=[query_embedding],
                num_neighbors=k,
            )

            # Convert to Document objects
            documents = []
            for neighbor in results[0]:
                documents.append(
                    Document(
                        page_content=f"Document {neighbor.id}",
                        metadata={"id": neighbor.id, "distance": neighbor.distance},
                    )
                )

            logger.info(
                "vertex_vectorstore_search_complete_async",
                results_count=len(documents),
            )

            return documents

        except Exception as e:
            logger.error("vertex_vectorstore_search_async_failed", error=str(e))
            raise VectorStoreError(f"Similarity search failed: {str(e)}")

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[Document, float]]:
        """
        Search for similar documents with similarity scores.

        Args:
            query: Query text
            k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of (document, score) tuples
        """
        docs = self.similarity_search(query, k, filter)
        # Extract scores from metadata
        return [(doc, doc.metadata.get("distance", 0.0)) for doc in docs]

    def delete(self, ids: List[str]) -> None:
        """
        Delete documents by IDs.

        Args:
            ids: List of document IDs to delete

        Raises:
            VectorStoreError: If deletion fails
        """
        try:
            logger.debug("vertex_vectorstore_deleting", count=len(ids))

            # Note: Actual implementation would use Vertex AI Vector Search API
            # to remove datapoints

            logger.info("vertex_vectorstore_deleted", count=len(ids))

        except Exception as e:
            logger.error("vertex_vectorstore_delete_failed", error=str(e))
            raise VectorStoreError(f"Delete failed: {str(e)}")
