#!/usr/bin/env python3
"""
Script to clean genres from bands_genres.json.
- Splits genres separated by "/" into separate items
- Removes (early)/(mid)/(later) markers and merges all genres
- Converts genre strings to lists
"""

import json
import re
import argparse
from pathlib import Path


def clean_genre_string(genre_str: str) -> list:
    """
    Clean a genre string and convert it to a list of genres.
    
    Examples:
    - "Heavy/Speed/Power Metal" -> ["Heavy", "Speed", "Power Metal"]
    - "Death Metal (early); Symphonic Black Metal (mid); Extreme Gothic Metal (later)" 
      -> ["Death Metal", "Symphonic Black Metal", "Extreme Gothic Metal"]
    - "Heavy Metal, Hard Rock" -> ["Heavy Metal", "Hard Rock"]
    """
    if not genre_str:
        return []
    
    # Step 1: Split by ";" to handle (early)/(mid)/(later) cases
    parts = [part.strip() for part in genre_str.split(';')]
    
    all_genres = []
    
    for part in parts:
        # Step 2: Remove (early)/(mid)/(later) markers
        part = re.sub(r'\s*\(early\)', '', part, flags=re.IGNORECASE)
        part = re.sub(r'\s*\(mid\)', '', part, flags=re.IGNORECASE)
        part = re.sub(r'\s*\(later\)', '', part, flags=re.IGNORECASE)
        part = re.sub(r'\s*\(early/later\)', '', part, flags=re.IGNORECASE)
        part = part.strip()
        
        if not part:
            continue
        
        # Step 3: Split by "," to separate genres
        comma_parts = [p.strip() for p in part.split(',')]
        
        for comma_part in comma_parts:
            if not comma_part:
                continue
            
            # Step 4: Split by "/" to separate genres
            # Simple approach: split by "/" and each part is a genre
            # e.g., "Heavy/Speed/Power Metal" -> ["Heavy", "Speed", "Power Metal"]
            # e.g., "Heavy Metal/Hard Rock" -> ["Heavy Metal", "Hard Rock"]
            slash_parts = [p.strip() for p in comma_part.split('/')]
            all_genres.extend(slash_parts)
    
    # Step 5: Clean up and deduplicate
    cleaned_genres = []
    seen = set()
    
    for genre in all_genres:
        genre = genre.strip()
        if genre and genre.lower() not in seen:
            cleaned_genres.append(genre)
            seen.add(genre.lower())
    
    return cleaned_genres


def clean_genres_file(input_file: str, output_file: str = None) -> dict:
    """
    Clean genres from a JSON file.
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Load the JSON file
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cleaned_data = {}
    
    for band_name, genre_value in data.items():
        if genre_value is None:
            cleaned_data[band_name] = None
        else:
            cleaned_genres = clean_genre_string(genre_value)
            cleaned_data[band_name] = cleaned_genres if cleaned_genres else None
    
    # Save to output file
    if output_file is None:
        output_file = input_file
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
    
    return cleaned_data


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Clean genres from bands_genres.json"
    )
    parser.add_argument(
        "-i", "--input",
        default="data/bands_genres.json",
        help="Input JSON file (default: data/bands_genres.json)"
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output JSON file (default: overwrites input file)"
    )
    args = parser.parse_args()
    
    print(f"Cleaning genres from {args.input}...")
    cleaned_data = clean_genres_file(args.input, args.output)
    
    output_file = args.output if args.output else args.input
    print(f"Cleaned genres saved to {output_file}")
    
    # Print some statistics
    total_bands = len(cleaned_data)
    bands_with_genres = sum(1 for v in cleaned_data.values() if v is not None)
    bands_with_multiple_genres = sum(1 for v in cleaned_data.values() if v is not None and len(v) > 1)
    
    print(f"\nStatistics:")
    print(f"  Total bands: {total_bands}")
    print(f"  Bands with genres: {bands_with_genres}")
    print(f"  Bands with multiple genres: {bands_with_multiple_genres}")
    
    # Show a few examples
    print(f"\nExample cleaned genres:")
    count = 0
    for band, genres in cleaned_data.items():
        if genres and len(genres) > 1 and count < 5:
            print(f"  {band}: {genres}")
            count += 1


if __name__ == "__main__":
    main()

