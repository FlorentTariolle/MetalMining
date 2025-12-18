"""Visualization functions for metal lyrics analysis."""

from .distribution import analyze_lyrics_distribution
from .metrics_plots import (
    line_plot_show,
    scatter_plot_show,
)
from .sentiment_plots import (
    plot_sentiment_distribution,
    plot_artist_scatter_metalness_sentiment,
    build_emotional_arc,
    plot_emotional_arc,
    build_sentiment_path,
    plot_sentiment_path,
)
from .wordcloud import (
    plot_word_cloud,
    plot_word_cloud_Debauchery,
    get_word_frequence_distribution,
)

__all__ = [
    'analyze_lyrics_distribution',
    'line_plot_show',
    'scatter_plot_show',
    'plot_sentiment_distribution',
    'plot_artist_scatter_metalness_sentiment',
    'build_emotional_arc',
    'plot_emotional_arc',
    'build_sentiment_path',
    'plot_sentiment_path',
    'plot_word_cloud',
    'plot_word_cloud_Debauchery',
    'get_word_frequence_distribution',
]
