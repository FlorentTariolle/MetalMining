#!/usr/bin/env python3
"""
Script to merge all progress.json files into a single dataset.json file
with language detection added to each song's lyrics.
"""

import json
from pathlib import Path
from langdetect import detect, LangDetectException
from tqdm import tqdm
import sys

def load_json_file(file_path):
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def detect_language(text):
    """
    Detect the language of the given text using langdetect.
    Returns 'unknown' if detection fails.
    """
    if not text or not text.strip():
        return 'unknown'
    
    try:
        # Clean the text a bit for better detection
        cleaned_text = text.strip()
        if len(cleaned_text) < 10:  # Too short for reliable detection
            return 'unknown'
        
        detected_lang = detect(cleaned_text)
        return detected_lang
    except LangDetectException:
        return 'unknown'
    except Exception:
        return 'unknown'

def add_language_to_songs(songs):
    """Add language detection to all songs in the list."""
    for song in songs:
        if 'lyrics' in song:
            song['language'] = detect_language(song['lyrics'])
        else:
            song['language'] = 'unknown'
    return songs

def merge_progress_files():
    """Merge all progress.json files into a single dataset."""
    
    # Get the data directory
    data_dir = Path('data')
    if not data_dir.exists():
        print("Error: 'data' directory not found!")
        return False
    
    # Find all progress.json files
    progress_files = list(data_dir.glob('progress*.json'))
    if not progress_files:
        print("Error: No progress*.json files found in data directory!")
        return False
    
    print(f"Found {len(progress_files)} progress files to merge:")
    for file in progress_files:
        print(f"  - {file.name}")
    
    # Load artists list to get total count for progress bar
    artists_list_path = data_dir / 'artists_list.json'
    if artists_list_path.exists():
        artists_list = load_json_file(artists_list_path)
        total_artists = len(artists_list) if artists_list else 0
    else:
        total_artists = 0
        print("Warning: artists_list.json not found, progress bar will show file count instead")
    
    # Initialize merged dataset
    merged_dataset = {}
    
    # Process each progress file
    processed_artists = 0
    
    for progress_file in tqdm(progress_files, desc="Processing progress files", unit="file"):
        print(f"\nProcessing {progress_file.name}...")
        
        # Load the progress file
        progress_data = load_json_file(progress_file)
        if not progress_data or 'dataset' not in progress_data:
            print(f"Warning: Skipping {progress_file.name} - invalid format")
            continue
        
        # Get artists from this file
        file_artists = list(progress_data['dataset'].keys())
        print(f"  Found {len(file_artists)} artists in {progress_file.name}")
        
        # Process each artist with progress bar
        for artist_name in tqdm(file_artists, desc=f"Processing artists from {progress_file.name}", 
                              leave=False, unit="artist"):
            
            artist_data = progress_data['dataset'][artist_name]
            
            # Process albums
            if 'albums' in artist_data:
                for album_name, album_data in artist_data['albums'].items():
                    if 'songs' in album_data:
                        # Add language detection to all songs
                        album_data['songs'] = add_language_to_songs(album_data['songs'])
            
            # Add to merged dataset
            merged_dataset[artist_name] = artist_data
            processed_artists += 1
    
    # Save the merged dataset
    output_path = data_dir / 'dataset.json'
    print(f"\nSaving merged dataset to {output_path}...")
    
    try:
        # Wrap the merged dataset in the expected structure
        final_dataset = {"dataset": merged_dataset}
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_dataset, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully created {output_path}")
        print(f"Total artists processed: {processed_artists}")
        print(f"Total artists in merged dataset: {len(merged_dataset)}")
        
        # Show some statistics about language detection
        language_stats = {}
        total_songs = 0
        
        for artist_name, artist_data in merged_dataset.items():
            if 'albums' in artist_data:
                for album_name, album_data in artist_data['albums'].items():
                    if 'songs' in album_data:
                        for song in album_data['songs']:
                            total_songs += 1
                            lang = song.get('language', 'unknown')
                            language_stats[lang] = language_stats.get(lang, 0) + 1
        
        print(f"\nLanguage detection statistics:")
        print(f"   Total songs processed: {total_songs}")
        for lang, count in sorted(language_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_songs) * 100 if total_songs > 0 else 0
            print(f"   {lang}: {count} songs ({percentage:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"Error saving dataset: {e}")
        return False

def main():
    """Main function."""
    print("Metal Mining Dataset Merger")
    print("=" * 40)
    
    # Check if langdetect is available
    try:
        from langdetect import detect
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
    
    # Run the merge process
    success = merge_progress_files()
    
    if success:
        print("\nDataset merging completed successfully!")
    else:
        print("\nDataset merging failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
