"""Aggregation functions for grouping metrics by artist, album, or year."""

from .aggregation import (
    aggregate_by_artist,
    aggregate_by_year,
    aggregate_sentiment_by_artist,
    aggregate_sentiment_by_album,
    build_stupidity_curve,
    top_songs_by_sentiment,
)

__all__ = [
    'aggregate_by_artist',
    'aggregate_by_year',
    'aggregate_sentiment_by_artist',
    'aggregate_sentiment_by_album',
    'build_stupidity_curve',
    'top_songs_by_sentiment',
]
