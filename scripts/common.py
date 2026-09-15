"""Utilitaires partagés : lecture/écriture des fichiers de posts et validation.

Le dépôt git sert de file d'attente ; il n'y a pas de base de données.
Ce module centralise l'accès aux fichiers de posts et les règles de validation
utilisées par ``generate_posts.py`` (et indirectement par ``publish_linkedin.py``).
"""
from __future__ import annotations

import datetime as dt
import logging
import re
from pathlib import Path

import frontmatter

logger = logging.getLogger(__name__)

# --- Chemins ---------------------------------------------------------------

# Racine du dépôt = dossier parent de scripts/.
REPO_ROOT = Path(__file__).resolve().parent.parent
QUEUE_DIR = REPO_ROOT / "posts" / "queue"
PUBLISHED_DIR = REPO_ROOT / "posts" / "published"

# --- Constantes de validation ---------------------------------------------

# Longueur maximale du texte d'un post.
MAX_POST_LENGTH = 450

# Champs obligatoires d'un post renvoyé par Groq.
REQUIRED_FIELDS = ("slug", "area", "concept", "source", "text")

# Format attendu pour un slug (kebab-case).
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Noms de références autorisés, repris exactement de la section SOURCES
# du prompt système (prompts/system.md). Un post dont le champ ``source``
# n'appartient pas à cette liste est rejeté.
ALLOWED_SOURCES = {
    "ByteByteGo",
    "Designing Data-Intensive Applications",
    "Google's Site Reliability Engineering book",
    "Hands-On Machine Learning",
    "The Hundred-Page Machine Learning Book",
    "StatQuest",
    "3Blue1Brown",
    "Designing Machine Learning Systems",
    "Machine Learning Engineering",
    "AI Engineering",
    "Andrej Karpathy's YouTube lectures",
    "Fundamentals of Data Engineering",
    "Fluent Python",
    "High Performance Python",
    "AWS Well-Architected Framework",
}

# Comparaison insensible à la casse et aux espaces superflus.
_ALLOWED_SOURCES_LOWER = {s.lower() for s in ALLOWED_SOURCES}

# Plages Unicode couvrant l'essentiel des emojis.
EMOJI_PATTERN = re.compile(
    "["
    "\U0001f000-\U0001faff"  # émoticônes, pictogrammes, symboles, drapeaux…
    "\U00002600-\U000027bf"  # symboles divers et dingbats
    "\U00002b00-\U00002bff"  # symboles et flèches supplémentaires
    "\U0000fe00-\U0000fe0f"  # sélecteurs de variation
    "\U000024c2"
    "\U0000203c\U00002049"
    "\U000020e3"
    "]",
    flags=re.UNICODE,
)

EM_DASH = "—"  # tiret cadratin —


# --- Validation ------------------------------------------------------------

def validate_post(post: dict, existing_slugs: set[str]) -> tuple[bool, str | None]:
    """Valide un post.

    Retourne ``(True, None)`` si le post est valide, sinon ``(False, raison)``.
    """
    if not isinstance(post, dict):
        return False, "post JSON invalide (objet attendu)"

    # Champs obligatoires présents et non vides.
    for field in REQUIRED_FIELDS:
        value = post.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, f"champ manquant ou vide : {field}"

    slug = str(post["slug"]).strip()
    text = str(post["text"])
    source = str(post["source"]).strip()

    if not SLUG_PATTERN.match(slug):
        return False, f"slug invalide (kebab-case attendu) : {slug!r}"

    if slug in existing_slugs:
        return False, f"slug déjà existant : {slug}"

    if source.lower() not in _ALLOWED_SOURCES_LOWER:
        return False, f"source non autorisée : {source!r}"

    if len(text) > MAX_POST_LENGTH:
        return False, f"texte trop long : {len(text)} > {MAX_POST_LENGTH} caractères"

    if EMOJI_PATTERN.search(text):
        return False, "présence d'un emoji"

    if EM_DASH in text:
        return False, "présence d'un tiret cadratin (—)"

    if "#" in text:
        return False, "présence d'un hashtag (#)"

    return True, None


# --- Lecture des posts existants ------------------------------------------

def _iter_post_files(*dirs: Path):
    for directory in dirs:
        if directory.exists():
            for path in sorted(directory.glob("*.md")):
                yield path


def _load(path: Path):
    try:
        return frontmatter.load(path)
    except Exception as exc:  # noqa: BLE001 - on log et on continue
        logger.warning("Impossible de lire %s : %s", path, exc)
        return None


def load_existing_slugs() -> set[str]:
    """Slugs présents dans posts/queue/ et posts/published/."""
    slugs: set[str] = set()
    for path in _iter_post_files(QUEUE_DIR, PUBLISHED_DIR):
        post = _load(path)
        if post is None:
            continue
        slug = post.get("slug")
        if slug:
            slugs.add(str(slug).strip())
    return slugs


def load_existing_concepts() -> list[str]:
    """Concepts présents dans posts/queue/ et posts/published/ (pour éviter les redites)."""
    concepts: list[str] = []
    for path in _iter_post_files(QUEUE_DIR, PUBLISHED_DIR):
        post = _load(path)
        if post is None:
            continue
        concept = post.get("concept")
        if concept:
            concepts.append(str(concept).strip())
    return concepts


# --- Écriture / déplacement -----------------------------------------------

def _render_body(text: str) -> str:
    """Corps du fichier : le texte du post, tel quel (aucune signature ajoutée)."""
    return text.rstrip("\n")


def build_post(post: dict, created: str | None = None) -> "frontmatter.Post":
    """Construit un objet frontmatter.Post prêt à être écrit."""
    created = created or dt.date.today().isoformat()
    metadata = {
        "slug": str(post["slug"]).strip(),
        "area": str(post["area"]).strip(),
        "concept": str(post["concept"]).strip(),
        "source": str(post["source"]).strip(),
        "created": created,
    }
    return frontmatter.Post(_render_body(str(post["text"])), **metadata)


def dump_post(fm_post: "frontmatter.Post", path: Path) -> None:
    """Écrit un fichier de post en préservant l'ordre des clés et les accents."""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = frontmatter.dumps(fm_post, sort_keys=False, allow_unicode=True)
    path.write_text(content + "\n", encoding="utf-8")


def write_queue_post(post: dict, created: str | None = None) -> Path:
    """Écrit un post validé dans posts/queue/ et retourne son chemin."""
    created = created or dt.date.today().isoformat()
    slug = str(post["slug"]).strip()
    path = QUEUE_DIR / f"{created}-{slug}.md"
    dump_post(build_post(post, created), path)
    return path


def oldest_queue_file() -> Path | None:
    """Fichier le plus ancien de la file (tri par nom de fichier)."""
    if not QUEUE_DIR.exists():
        return None
    files = sorted(QUEUE_DIR.glob("*.md"))
    return files[0] if files else None


def post_commentary(fm_post: "frontmatter.Post") -> str:
    """Texte à publier (corps du fichier)."""
    return fm_post.content.rstrip("\n")
