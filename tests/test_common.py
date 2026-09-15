"""Tests de la validation des posts (common.validate_post)."""
import common
import pytest


def valid_post(**overrides):
    post = {
        "slug": "kv-cache-basics",
        "area": "LLMs and RAG",
        "concept": "KV cache",
        "source": "AI Engineering",
        "text": "Cache what's read. Queue what's written.\n\nThe KV cache stores past tokens.\nIt avoids recomputing attention.\nDrop it and latency explodes.",
    }
    post.update(overrides)
    return post


def test_valid_post_passes():
    ok, reason = common.validate_post(valid_post(), set())
    assert ok is True
    assert reason is None


def test_missing_field_rejected():
    post = valid_post()
    del post["source"]
    ok, reason = common.validate_post(post, set())
    assert ok is False
    assert "source" in reason


def test_empty_field_rejected():
    ok, reason = common.validate_post(valid_post(text="   "), set())
    assert ok is False
    assert "text" in reason


def test_text_too_long_rejected():
    ok, reason = common.validate_post(valid_post(text="x" * 451), set())
    assert ok is False
    assert "trop long" in reason


def test_text_at_limit_accepted():
    ok, _ = common.validate_post(valid_post(text="x" * 450), set())
    assert ok is True


def test_emoji_rejected():
    ok, reason = common.validate_post(valid_post(text="Great idea \U0001f600 here"), set())
    assert ok is False
    assert "emoji" in reason


def test_em_dash_rejected():
    ok, reason = common.validate_post(valid_post(text="One thing — another thing"), set())
    assert ok is False
    assert "tiret cadratin" in reason


def test_hashtag_rejected():
    ok, reason = common.validate_post(valid_post(text="Learn this #mlops today"), set())
    assert ok is False
    assert "hashtag" in reason


def test_existing_slug_rejected():
    ok, reason = common.validate_post(valid_post(), {"kv-cache-basics"})
    assert ok is False
    assert "déjà existant" in reason


def test_invalid_slug_rejected():
    ok, reason = common.validate_post(valid_post(slug="Not A Slug"), set())
    assert ok is False
    assert "slug invalide" in reason


def test_unknown_source_rejected():
    ok, reason = common.validate_post(valid_post(source="Some Random Blog"), set())
    assert ok is False
    assert "source non autorisée" in reason


def test_source_case_insensitive():
    ok, _ = common.validate_post(valid_post(source="ai engineering"), set())
    assert ok is True


@pytest.mark.parametrize("source", sorted(common.ALLOWED_SOURCES))
def test_all_allowed_sources_accepted(source):
    ok, _ = common.validate_post(valid_post(source=source), set())
    assert ok is True


def test_non_dict_rejected():
    ok, reason = common.validate_post("not a dict", set())
    assert ok is False
