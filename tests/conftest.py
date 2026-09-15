"""Ajoute scripts/ au sys.path pour que les tests importent common / publish_linkedin."""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
