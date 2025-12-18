"""Metrics computation for metal lyrics analysis."""

from .swear_words import swear_ratio, load_list
from .readability import readability_cl
from .metalness import compute_metalness, compute_songs_metalness_from_lyrics
from .metallitude import process_idf_scores
from .sentiment import measure_lyrics_sentiment, add_sentiment_index, words_happiness
from .song_metrics import compute_song_metrics

__all__ = [
    'swear_ratio',
    'load_list',
    'readability_cl',
    'compute_metalness',
    'compute_songs_metalness_from_lyrics',
    'process_idf_scores',
    'measure_lyrics_sentiment',
    'add_sentiment_index',
    'words_happiness',
    'compute_song_metrics',
]
