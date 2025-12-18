import os
from typing import Iterable, List

import pandas as pd

def _get_project_root():
    """Get project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

METALNESS_CANDIDATE_PATHS: List[str] = [
    os.path.join(_get_project_root(), "output_data", "metalness.csv"),
    os.path.join(_get_project_root(), "output_data", "words_metalness.csv"),
]


def _normalize_metalness_df(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    if "Word" not in df.columns and "words" in df.columns:
        rename_map["words"] = "Word"
    if "Metalness" not in df.columns and "metalness" in df.columns:
        rename_map["metalness"] = "Metalness"

    if rename_map:
        df = df.rename(columns=rename_map)

    if {"Word", "Metalness"} - set(df.columns):
        missing_cols = sorted({"Word", "Metalness"} - set(df.columns))
        raise ValueError(
            f"Metalness data is missing required columns: {missing_cols}. "
            f"Expect 'Word' and 'Metalness'."
        )

    return df[["Word", "Metalness"]]


def load_metalness_df(candidate_paths: Iterable[str] = None) -> pd.DataFrame:
    """
    Loads metalness scores from the first existing candidate file.

    Args:
        candidate_paths: Iterable of relative paths to try. Falls back to defaults if None.

    Raises:
        FileNotFoundError: if none of the candidates exist.
        ValueError: if a found file is missing expected columns.
    """
    paths_to_try = list(candidate_paths) if candidate_paths is not None else METALNESS_CANDIDATE_PATHS

    for path in paths_to_try:
        if os.path.exists(path):
            df = pd.read_csv(path)
            return _normalize_metalness_df(df)

    raise FileNotFoundError(
        "Metalness data not found in any of the expected locations "
        f"{paths_to_try}. Run `python -m analysis.process_wordcloud_metalness -f data/dataset.json -o output_pics` "
        "to regenerate the word metalness scores."
    )

