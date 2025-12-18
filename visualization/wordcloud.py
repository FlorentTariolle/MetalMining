"""Word cloud generation functions."""

import os
import string
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk import FreqDist


def _get_project_root():
    """Get project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


STOPWORDS = list(set([str(line.rstrip('\n')) for line in open(os.path.join(_get_project_root(), "resources", "stopwords_eng.txt"), "r")]))
PUNCTUATION = list(string.punctuation) + ['..', '...', '’', "''", '``', '`']


def get_word_frequence_distribution(df: pd.DataFrame, text_column: str = 'lyrics') -> FreqDist:
    """
    Compute word frequency distribution from a text column in the DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing the text data.
        text_column (str): Column name containing the text (lyrics).

    Returns:
        FreqDist: NLTK frequency distribution of words.
    """
    words_corpus = " ".join(df[text_column].dropna().astype(str).values)
    words_corpus = words_corpus.lower().replace('\\n', ' ')
    try:
        tokens = nltk.word_tokenize(words_corpus)
    except LookupError:
        nltk.download('punkt', quiet=True)
        try:
            tokens = nltk.word_tokenize(words_corpus)
        except LookupError:
            tokenizer = RegexpTokenizer(r'\w+')
            tokens = tokenizer.tokenize(words_corpus)

    word_freq_dist = FreqDist(tokens)

    # remove punctuation and stopwords
    for stopword in STOPWORDS:
        if stopword in word_freq_dist:
            del word_freq_dist[stopword]

    for punctuation in PUNCTUATION:
        if punctuation in word_freq_dist:
            del word_freq_dist[punctuation]

    return word_freq_dist


def plot_word_cloud(freq: FreqDist, output_path: str = None) -> None:
    """
    Generate and either save the image or display it.

    Args:
        freq (FreqDist): Word frequency distribution.
        output_path (str, optional): Path to save the word cloud image.
                                     If None, the image will not be saved.
    """
    wordcloud = WordCloud(width=800, height=400, background_color='black').generate_from_frequencies(freq)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Lyrics', fontsize=20)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, bbox_inches='tight')
        print(f"Word cloud saved to {output_path}")
    else:
        plt.show()


def plot_word_cloud_Debauchery(dataframe: pd.DataFrame) -> None:
    """
    Generate and display a word cloud for Debauchery lyrics.
    
    Args:
        dataframe: DataFrame with 'artist' and 'lyrics' columns
    """
    Debauchery_songs = dataframe[dataframe['artist'] == 'Debauchery']
    Debauchery_word_freq_dist = get_word_frequence_distribution(Debauchery_songs, text_column='lyrics')
    plot_word_cloud(Debauchery_word_freq_dist)
    print(Debauchery_word_freq_dist.most_common(20))
    project_root = _get_project_root()
    plt.savefig(os.path.join(project_root, "output_pics", "Debauchery_wordcloud.png"), bbox_inches='tight')
