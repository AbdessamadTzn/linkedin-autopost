"""Affiche l'identifiant de personne LinkedIn (LINKEDIN_PERSON_ID).

Appelle GET /v2/userinfo (OpenID Connect) avec le jeton et affiche le champ
``sub``. À lancer une seule fois en local :

    python scripts/get_person_id.py
"""
from __future__ import annotations

import logging
import os
import sys

import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("get_person_id")

USERINFO_URL = "https://api.linkedin.com/v2/userinfo"


def main() -> None:
    load_dotenv()

    token = os.environ.get("LINKEDIN_TOKEN")
    if not token:
        logger.error("Variable d'environnement LINKEDIN_TOKEN absente.")
        sys.exit(1)

    response = requests.get(
        USERINFO_URL,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )

    if response.status_code == 401:
        logger.error(
            "Jeton LinkedIn expiré ou invalide, régénère-le et réessaie."
        )
        sys.exit(1)

    if response.status_code != 200:
        logger.error("Échec (statut %s) : %s", response.status_code, response.text)
        sys.exit(1)

    sub = response.json().get("sub")
    if not sub:
        logger.error("Champ 'sub' absent de la réponse : %s", response.text)
        sys.exit(1)

    print(sub)
    logger.info("Renseigne cette valeur dans le secret LINKEDIN_PERSON_ID.")


if __name__ == "__main__":
    main()
