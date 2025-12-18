#!/usr/bin/env python3
"""
Example script: Dataset distribution analysis.

This script demonstrates how to use the refactored modules to analyze
the distribution of songs, albums, and languages in the metal dataset.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loading import load_music_data
from visualization import analyze_lyrics_distribution


def main():
    """Run dataset distribution analysis."""
    df_songs, df_albums = load_music_data('data/dataset.json')
    analyze_lyrics_distribution(df_songs, df_albums)


if __name__ == "__main__":
    main()
