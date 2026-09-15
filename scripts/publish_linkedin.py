"""Publie le post le plus ancien de posts/queue/ sur LinkedIn, puis le déplace.

Usage :
    python scripts/publish_linkedin.py [--dry-run]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import os
import sys

import requests
from dotenv import load_dotenv

import common

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("publish_linkedin")

# Version de l'API LinkedIn (format YYYYMM). LinkedIn maintient chaque version
# au moins 2 ans ; « 202607 » est une version actuellement supportée.
# Doc : https://learn.microsoft.com/en-us/linkedin/marketing/versioning
LINKEDIN_API_VERSION = "202607"

POSTS_URL = "https://api.linkedin.com/rest/posts"

# Caractères réservés du format « little text » de LinkedIn : ils doivent être
# précédés d'un backslash, sinon le post est tronqué ou refusé.
LITTLE_TEXT_RESERVED = set(r"\|{}@[]()<>#*_~")


def escape_little_text(text: str) -> str:
    """Échappe les caractères réservés du format « little text » de LinkedIn.

    Le backslash fait partie des caractères réservés ; comme on parcourt le
    texte caractère par caractère, il est échappé une seule fois, sans double
    traitement des backslashes déjà insérés.
    """
    out = []
    for ch in text:
        if ch in LITTLE_TEXT_RESERVED:
            out.append("\\")
        out.append(ch)
    return "".join(out)


def build_body(person_id: str, commentary: str) -> dict:
    """Construit le corps JSON de la requête POST /rest/posts."""
    return {
        "author": f"urn:li:person:{person_id}",
        "commentary": commentary,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }


def publish(body: dict, token: str) -> requests.Response:
    headers = {
        "Authorization": f"Bearer {token}",
        "LinkedIn-Version": LINKEDIN_API_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }
    return requests.post(POSTS_URL, headers=headers, json=body, timeout=30)


def main() -> None:
    parser = argparse.ArgumentParser(description="Publie le post le plus ancien sur LinkedIn.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche le JSON qui serait envoyé, sans appel réseau.",
    )
    args = parser.parse_args()

    load_dotenv()

    import frontmatter

    path = common.oldest_queue_file()
    if path is None:
        logger.warning("File d'attente vide : rien à publier.")
        sys.exit(0)

    logger.info("Post sélectionné : %s", path.relative_to(common.REPO_ROOT))
    fm_post = frontmatter.load(path)
    commentary = escape_little_text(common.post_commentary(fm_post))

    person_id = os.environ.get("LINKEDIN_PERSON_ID", "")
    body = build_body(person_id, commentary)

    if args.dry_run:
        if not person_id:
            body["author"] = "urn:li:person:<LINKEDIN_PERSON_ID>"
        logger.info("--dry-run : aucun appel réseau.")
        print(json.dumps(body, ensure_ascii=False, indent=2))
        return

    token = os.environ.get("LINKEDIN_TOKEN")
    if not token:
        logger.error("Variable d'environnement LINKEDIN_TOKEN absente.")
        sys.exit(1)
    if not person_id:
        logger.error("Variable d'environnement LINKEDIN_PERSON_ID absente.")
        sys.exit(1)

    response = publish(body, token)

    if response.status_code == 201:
        post_id = response.headers.get("x-restli-id", "")
        logger.info("Post publié (id : %s).", post_id)
        fm_post["published_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        fm_post["post_id"] = post_id
        target = common.PUBLISHED_DIR / path.name
        common.dump_post(fm_post, target)
        path.unlink()
        logger.info("Déplacé vers %s", target.relative_to(common.REPO_ROOT))
        return

    if response.status_code == 401:
        logger.error(
            "Jeton LinkedIn expiré, régénère-le et mets à jour le secret LINKEDIN_TOKEN"
        )
        sys.exit(1)

    logger.error(
        "Échec de publication (statut %s). Le fichier reste dans la file.\n%s",
        response.status_code,
        response.text,
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
