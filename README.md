# linkedin-autopost

Génère et publie automatiquement des posts LinkedIn sur un profil personnel,
orchestré par GitHub Actions. **Le dépôt git sert de file d'attente : pas de base
de données.**

- Un workflow hebdomadaire (dimanche) génère 7 posts avec Groq et ouvre une Pull
  Request pour relecture.
- Un workflow quotidien (lundi–vendredi) publie le post le plus ancien de la file
  et le déplace dans `posts/published/`.

## Fonctionnement

```
posts/queue/       posts validés en attente de publication
posts/published/   posts déjà publiés
prompts/system.md  prompt système Groq
scripts/           génération, publication, utilitaires
.github/workflows/ génération hebdo + publication quotidienne
```

Chaque post est un fichier `posts/queue/YYYY-MM-DD-<slug>.md` :

```markdown
---
slug: kv-cache-basics
area: LLMs and RAG
concept: KV cache
source: AI Engineering
created: 2026-09-15
---
Cache what's read. Queue what's written.

...
```

Le post est publié tel que le modèle l'écrit : aucune signature ni lien n'est
ajouté par le script.

## Prérequis

- Python 3.12
- Un compte Groq (clé API) et une application LinkedIn (voir plus bas)

Installation locale :

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # puis renseigner les valeurs
```

## Scripts

| Script | Rôle |
| --- | --- |
| `scripts/generate_posts.py` | Génère 7 posts avec Groq, valide, écrit dans `posts/queue/`. |
| `scripts/publish_linkedin.py` | Publie le post le plus ancien puis le déplace dans `posts/published/`. |
| `scripts/get_person_id.py` | Affiche votre `LINKEDIN_PERSON_ID` (à lancer une fois). |
| `scripts/common.py` | Lecture/écriture des fichiers de posts et validation. |

Options `--dry-run` disponibles :

```bash
python scripts/generate_posts.py --dry-run   # affiche les posts sans écrire (appelle Groq)
python scripts/publish_linkedin.py --dry-run # affiche le JSON, sans appel réseau
```

Validation d'un post (rejet avec log sinon) : texte ≤ 450 caractères, pas d'emoji,
pas de tiret cadratin (—), pas de hashtag, slug unique, champ `source` présent et
appartenant à la liste `ALLOWED_SOURCES` (section SOURCES du prompt système).

## Configuration de l'application LinkedIn

1. **Page entreprise.** LinkedIn exige une page pour créer une app. Créez (ou
   utilisez) la page **TechFi24**.
2. **Créer l'app** sur <https://www.linkedin.com/developers/apps> et l'associer à
   cette page.
3. **Ajouter deux produits** (onglet *Products*) :
   - **Share on LinkedIn**
   - **Sign In with LinkedIn using OpenID Connect**
4. **Scopes nécessaires** : `openid`, `profile`, `w_member_social`.
5. **Générer le jeton** avec le *token generator* du portail (onglet *Auth* →
   *OAuth 2.0 tools* → *Token Generator*). Sélectionnez les trois scopes ci-dessus.
   Copiez l'*access token* obtenu : c'est `LINKEDIN_TOKEN`.
6. **Obtenir votre identifiant** :

   ```bash
   LINKEDIN_TOKEN=... python scripts/get_person_id.py
   ```

   La valeur affichée (`sub`) est `LINKEDIN_PERSON_ID`.

> La version de l'API LinkedIn utilisée est fixée dans `scripts/publish_linkedin.py`
> (`LINKEDIN_API_VERSION = "202607"`). LinkedIn maintient chaque version au moins
> 2 ans ; mettez-la à jour si besoin depuis la
> [doc officielle](https://learn.microsoft.com/en-us/linkedin/marketing/versioning).

## Secrets GitHub

Dans **Settings → Secrets and variables → Actions**, créez :

| Secret | Valeur |
| --- | --- |
| `GROQ_API_KEY` | Clé API Groq (<https://console.groq.com/keys>). |
| `LINKEDIN_TOKEN` | Access token LinkedIn. |
| `LINKEDIN_PERSON_ID` | Champ `sub` renvoyé par `get_person_id.py`. |

## Réglage GitHub à activer

Pour que le workflow du dimanche puisse ouvrir une PR :
**Settings → Actions → General → Workflow permissions** → cochez
**« Allow GitHub Actions to create and approve pull requests »**.
Sans ça, la création de la PR échoue.

## Premier essai

1. **Génération manuelle** : onglet *Actions* → *Génération hebdomadaire des posts*
   → *Run workflow*.
2. **Relecture** : ouvrez la PR créée, vérifiez les posts, mergez-la.
3. **Publication manuelle** : *Actions* → *Publication quotidienne* → *Run workflow*.
4. Si le post s'affiche correctement sur votre profil, laissez les crons tourner :
   - génération : dimanche 16:23 UTC ;
   - publication : lundi–vendredi 06:17 UTC.

## Renouvellement du jeton (tous les 60 jours)

Les access tokens LinkedIn expirent après **60 jours**. Quand le workflow de
publication échoue avec `Jeton LinkedIn expiré…` (HTTP 401) :

1. Régénérez un token via le *Token Generator* du portail LinkedIn (mêmes scopes).
2. Mettez à jour le secret `LINKEDIN_TOKEN` dans les *Settings* du dépôt.
3. Relancez le workflow *Publication quotidienne* si nécessaire.

## Tests

```bash
pytest
```

Les tests couvrent la validation des posts et `escape_little_text()`.

## Sécurité

Aucun secret n'est stocké dans le dépôt. En local, les scripts chargent `.env`
(via `python-dotenv`) ; en CI, ils lisent les variables d'environnement injectées
depuis les secrets GitHub.
