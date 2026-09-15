"""Génère 7 nouveaux posts LinkedIn avec Groq et les écrit dans posts/queue/.

Le prompt système est lu depuis prompts/system.md. Le message utilisateur liste
les concepts déjà publiés ou en file d'attente pour éviter les redites.

Usage :
    python scripts/generate_posts.py [--dry-run] [--summary-path CHEMIN]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import os
import sys

from dotenv import load_dotenv

import common

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("generate_posts")

GROQ_MODEL = "openai/gpt-oss-120b"
NUM_POSTS = 7
TEMPERATURE = 0.8
SYSTEM_PROMPT_PATH = common.REPO_ROOT / "prompts" / "system.md"


def read_system_prompt() -> str:
    if not SYSTEM_PROMPT_PATH.exists():
        logger.error("Prompt système introuvable : %s", SYSTEM_PROMPT_PATH)
        sys.exit(1)
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


def build_user_message() -> str:
    """Construit le message utilisateur envoyé à Groq."""
    concepts = common.load_existing_concepts()
    lines = [f"Write {NUM_POSTS} new posts."]
    if concepts:
        lines.append("")
        lines.append("Already published or queued concepts (never reuse these):")
        lines.extend(f"- {c}" for c in concepts)
    return "\n".join(lines)


def call_groq(system_prompt: str, user_message: str) -> str:
    """Appelle l'API Groq et retourne le contenu JSON brut."""
    from groq import Groq

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logger.error("Variable d'environnement GROQ_API_KEY absente.")
        sys.exit(1)

    client = Groq(api_key=api_key)
    logger.info("Appel Groq (modèle %s)…", GROQ_MODEL)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
        temperature=TEMPERATURE,
    )
    return response.choices[0].message.content


def parse_posts(raw: str) -> list[dict]:
    """Extrait la liste des posts du JSON renvoyé par Groq."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("Réponse Groq non JSON : %s", exc)
        sys.exit(1)
    posts = data.get("posts")
    if not isinstance(posts, list):
        logger.error("Réponse Groq sans liste 'posts' exploitable.")
        sys.exit(1)
    return posts


def select_valid_posts(posts: list[dict]) -> list[dict]:
    """Filtre les posts valides ; log chaque rejet avec sa raison."""
    existing_slugs = common.load_existing_slugs()
    valid: list[dict] = []
    for index, post in enumerate(posts, start=1):
        ok, reason = common.validate_post(post, existing_slugs)
        if not ok:
            slug = post.get("slug", "?") if isinstance(post, dict) else "?"
            logger.warning("Post #%d rejeté (%s) : %s", index, slug, reason)
            continue
        valid.append(post)
        # Empêche les doublons de slug à l'intérieur d'un même lot.
        existing_slugs.add(str(post["slug"]).strip())
    return valid


def write_summary(posts: list[dict], summary_path: str) -> None:
    """Écrit un corps de PR listant concept, area et source de chaque post."""
    lines = [f"{len(posts)} post(s) générés cette semaine :", ""]
    for post in posts:
        lines.append(
            f"- **{post['concept']}** — area : {post['area']} — "
            f"source : {post['source']} (`{post['slug']}`)"
        )
    from pathlib import Path

    Path(summary_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Corps de PR écrit dans %s", summary_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Génère des posts LinkedIn avec Groq.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche les posts sans écrire de fichier.",
    )
    parser.add_argument(
        "--summary-path",
        default=None,
        help="Chemin où écrire le corps de la PR (concept, area, source).",
    )
    args = parser.parse_args()

    load_dotenv()

    system_prompt = read_system_prompt()
    user_message = build_user_message()

    raw = call_groq(system_prompt, user_message)
    posts = parse_posts(raw)
    valid = select_valid_posts(posts)

    if not valid:
        logger.error("Aucun post valide ; rien à écrire.")
        sys.exit(1)

    if args.dry_run:
        logger.info("--dry-run : %d post(s) valide(s), aucun fichier écrit.", len(valid))
        for post in valid:
            print("-" * 60)
            print(f"slug    : {post['slug']}")
            print(f"area    : {post['area']}")
            print(f"concept : {post['concept']}")
            print(f"source  : {post['source']}")
            print()
            print(post["text"])
            print(f"\n{common.SIGNATURE}")
        return

    created = dt.date.today().isoformat()
    for post in valid:
        path = common.write_queue_post(post, created)
        logger.info("Écrit : %s", path.relative_to(common.REPO_ROOT))

    logger.info("%d post(s) ajoutés à la file.", len(valid))

    if args.summary_path:
        write_summary(valid, args.summary_path)


if __name__ == "__main__":
    main()
