"""Tests de escape_little_text et build_body (publish_linkedin)."""
import publish_linkedin as pub


def test_escape_reserved_characters():
    assert pub.escape_little_text("a|b") == "a\\|b"
    assert pub.escape_little_text("(x)") == "\\(x\\)"
    assert pub.escape_little_text("a{b}c") == "a\\{b\\}c"
    assert pub.escape_little_text("@handle") == "\\@handle"
    assert pub.escape_little_text("a#b*c_d~e") == "a\\#b\\*c\\_d\\~e"
    assert pub.escape_little_text("[a]<b>") == "\\[a\\]\\<b\\>"


def test_escape_backslash_once():
    # Un backslash isolé devient exactement deux caractères, pas plus.
    assert pub.escape_little_text("\\") == "\\\\"
    assert pub.escape_little_text("a\\b") == "a\\\\b"


def test_escape_plain_text_unchanged():
    text = "Fit on train. Score on test. Never peek."
    assert pub.escape_little_text(text) == text


def test_escape_preserves_newlines():
    text = "line one\nline two"
    assert pub.escape_little_text(text) == text


def test_escape_all_reserved_together():
    reserved = r"\|{}@[]()<>#*_~"
    escaped = pub.escape_little_text(reserved)
    # Chaque caractère réservé est précédé d'un backslash.
    assert escaped == "".join("\\" + c for c in reserved)


def test_build_body_shape():
    body = pub.build_body("ABC123", "Hello world")
    assert body["author"] == "urn:li:person:ABC123"
    assert body["commentary"] == "Hello world"
    assert body["visibility"] == "PUBLIC"
    assert body["lifecycleState"] == "PUBLISHED"
    assert body["isReshareDisabledByAuthor"] is False
    assert body["distribution"]["feedDistribution"] == "MAIN_FEED"
    assert body["distribution"]["targetEntities"] == []
    assert body["distribution"]["thirdPartyDistributionChannels"] == []


def test_api_version_format():
    assert pub.LINKEDIN_API_VERSION.isdigit()
    assert len(pub.LINKEDIN_API_VERSION) == 6
