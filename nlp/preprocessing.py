import re
from functools import lru_cache

import nltk
import spacy
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


def _has_nltk_resource(resource: str) -> bool:
    try:
        nltk.data.find(resource)
        return True
    except LookupError:
        return False


@lru_cache(maxsize=1)
def load_spacy_model():
    """Load spaCy model with a blank fallback for fully offline execution."""
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        return spacy.blank("en")


@lru_cache(maxsize=1)
def get_stop_words() -> set[str]:
    try:
        if not _has_nltk_resource("corpora/stopwords"):
            raise LookupError
        return set(stopwords.words("english"))
    except Exception:
        return {
            "a",
            "an",
            "the",
            "and",
            "or",
            "to",
            "of",
            "in",
            "for",
            "with",
            "on",
            "by",
            "is",
            "are",
        }


def clean_text(text: str) -> str:
    """Normalize text for matching and analysis."""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-z0-9+#.\s-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_text(text: str) -> list[str]:
    """Tokenize using NLTK with a regex fallback."""
    cleaned = clean_text(text)
    try:
        if not _has_nltk_resource("tokenizers/punkt"):
            raise LookupError
        tokens = word_tokenize(cleaned)
    except Exception:
        tokens = re.findall(r"[a-z0-9+#.-]+", cleaned)
    return tokens


def lemmatize_tokens(tokens: list[str]) -> list[str]:
    """Lemmatize tokens with NLTK and spaCy fallbacks."""
    stop_words = get_stop_words()
    filtered_tokens = [token for token in tokens if token not in stop_words and len(token) > 1]
    try:
        if not _has_nltk_resource("corpora/wordnet"):
            raise LookupError
        lemmatizer = WordNetLemmatizer()
        return [lemmatizer.lemmatize(token) for token in filtered_tokens]
    except Exception:
        nlp = load_spacy_model()
        doc = nlp(" ".join(filtered_tokens))
        return [token.lemma_ if token.lemma_ else token.text for token in doc]


def preprocess_text(text: str) -> str:
    """Clean, tokenize, remove stopwords, and lemmatize text."""
    tokens = tokenize_text(text)
    lemmas = lemmatize_tokens(tokens)
    return " ".join(lemmas)
