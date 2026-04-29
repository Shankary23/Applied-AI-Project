import sys
from pathlib import Path

# Add src/ to sys.path so that bare imports like `from retriever import ...`
# inside src/recommender.py resolve correctly when pytest runs from the project root.
sys.path.insert(0, str(Path(__file__).parent / "src"))
