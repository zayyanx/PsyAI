"""
Database models for PsyAI.

This module defines all database tables used in the application.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from psyai.platform.storage_layer.database.base import BaseModel

import enum


class ChatMode(str, enum.Enum):
    """Chat modes."""

    AI = "ai"
    EXPERT = "expert"
    PASSTHROUGH = "passthrough"


class ReviewStatus(str, enum.Enum):
    """Review statuses for HITL."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


class User(BaseModel):
    """
    User model.

    Represents users in the system (both end users and experts).
    """

    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_expert = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="expert", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class ChatSession(BaseModel):
    """
    Chat session model.

    Represents a conversation session between a user and the AI.
    """

    __tablename__ = "chat_sessions"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mode = Column(Enum(ChatMode), nullable=False, default=ChatMode.AI)
    title = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    metadata = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, mode={self.mode}, user_id={self.user_id})>"


class Message(BaseModel):
    """
    Message model.

    Represents individual messages in a chat session.
    """

    __tablename__ = "messages"

    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=True)
    needs_review = Column(Boolean, default=False, nullable=False)
    metadata = Column(JSON, nullable=True)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    review = relationship("Review", back_populates="message", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role}, session_id={self.session_id})>"


class Review(BaseModel):
    """
    Review model.

    Represents expert reviews for HITL (Human-in-the-Loop) workflow.
    """

    __tablename__ = "reviews"

    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False, unique=True, index=True)
    expert_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    status = Column(Enum(ReviewStatus), nullable=False, default=ReviewStatus.PENDING)
    original_content = Column(Text, nullable=False)
    reviewed_content = Column(Text, nullable=True)
    expert_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    # Relationships
    message = relationship("Message", back_populates="review")
    expert = relationship("User", back_populates="reviews")

    def __repr__(self) -> str:
        return f"<Review(id={self.id}, status={self.status}, message_id={self.message_id})>"


class Dataset(BaseModel):
    """
    Dataset model.

    Represents evaluation datasets for testing and improvement.
    """

    __tablename__ = "datasets"

    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    langsmith_dataset_id = Column(String(255), nullable=True, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)
    metadata = Column(JSON, nullable=True)

    # Relationships
    examples = relationship("DatasetExample", back_populates="dataset", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="dataset", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Dataset(id={self.id}, name={self.name})>"


class DatasetExample(BaseModel):
    """
    Dataset example model.

    Represents individual examples in an evaluation dataset.
    """

    __tablename__ = "dataset_examples"

    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False, index=True)
    langsmith_example_id = Column(String(255), nullable=True, unique=True)
    inputs = Column(JSON, nullable=False)
    expected_outputs = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    dataset = relationship("Dataset", back_populates="examples")

    def __repr__(self) -> str:
        return f"<DatasetExample(id={self.id}, dataset_id={self.dataset_id})>"


class Evaluation(BaseModel):
    """
    Evaluation model.

    Represents evaluation runs on datasets.
    """

    __tablename__ = "evaluations"

    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    langsmith_run_id = Column(String(255), nullable=True, unique=True)
    total_examples = Column(Integer, nullable=False, default=0)
    passed_examples = Column(Integer, nullable=False, default=0)
    failed_examples = Column(Integer, nullable=False, default=0)
    average_score = Column(Float, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    dataset = relationship("Dataset", back_populates="evaluations")
    results = relationship("EvaluationResult", back_populates="evaluation", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Evaluation(id={self.id}, name={self.name})>"


class EvaluationResult(BaseModel):
    """
    Evaluation result model.

    Represents individual results from evaluation runs.
    """

    __tablename__ = "evaluation_results"

    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), nullable=False, index=True)
    example_id = Column(Integer, ForeignKey("dataset_examples.id"), nullable=True, index=True)
    passed = Column(Boolean, nullable=False)
    score = Column(Float, nullable=True)
    actual_output = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    evaluation = relationship("Evaluation", back_populates="results")
    example = relationship("DatasetExample")

    def __repr__(self) -> str:
        return f"<EvaluationResult(id={self.id}, passed={self.passed})>"


class Document(BaseModel):
    """
    Document model.

    Represents documents for RAG (Retrieval Augmented Generation).
    """

    __tablename__ = "documents"

    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    source = Column(String(500), nullable=True)
    source_type = Column(String(50), nullable=True)  # file, url, api, etc.
    vector_store_id = Column(String(255), nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, title={self.title})>"


class DocumentChunk(BaseModel):
    """
    Document chunk model.

    Represents chunks of documents for vector storage.
    """

    __tablename__ = "document_chunks"

    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    vector_id = Column(String(255), nullable=True, unique=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    document = relationship("Document", back_populates="chunks")

    def __repr__(self) -> str:
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index})>"
