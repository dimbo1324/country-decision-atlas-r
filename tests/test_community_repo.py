"""SQL-only community repository: required functions and published-only filtering."""

from app.repositories import community as repository
import inspect


def test_community_repository_is_sql_only() -> None:
    source = inspect.getsource(repository)

    assert "fastapi" not in source
    assert "BaseModel" not in source
    assert "INSERT INTO qna_questions" in source
    assert "INSERT INTO qna_answers" in source
    assert "INSERT INTO qna_votes" in source


def test_community_repository_has_required_functions() -> None:
    for name in [
        "insert_question",
        "list_published_questions",
        "get_question",
        "update_question_status",
        "insert_answer",
        "list_published_answers",
        "get_answer",
        "update_answer_status",
        "insert_vote",
        "get_vote_summary",
    ]:
        assert hasattr(repository, name), name


def test_list_published_questions_filters_by_status() -> None:
    source = inspect.getsource(repository.list_published_questions)

    assert "status = 'published'" in source


def test_get_question_public_only_filters_by_status() -> None:
    source = inspect.getsource(repository.get_question)

    assert "status = 'published'" in source


def test_insert_vote_is_idempotent_on_conflict() -> None:
    source = inspect.getsource(repository.insert_vote)

    assert "ON CONFLICT" in source
    assert "DO NOTHING" in source
