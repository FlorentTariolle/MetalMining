#!/usr/bin/env python3
"""
Script to recalculate language detection for all songs in dataset.json
using the improved detection algorithm with confidence thresholds.
"""

import json
from pathlib import Path
from langdetect import detect_langs, LangDetectException
from tqdm import tqdm
import sys

def detect_language(text):
    """
    Detect the language of the given text using langdetect.
    Returns 'unknown' if detection fails or text is too short/unreliable.
    
    Improvements:
    - Requires minimum 50 characters for reliable detection
    - Uses confidence scores with minimum threshold of 0.7
    - Handles common instrumental patterns
    """
    if not text or not text.strip():
        return 'unknown'
    
    # Clean the text a bit for better detection
    cleaned_text = text.strip()
    
    # Check for common instrumental patterns (these are too short/unreliable)
    instrumental_patterns = [
        '[instrumental]',
        '[Instrumental]',
        '[INSTRUMENTAL]',
        'instrumental',
        'Instrumental'
    ]
    if cleaned_text.lower() in [p.lower() for p in instrumental_patterns]:
        return 'unknown'
    
    # Require minimum length for reliable detection (increased from 10 to 50)
    # Very short texts can give false positives, especially for Romanian
    if len(cleaned_text) < 50:
        return 'unknown'
    
    try:
        # Use detect_langs to get confidence scores
        detected_langs = detect_langs(cleaned_text)
        
        if not detected_langs:
            return 'unknown'
        
        # Get the top detection with its confidence score
        top_lang = detected_langs[0]
        
        # Require minimum confidence of 0.7
        if top_lang.prob < 0.7:
            return 'unknown'
        
        return top_lang.lang
        
    except LangDetectException:
        return 'unknown'
    except Exception:
        return 'unknown'

def recalculate_languages(dataset_path='data/dataset.json'):
    """
    Recalculate language detection for all songs in the dataset.
    Updates the language field for each song and saves the updated dataset.
    """
    dataset_path = Path(dataset_path)
    
    if not dataset_path.exists():
        print(f"Error: Dataset file not found at {dataset_path}")
        return False
    
    print(f"Loading dataset from {dataset_path}...")
    print("(This may take a moment for large files)")
    
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return False
    
    # Handle nested dataset structure
    if 'dataset' in data:
        dataset = data['dataset']
    else:
        dataset = data
    
    # Count total songs for progress tracking
    total_songs = 0
    for artist_data in dataset.values():
        if 'albums' in artist_data:
            for album_data in artist_data['albums'].values():
                if 'songs' in album_data:
                    total_songs += len(album_data['songs'])
    
    print(f"Found {len(dataset)} artists with {total_songs} total songs")
    print("Recalculating languages...")
    print("=" * 60)
    
    # Track statistics
    language_changes = {}
    language_stats = {}
    songs_processed = 0
    
    # Process each artist
    for artist_name, artist_data in tqdm(dataset.items(), desc="Processing artists", unit="artist"):
        if 'albums' not in artist_data:
            continue
        
        # Process each album
        for album_name, album_data in artist_data['albums'].items():
            if 'songs' not in album_data:
                continue
            
            # Process each song
            for song in album_data['songs']:
                songs_processed += 1
                
                # Get current language
                old_language = song.get('language', 'unknown')
                
                # Recalculate language
                lyrics = song.get('lyrics', '')
                new_language = detect_language(lyrics)
                
                # Update the language field
                song['language'] = new_language
                
                # Track statistics
                language_stats[new_language] = language_stats.get(new_language, 0) + 1
                
                # Track changes
                if old_language != new_language:
                    change_key = f"{old_language} -> {new_language}"
                    language_changes[change_key] = language_changes.get(change_key, 0) + 1
    
    # Save the updated dataset
    print(f"\nSaving updated dataset to {dataset_path}...")
    
    # Reconstruct the original structure
    if 'dataset' in data:
        data['dataset'] = dataset
    else:
        data = dataset
    
    try:
        # Create backup first
        backup_path = dataset_path.with_suffix('.json.backup')
        print(f"Creating backup at {backup_path}...")
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Save the updated dataset
        with open(dataset_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully saved updated dataset!")
        print(f"Backup saved at: {backup_path}")
        
    except Exception as e:
        print(f"Error saving dataset: {e}")
        return False
    
    # Print statistics
    print("\n" + "=" * 60)
    print("Language Recalculation Statistics")
    print("=" * 60)
    print(f"Total songs processed: {songs_processed}")
    
    print("\nLanguage distribution (after recalculation):")
    for lang, count in sorted(language_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / songs_processed) * 100 if songs_processed > 0 else 0
        print(f"   {lang:15s}: {count:6d} songs ({percentage:5.1f}%)")
    
    if language_changes:
        print("\nLanguage changes:")
        for change, count in sorted(language_changes.items(), key=lambda x: x[1], reverse=True):
            print(f"   {change:30s}: {count:6d} songs")
    else:
        print("\nNo language changes detected (all languages were already correct).")
    
    return True

def main():
    """Main function."""
    print("Language Recalculation Tool")
    print("=" * 60)
    
    # Check if langdetect is available
    try:
        from langdetect import detect_langs
    except ImportError:
        print("Error: langdetect module not found!")
        print("Please install it with: pip install langdetect")
        sys.exit(1)
    
    # Check if tqdm is available
    try:
        from tqdm import tqdm
    except ImportError:
        print("Error: tqdm module not found!")
        print("Please install it with: pip install tqdm")
        sys.exit(1)
    
    # Get dataset path from command line or use default
    import argparse
    parser = argparse.ArgumentParser(description="Recalculate language detection for all songs")
    parser.add_argument("-f", "--file", default='data/dataset.json',
                       help="Path to dataset JSON file (default: data/dataset.json)")
    args = parser.parse_args()
    
    # Run the recalculation
    success = recalculate_languages(args.file)
    
    if success:
        print("\n" + "=" * 60)
        print("Language recalculation completed successfully!")
    else:
        print("\n" + "=" * 60)
        print("Language recalculation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

