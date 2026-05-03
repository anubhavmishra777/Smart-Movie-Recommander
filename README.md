Smart Movie Recommender
A Python-based web application that recommends movies from a predefined dataset using content-based filtering. The system combines movie genres, keywords, and plot overview, converts the text into TF-IDF vectors, and ranks similar movies with cosine similarity.

Features
Search by movie title
Fuzzy title matching for small typing mistakes
Content-based recommendations using genres, keywords, and overview text
Cinematic search interface with poster/photo result cards
Quick vibe buttons for instant demo searches
Streamlit interface plus a dependency-free built-in web version
Reproducible preprocessing script
Processed dataset deliverable
Notebook, report, and presentation material included
Project Structure
Smart Movie Recommender/
|-- app.py
|-- requirements.txt
|-- data/
|   |-- movies_raw.csv
|   `-- movies_processed.csv
|-- docs/
|   |-- project_report.md
|   `-- presentation_outline.md
|-- notebooks/
|   `-- movie_recommender_workflow.ipynb
|-- src/
|   |-- __init__.py
|   |-- preprocessing.py
|   `-- recommender.py
`-- tests/
    `-- test_recommender.py
Setup
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
If virtual environment creation fails on Windows with a PermissionError in AppData\Local\Temp, the project can still run with the system Python as long as the packages in requirements.txt are installed there.

Prepare Dataset
python -m src.preprocessing
This creates data/movies_processed.csv.

Run Web Application
Recommended Streamlit version:

python -m streamlit run app.py
Open the local URL shown by Streamlit, usually http://localhost:8501.

Dependency-free local version:

python simple_web_app.py
Open http://127.0.0.1:8000.

Run Tests
python -m pytest
Methodology
Load raw movie data using Pandas.
Clean missing values in text columns.
Combine genres, keywords, and overview into a single content field.
Preprocess text using lowercasing, punctuation removal, stop-word removal, and stemming.
Convert processed content into numerical vectors using TF-IDF.
Calculate cosine similarity between movies.
Return top similar movie titles for a user-provided movie.
Author
Created by Anubhav Mishra
