"""Tests for database models."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from psyai.platform.storage_layer.database.base import Base
from psyai.platform.storage_layer.database.models import (
    ChatMode,
    ChatSession,
    Dataset,
    DatasetExample,
    Document,
    DocumentChunk,
    Evaluation,
    EvaluationResult,
    Message,
    Review,
    ReviewStatus,
    User,
)


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()


class TestUserModel:
    """Test User model."""

    def test_create_user(self, db_session: Session):
        """Test creating a user."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed123",
            full_name="Test User",
            is_active=True,
            is_expert=False,
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.is_expert is False
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_to_dict(self, db_session: Session):
        """Test user to_dict method."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed123",
        )
        db_session.add(user)
        db_session.commit()

        user_dict = user.to_dict()

        assert user_dict["email"] == "test@example.com"
        assert user_dict["username"] == "testuser"
        assert "id" in user_dict
        assert "created_at" in user_dict

    def test_user_relationships(self, db_session: Session):
        """Test user relationships."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed123",
        )
        db_session.add(user)
        db_session.commit()

        # Create chat session
        session = ChatSession(user_id=user.id, mode=ChatMode.AI)
        db_session.add(session)
        db_session.commit()

        assert len(user.chat_sessions) == 1
        assert user.chat_sessions[0].mode == ChatMode.AI


class TestChatSessionModel:
    """Test ChatSession model."""

    def test_create_chat_session(self, db_session: Session):
        """Test creating a chat session."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed123",
        )
        db_session.add(user)
        db_session.commit()

        session = ChatSession(
            user_id=user.id,
            mode=ChatMode.AI,
            title="Test Session",
            is_active=True,
        )
        db_session.add(session)
        db_session.commit()

        assert session.id is not None
        assert session.user_id == user.id
        assert session.mode == ChatMode.AI
        assert session.title == "Test Session"
        assert session.is_active is True

    def test_chat_modes(self, db_session: Session):
        """Test different chat modes."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed123",
        )
        db_session.add(user)
        db_session.commit()

        for mode in [ChatMode.AI, ChatMode.EXPERT, ChatMode.PASSTHROUGH]:
            session = ChatSession(user_id=user.id, mode=mode)
            db_session.add(session)
            db_session.commit()

            assert session.mode == mode


class TestMessageModel:
    """Test Message model."""

    def test_create_message(self, db_session: Session):
        """Test creating a message."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed123",
        )
        db_session.add(user)
        db_session.commit()

        session = ChatSession(user_id=user.id, mode=ChatMode.AI)
        db_session.add(session)
        db_session.commit()

        message = Message(
            session_id=session.id,
            role="user",
            content="Hello, world!",
            confidence_score=0.95,
            needs_review=False,
        )
        db_session.add(message)
        db_session.commit()

        assert message.id is not None
        assert message.session_id == session.id
        assert message.role == "user"
        assert message.content == "Hello, world!"
        assert message.confidence_score == 0.95
        assert message.needs_review is False


class TestReviewModel:
    """Test Review model."""

    def test_create_review(self, db_session: Session):
        """Test creating a review."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed123",
        )
        expert = User(
            email="expert@example.com",
            username="expert",
            hashed_password="hashed123",
            is_expert=True,
        )
        db_session.add_all([user, expert])
        db_session.commit()

        session = ChatSession(user_id=user.id, mode=ChatMode.AI)
        db_session.add(session)
        db_session.commit()

        message = Message(
            session_id=session.id,
            role="assistant",
            content="Original response",
            needs_review=True,
        )
        db_session.add(message)
        db_session.commit()

        review = Review(
            message_id=message.id,
            expert_id=expert.id,
            status=ReviewStatus.PENDING,
            original_content="Original response",
        )
        db_session.add(review)
        db_session.commit()

        assert review.id is not None
        assert review.message_id == message.id
        assert review.expert_id == expert.id
        assert review.status == ReviewStatus.PENDING

    def test_review_statuses(self, db_session: Session):
        """Test different review statuses."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed123",
        )
        db_session.add(user)
        db_session.commit()

        session = ChatSession(user_id=user.id, mode=ChatMode.AI)
        db_session.add(session)
        db_session.commit()

        for status in [ReviewStatus.PENDING, ReviewStatus.APPROVED, ReviewStatus.REJECTED, ReviewStatus.MODIFIED]:
            message = Message(
                session_id=session.id,
                role="assistant",
                content=f"Response {status.value}",
            )
            db_session.add(message)
            db_session.commit()

            review = Review(
                message_id=message.id,
                status=status,
                original_content=f"Response {status.value}",
            )
            db_session.add(review)
            db_session.commit()

            assert review.status == status


class TestDatasetModel:
    """Test Dataset and related models."""

    def test_create_dataset(self, db_session: Session):
        """Test creating a dataset."""
        dataset = Dataset(
            name="test_dataset",
            description="Test dataset for evaluation",
            is_active=True,
        )
        db_session.add(dataset)
        db_session.commit()

        assert dataset.id is not None
        assert dataset.name == "test_dataset"
        assert dataset.is_active is True

    def test_dataset_with_examples(self, db_session: Session):
        """Test dataset with examples."""
        dataset = Dataset(name="test_dataset")
        db_session.add(dataset)
        db_session.commit()

        example = DatasetExample(
            dataset_id=dataset.id,
            inputs={"query": "What is 2+2?"},
            expected_outputs={"answer": "4"},
        )
        db_session.add(example)
        db_session.commit()

        assert len(dataset.examples) == 1
        assert dataset.examples[0].inputs["query"] == "What is 2+2?"


class TestEvaluationModel:
    """Test Evaluation model."""

    def test_create_evaluation(self, db_session: Session):
        """Test creating an evaluation."""
        dataset = Dataset(name="test_dataset")
        db_session.add(dataset)
        db_session.commit()

        evaluation = Evaluation(
            dataset_id=dataset.id,
            name="Test Evaluation",
            total_examples=10,
            passed_examples=8,
            failed_examples=2,
            average_score=0.85,
        )
        db_session.add(evaluation)
        db_session.commit()

        assert evaluation.id is not None
        assert evaluation.dataset_id == dataset.id
        assert evaluation.total_examples == 10
        assert evaluation.passed_examples == 8
        assert evaluation.average_score == 0.85


class TestDocumentModel:
    """Test Document model."""

    def test_create_document(self, db_session: Session):
        """Test creating a document."""
        doc = Document(
            title="Test Document",
            content="This is test content",
            source="test.txt",
            source_type="file",
        )
        db_session.add(doc)
        db_session.commit()

        assert doc.id is not None
        assert doc.title == "Test Document"
        assert doc.content == "This is test content"

    def test_document_with_chunks(self, db_session: Session):
        """Test document with chunks."""
        doc = Document(
            title="Test Document",
            content="This is test content",
        )
        db_session.add(doc)
        db_session.commit()

        chunk1 = DocumentChunk(
            document_id=doc.id,
            chunk_index=0,
            content="This is",
        )
        chunk2 = DocumentChunk(
            document_id=doc.id,
            chunk_index=1,
            content="test content",
        )
        db_session.add_all([chunk1, chunk2])
        db_session.commit()

        assert len(doc.chunks) == 2
        assert doc.chunks[0].chunk_index == 0
        assert doc.chunks[1].chunk_index == 1
