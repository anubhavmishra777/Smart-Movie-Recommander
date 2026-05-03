from __future__ import annotations

import re
import string
from pathlib import Path

import pandas as pd

try:
    from nltk.stem import PorterStemmer
except ImportError:  # pragma: no cover
    PorterStemmer = None


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = ROOT_DIR / "data" / "movies_raw.csv"
PROCESSED_DATA_PATH = ROOT_DIR / "data" / "movies_processed.csv"

TEXT_COLUMNS = ["genres", "keywords", "overview"]

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "he",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "while",
    "with",
}


def load_movies(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load movie data from CSV."""
    return pd.read_csv(path)


def clean_text(value: str) -> str:
    """Lowercase, remove punctuation, remove stop words, and stem words."""
    text = str(value).lower()
    text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)
    tokens = [token for token in text.split() if token not in STOP_WORDS]

    if PorterStemmer is not None:
        stemmer = PorterStemmer()
        tokens = [stemmer.stem(token) for token in tokens]

    return " ".join(tokens)


def preprocess_movies(movies: pd.DataFrame) -> pd.DataFrame:
    """Prepare movie records for content-based recommendation."""
    processed = movies.copy()

    for column in TEXT_COLUMNS:
        if column not in processed.columns:
            processed[column] = ""
        processed[column] = processed[column].fillna("")

    processed["title"] = processed["title"].fillna("Unknown Title")
    processed["combined_content"] = (
        processed["genres"]
        + " "
        + processed["genres"]
        + " "
        + processed["genres"]
        + " "
        + processed["keywords"]
        + " "
        + processed["keywords"]
        + " "
        + processed["overview"]
    )
    processed["processed_content"] = processed["combined_content"].apply(clean_text)

    output_columns = [
        "movie_id",
        "title",
        "genres",
        "keywords",
        "overview",
        "release_year",
        "vote_average",
        "combined_content",
        "processed_content",
    ]
    return processed[output_columns]


def save_processed_dataset(
    raw_path: Path = RAW_DATA_PATH,
    processed_path: Path = PROCESSED_DATA_PATH,
) -> pd.DataFrame:
    """Create and save the cleaned dataset deliverable."""
    movies = load_movies(raw_path)
    processed = preprocess_movies(movies)
    processed.to_csv(processed_path, index=False)
    return processed


if __name__ == "__main__":
    dataset = save_processed_dataset()
    print(f"Processed {len(dataset)} movies")
    print(f"Saved cleaned dataset to {PROCESSED_DATA_PATH}")
