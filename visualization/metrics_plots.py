"""Visualization functions for metrics analysis (swear words, readability, etc.)."""

import matplotlib.pyplot as plt
import pandas as pd


def line_plot_show(df: pd.DataFrame, x: str, y: str, xlabel: str, ylabel: str, title: str, figsize=(12, 6)) -> None:
    """
    Plot a simple line chart and display it.
    
    Args:
        df: DataFrame with data to plot
        x: Column name for x-axis
        y: Column name for y-axis
        xlabel: Label for x-axis
        ylabel: Label for y-axis
        title: Plot title
        figsize: Figure size tuple
    """
    plt.figure(figsize=figsize)
    plt.plot(df[x].values, df[y].values, marker="o")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.show()


def scatter_plot_show(df: pd.DataFrame, x: str, y: str, xlabel: str, ylabel: str, title: str, figsize=(10, 10)) -> None:
    """
    Plot a simple scatter plot and display it.
    
    Args:
        df: DataFrame with data to plot
        x: Column name for x-axis
        y: Column name for y-axis
        xlabel: Label for x-axis
        ylabel: Label for y-axis
        title: Plot title
        figsize: Figure size tuple
    """
    plt.figure(figsize=figsize)
    plt.scatter(df[x].values, df[y].values, s=25, alpha=0.7)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.show()
