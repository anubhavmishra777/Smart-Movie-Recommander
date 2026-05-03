from __future__ import annotations

from dataclasses import dataclass
from difflib import get_close_matches
from collections import Counter
from base64 import b64encode
import math
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

import pandas as pd

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:  # pragma: no cover
    TfidfVectorizer = None
    cosine_similarity = None

from src.preprocessing import PROCESSED_DATA_PATH, save_processed_dataset


POSTER_URLS = {
    "Inception": "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
    "Interstellar": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
    "The Dark Knight": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
    "The Matrix": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
    "Avatar": "https://image.tmdb.org/t/p/w500/kyeqWdyUXW608qlYkRqosgbbJyK.jpg",
    "The Lord of the Rings: The Fellowship of the Ring": "https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg",
    "The Lord of the Rings: The Return of the King": "https://image.tmdb.org/t/p/w500/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg",
    "Harry Potter and the Sorcerer's Stone": "https://image.tmdb.org/t/p/w500/wuMc08IPKEatf9rnMNXvIDxqP4dR.jpg",
    "The Avengers": "https://image.tmdb.org/t/p/w500/RYMX2wcKCBAr24UyPD7xwmjaTn.jpg",
    "Iron Man": "https://image.tmdb.org/t/p/w500/78lPtwv72eTNqFW9COBYI0dWDJa.jpg",
    "Guardians of the Galaxy": "https://image.tmdb.org/t/p/w500/r7vmZjiyZw9rpJMQJdXpjgiCOk9.jpg",
    "Star Wars: A New Hope": "https://image.tmdb.org/t/p/w500/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg",
    "Star Wars: The Empire Strikes Back": "https://image.tmdb.org/t/p/w500/nNAeTmF4CtdSgMDplXTDPOpYzsX.jpg",
    "Jurassic Park": "https://image.tmdb.org/t/p/w500/9i3plLl89DHMz7mahksDaAo7HIS.jpg",
    "Toy Story": "https://image.tmdb.org/t/p/w500/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
    "Finding Nemo": "https://image.tmdb.org/t/p/w500/eHuGQ10FUzK1mdOY69wF5pGgEf5.jpg",
    "Coco": "https://image.tmdb.org/t/p/w500/gGEsBPAijhVUFoiNpgZXqRVWJt2.jpg",
    "WALL-E": "https://image.tmdb.org/t/p/w500/hbhFnRzzg6ZDmm8YAmxBnQpQIPh.jpg",
    "Titanic": "https://image.tmdb.org/t/p/w500/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg",
    "The Notebook": "https://image.tmdb.org/t/p/w500/qom1SZSENdmHFNZBXbtJAU0WTlC.jpg",
    "La La Land": "https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg",
    "A Star Is Born": "https://image.tmdb.org/t/p/w500/wrFpXMNBRj2PBiN4Z5kix51XaIZ.jpg",
    "The Social Network": "https://image.tmdb.org/t/p/w500/n0ybibhJtQ5icDqTp8eRytcIHJx.jpg",
    "The Imitation Game": "https://image.tmdb.org/t/p/w500/zSqJ1qFq8NXFfi7JeIYMlzyR0dx.jpg",
    "Forrest Gump": "https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg",
    "The Shawshank Redemption": "https://image.tmdb.org/t/p/w500/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg",
    "Fight Club": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZDIK0hQQm.jpg",
    "Shutter Island": "https://image.tmdb.org/t/p/w500/4GDy0PHYX3VRXUtwK5ysFbg3kEx.jpg",
    "Gone Girl": "https://image.tmdb.org/t/p/w500/lv5xShBIDPe7m4ufdlV0IAc7Avk.jpg",
    "Se7en": "https://image.tmdb.org/t/p/w500/191nKfP0ehp3uIvWqgPbFmI4lv9.jpg",
    "The Silence of the Lambs": "https://image.tmdb.org/t/p/w500/uS9m8OBk1A8eM9I042bx8XXpqAq.jpg",
    "Knives Out": "https://image.tmdb.org/t/p/w500/pThyQovXQrw2m0s9x82twj48Jq4.jpg",
    "Parasite": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
    "Joker": "https://image.tmdb.org/t/p/w500/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg",
    "The Godfather": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
    "Goodfellas": "https://image.tmdb.org/t/p/w500/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg",
    "The Departed": "https://image.tmdb.org/t/p/w500/nT97ifVT2J1yMQmeq20Qblg61T.jpg",
    "Spirited Away": "https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg",
    "Your Name": "https://image.tmdb.org/t/p/w500/q719jXXEzOoYaps6babgKnONONX.jpg",
    "Black Panther": "https://image.tmdb.org/t/p/w500/uxzzxijgPIY7slzFvMotPv8wjKA.jpg",
    "Doctor Strange": "https://image.tmdb.org/t/p/w500/uGBVj3bEbCoZbDjjl9wTxcygko1.jpg",
    "Mad Max: Fury Road": "https://image.tmdb.org/t/p/w500/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg",
    "The Martian": "https://image.tmdb.org/t/p/w500/3ndAx3weG6KDkJIRMCi5vXX6Dyb.jpg",
    "Gravity": "https://image.tmdb.org/t/p/w500/kZ2nZw8D681aphje8NJi8EfbL1U.jpg",
    "Whiplash": "https://image.tmdb.org/t/p/w500/7fn624j5lj3xTme2SgiLCeuedmO.jpg",
    "Inside Out": "https://image.tmdb.org/t/p/w500/2H1TmgdfNtsKlU9jKdeNyYL5y8T.jpg",
}


@dataclass(frozen=True)
class RecommendationResult:
    title: str
    genres: str
    release_year: int
    vote_average: float
    similarity_score: float
    overview: str
    poster_url: str


class MovieRecommender:
    """Content-based recommender using TF-IDF and cosine similarity."""

    def __init__(self, data_path: Path = PROCESSED_DATA_PATH) -> None:
        if not data_path.exists():
            save_processed_dataset(processed_path=data_path)

        self.movies = pd.read_csv(data_path)
        self.movies["processed_content"] = self.movies["processed_content"].fillna("")
        self.vectorizer = None
        self.feature_matrix = None
        self.cosine_sim_matrix = self._build_similarity_matrix()
        self.title_to_index = {
            title.lower(): index for index, title in enumerate(self.movies["title"].tolist())
        }

    def _build_similarity_matrix(self):
        """Use scikit-learn when available, otherwise use a lightweight local TF-IDF."""
        documents = self.movies["processed_content"].tolist()

        if TfidfVectorizer is not None and cosine_similarity is not None:
            self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
            self.feature_matrix = self.vectorizer.fit_transform(documents)
            return cosine_similarity(self.feature_matrix, self.feature_matrix)

        self.feature_matrix = _build_tfidf_vectors(documents)
        return _cosine_similarity_matrix(self.feature_matrix)

    @property
    def titles(self) -> list[str]:
        return self.movies["title"].tolist()

    @staticmethod
    def poster_url(title: str) -> str:
        """Return a poster URL, with a local SVG fallback for unknown titles."""
        if title in POSTER_URLS:
            return POSTER_URLS[title]

        safe_title = xml_escape(title[:30])
        svg = f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="420" height="630" viewBox="0 0 420 630">
            <defs>
                <linearGradient id="g" x1="0" x2="1" y1="0" y2="1">
                    <stop stop-color="#ff4d5a"/>
                    <stop offset="0.52" stop-color="#172331"/>
                    <stop offset="1" stop-color="#22d3c5"/>
                </linearGradient>
            </defs>
            <rect width="420" height="630" fill="url(#g)"/>
            <circle cx="335" cy="80" r="90" fill="#ffffff" opacity="0.12"/>
            <circle cx="55" cy="565" r="125" fill="#ffffff" opacity="0.10"/>
            <text x="34" y="74" fill="#fff8ee" font-family="Arial" font-size="24" font-weight="700">SMART PICK</text>
            <text x="34" y="315" fill="#fff8ee" font-family="Arial" font-size="34" font-weight="800">{safe_title[:28]}</text>
            <text x="34" y="578" fill="#fff8ee" font-family="Arial" font-size="18">Content-based match</text>
        </svg>
        """
        encoded_svg = b64encode(svg.encode("utf-8")).decode("ascii")
        return f"data:image/svg+xml;base64,{encoded_svg}"

    def find_best_title(self, movie_title: str) -> str | None:
        """Return exact or closest known movie title."""
        query = movie_title.strip().lower()
        if query in self.title_to_index:
            return self.movies.loc[self.title_to_index[query], "title"]

        matches = get_close_matches(query, self.title_to_index.keys(), n=1, cutoff=0.55)
        if not matches:
            return None

        return self.movies.loc[self.title_to_index[matches[0]], "title"]

    def get_recommendations(
        self,
        movie_title: str,
        top_n: int = 10,
    ) -> tuple[str | None, list[RecommendationResult]]:
        """Return top N similar movies for a given title."""
        matched_title = self.find_best_title(movie_title)
        if matched_title is None:
            return None, []

        movie_index = self.title_to_index[matched_title.lower()]
        similarity_scores = list(enumerate(self.cosine_sim_matrix[movie_index]))
        similarity_scores = sorted(similarity_scores, key=lambda item: item[1], reverse=True)

        recommendations: list[RecommendationResult] = []
        for index, score in similarity_scores:
            if index == movie_index:
                continue

            row = self.movies.iloc[index]
            recommendations.append(
                RecommendationResult(
                    title=row["title"],
                    genres=row["genres"],
                    release_year=int(row["release_year"]),
                    vote_average=float(row["vote_average"]),
                    similarity_score=round(float(score), 4),
                    overview=row["overview"],
                    poster_url=self.poster_url(row["title"]),
                )
            )

            if len(recommendations) == top_n:
                break

        return matched_title, recommendations


def get_recommendations(
    movie_title: str,
    cosine_sim_matrix=None,
    movies_df: pd.DataFrame | None = None,
    top_n: int = 10,
) -> list[str]:
    """Guideline-compatible helper returning only movie titles."""
    if cosine_sim_matrix is not None and movies_df is not None:
        titles = movies_df["title"].tolist()
        title_to_index = {title.lower(): index for index, title in enumerate(titles)}
        query = movie_title.strip().lower()
        if query not in title_to_index:
            return []

        movie_index = title_to_index[query]
        scores = list(enumerate(cosine_sim_matrix[movie_index]))
        scores = sorted(scores, key=lambda item: item[1], reverse=True)
        return [titles[index] for index, _ in scores if index != movie_index][:top_n]

    recommender = MovieRecommender()
    _, results = recommender.get_recommendations(movie_title, top_n=top_n)
    return [result.title for result in results]


def _build_tfidf_vectors(documents: list[str]) -> list[dict[str, float]]:
    tokenized_docs = [document.split() for document in documents]
    doc_count = len(tokenized_docs)
    document_frequency: Counter[str] = Counter()

    for tokens in tokenized_docs:
        document_frequency.update(set(tokens))

    vectors: list[dict[str, float]] = []
    for tokens in tokenized_docs:
        term_frequency = Counter(tokens)
        total_terms = max(len(tokens), 1)
        vector: dict[str, float] = {}

        for term, count in term_frequency.items():
            tf = count / total_terms
            idf = math.log((1 + doc_count) / (1 + document_frequency[term])) + 1
            vector[term] = tf * idf

        vectors.append(vector)

    return vectors


def _cosine_similarity_matrix(vectors: list[dict[str, float]]) -> list[list[float]]:
    norms = [
        math.sqrt(sum(weight * weight for weight in vector.values())) for vector in vectors
    ]
    matrix: list[list[float]] = []

    for left_index, left_vector in enumerate(vectors):
        row: list[float] = []
        for right_index, right_vector in enumerate(vectors):
            shared_terms = set(left_vector).intersection(right_vector)
            dot_product = sum(left_vector[term] * right_vector[term] for term in shared_terms)
            denominator = norms[left_index] * norms[right_index]
            row.append(dot_product / denominator if denominator else 0.0)
        matrix.append(row)

    return matrix


if __name__ == "__main__":
    engine = MovieRecommender()
    matched, sample_results = engine.get_recommendations("Inception", top_n=5)
    print(f"Input matched to: {matched}")
    for rank, result in enumerate(sample_results, start=1):
        print(f"{rank}. {result.title} ({result.similarity_score})")
