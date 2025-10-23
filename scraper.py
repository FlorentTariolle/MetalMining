#!/usr/bin/env python3

"""
Comprehensive script using metalparser to fetch and save the complete dataset from DarkLyrics.
Downloads all artists, their albums, and all songs in each album.
Saves to data/progress{quarter}.json

Supports multi-user scraping with different quarters of the artist list.
Users: Florent (quarter 1), Nizar (quarter 2), Mathis (quarter 3), Rayen (quarter 4)
"""

import argparse
import json
import os
import sys

from metalparser.darklyrics import DarkLyricsApi


def get_user_info(user_name):
	"""
	Get user information including quarter number and progress file name.
	"""
	user_mapping = {
		"Florent": 1,
		"Nizar": 2,
		"Mathis": 3,
		"Rayen": 4
	}
	
	if user_name not in user_mapping:
		raise ValueError(f"Invalid user '{user_name}'. Valid users are: {', '.join(user_mapping.keys())}")
	
	quarter = user_mapping[user_name]
	progress_file = f"progress{quarter}.json"
	
	return quarter, progress_file


def split_artists_by_quarter(artists, quarter):
	"""
	Split the artists list into quarters and return the specified quarter.
	"""
	total_artists = len(artists)
	quarter_size = total_artists // 4
	
	# Calculate start and end indices for the quarter
	if quarter == 1:
		start_idx = 0
		end_idx = quarter_size
	elif quarter == 2:
		start_idx = quarter_size
		end_idx = quarter_size * 2
	elif quarter == 3:
		start_idx = quarter_size * 2
		end_idx = quarter_size * 3
	elif quarter == 4:
		start_idx = quarter_size * 3
		end_idx = total_artists
	else:
		raise ValueError(f"Invalid quarter: {quarter}")
	
	quarter_artists = artists[start_idx:end_idx]
	print(f"Quarter {quarter}: Processing artists {start_idx + 1} to {end_idx} ({len(quarter_artists)} artists)")
	
	return quarter_artists, start_idx


def get_next_user_boundary(quarter, total_artists):
	"""
	Get the starting position of the next user's quarter (the boundary where this user should stop).
	"""
	quarter_size = total_artists // 4
	
	if quarter == 1:
		return quarter_size  # Start of quarter 2
	elif quarter == 2:
		return quarter_size * 2  # Start of quarter 3
	elif quarter == 3:
		return quarter_size * 3  # Start of quarter 4
	elif quarter == 4:
		return total_artists  # End of all artists
	else:
		raise ValueError(f"Invalid quarter: {quarter}")


def fetch_complete_dataset(api, artists, existing_dataset=None, start_position=0, progress_file_name="progress.json", user_boundary=None):
	"""
	Fetch complete dataset: artists, their albums, and all songs.
	Returns a nested dictionary structure.
	"""
	complete_dataset = existing_dataset.copy() if existing_dataset else {}
	total_artists = len(artists) + start_position
	
	for i, artist in enumerate(artists, 1):
		absolute_position = start_position + i
		
		# Check if we've reached the next user's boundary
		if user_boundary is not None and absolute_position > user_boundary:
			print(f"🛑 Reached user boundary at position {absolute_position} (next user starts at {user_boundary + 1})")
			print(f"Stopping processing for this user.")
			break
		
		print(f"[{absolute_position}/{total_artists}] Processing artist: {artist}")
		
		try:
			# Get albums for this artist
			albums = api.get_albums_info(artist, title_only=False) or []
			print(f"  Found {len(albums)} albums")
			
			artist_data = {
				"name": artist,
				"albums": {}
			}
			
			for j, album in enumerate(albums, 1):
				# Extract album name from album object if it's a dict
				if isinstance(album, dict):
					album_name = album.get("title", str(album))
				else:
					album_name = str(album)
				
				print(f"    [{j}/{len(albums)}] Processing album: {album_name}")
				
				try:
					# Get songs for this album
					songs_data = api.get_album_info_and_lyrics(album_name, artist, lyrics_only=False) or []
					print(f"      Found {len(songs_data)} songs")
					
					# Get album metadata from first song (all songs in album have same metadata)
					album_metadata = {
						"release_year": songs_data[0].get("release_year", "") if songs_data else "",
						"album_type": songs_data[0].get("album_type", "") if songs_data else ""
					}
					
					album_data = {
						"name": album_name,
						"release_year": album_metadata["release_year"],
						"album_type": album_metadata["album_type"],
						"songs": []
					}
					
					for song_data in songs_data:
						song_info = {
							"title": song_data.get("title", ""),
							"track_number": song_data.get("track_no", 0),  # Fixed field name to match metalparser
							"lyrics": song_data.get("lyrics", "")
						}
						album_data["songs"].append(song_info)
					
					artist_data["albums"][album_name] = album_data
										
				except Exception as e:
					print(f"      Error processing album '{album_name}': {e}")
					continue
			
			complete_dataset[artist] = artist_data
			
			# Save progress after each artist (for frequent saves)
			save_progress(complete_dataset, absolute_position, total_artists, progress_file_name)
			
		except Exception as e:
			print(f"  Error processing artist '{artist}': {e}")
			continue
	
	return complete_dataset


def save_progress(dataset, current, total, progress_file_name="progress.json"):
	"""Save progress to a user-specific progress file."""
	progress_file = os.path.join("data", progress_file_name)
	
	# Count total albums and songs for progress info
	total_albums = sum(len(artist_data.get("albums", {})) for artist_data in dataset.values())
	total_songs = sum(
		sum(len(album_data.get("songs", [])) for album_data in artist_data.get("albums", {}).values())
		for artist_data in dataset.values()
	)
	
	progress_data = {
		"dataset": dataset,
		"progress": {
			"current": current,
			"total": total,
			"processed_artists": len(dataset),
			"total_albums": total_albums,
			"total_songs": total_songs
		}
	}
	
	with open(progress_file, "w", encoding="utf-8") as f:
		json.dump(progress_data, f, ensure_ascii=False, indent=2)
	
	print(f"  ✅ Progress saved: {current}/{total} artists ({len(dataset)} completed)")
	print(f"     📊 {total_albums} albums, {total_songs} songs collected so far")


def main():
	# Parse command line arguments
	parser = argparse.ArgumentParser(description="Scrape DarkLyrics with multi-user support")
	parser.add_argument("--user", required=True, choices=["Florent", "Nizar", "Mathis", "Rayen"],
						help="User name (Florent, Nizar, Mathis, or Rayen)")
	args = parser.parse_args()
	
	# Get user-specific information
	try:
		quarter, progress_file_name = get_user_info(args.user)
		print(f"User: {args.user} (Quarter {quarter})")
		print(f"Progress file: {progress_file_name}")
	except ValueError as e:
		print(f"Error: {e}")
		return 1
	
	out_dir = os.path.abspath("data")
	os.makedirs(out_dir, exist_ok=True)

	# Initialize dataset variable
	dataset = {}

	# Check for existing complete dataset
	dataset_path = os.path.join(out_dir, "complete_dataset.json")
	if os.path.exists(dataset_path):
		print("Complete dataset already exists!")
		with open(dataset_path, "r", encoding="utf-8") as f:
			dataset = json.load(f)
		print(f"Dataset contains {len(dataset)} artists")
		return 0

	# Check for existing progress (user-specific)
	progress_path = os.path.join(out_dir, progress_file_name)
	if os.path.exists(progress_path):
		print(f"Found existing progress file for {args.user}. Loading...")
		try:
			with open(progress_path, "r", encoding="utf-8") as f:
				progress_data = json.load(f)
			dataset = progress_data.get("dataset", {})
			progress_info = progress_data.get("progress", {})
			current = progress_info.get("current", 0)
			total = progress_info.get("total", 0)
			print(f"Resuming from artist {current}/{total}")
			print(f"Already processed {len(dataset)} artists")
			
			# Keep the progress file for now - we'll update it as we go
		except Exception as e:
			print(f"Error loading progress: {e}")
			dataset = {}

	# Check for existing artists list first
	artists_file = os.path.join(out_dir, "artists_list.json")
	if os.path.exists(artists_file):
		print("Loading existing artists list...")
		try:
			with open(artists_file, "r", encoding="utf-8") as f:
				all_artists = json.load(f) or []
			print(f"Loaded {len(all_artists)} artists from existing file")
		except (json.JSONDecodeError, IOError) as e:
			print(f"Error loading artists file: {e}")
			all_artists = []
	else:
		# Initialize API and fetch artists list
		api = DarkLyricsApi(use_cache=False)
		print("Fetching artists list...")
		all_artists = api.get_artists_list() or []
		print(f"Found {len(all_artists)} artists")
		
		# Save artists list to avoid losing it
		with open(artists_file, "w", encoding="utf-8") as f:
			json.dump(all_artists, f, ensure_ascii=False, indent=2)
		print(f"Saved artists list to: {artists_file}")
	
	# Get user's quarter of artists
	artists, quarter_start_idx = split_artists_by_quarter(all_artists, quarter)
	
	# Calculate the boundary where this user should stop (start of next user's quarter)
	user_boundary = get_next_user_boundary(quarter, len(all_artists))
	print(f"User boundary: Will stop at position {user_boundary} (before next user's quarter)")
	
	# Initialize API for dataset fetching
	api = DarkLyricsApi(use_cache=False)

	# If we have existing dataset, filter out already processed artists
	start_position = 0
	if dataset:
		processed_artists = set(dataset.keys())
		remaining_artists = [artist for artist in artists if artist not in processed_artists]
		start_position = quarter_start_idx + len(artists) - len(remaining_artists)
		print(f"Resuming with {len(remaining_artists)} remaining artists from quarter {quarter} (starting from position {start_position + 1})")
		artists = remaining_artists
	else:
		start_position = quarter_start_idx

	if not artists:
		print(f"No artists to process for {args.user}!")
		return 0

	# Fetch complete dataset
	print(f"Starting dataset fetch for {args.user} (Quarter {quarter})...")
	final_dataset = fetch_complete_dataset(api, artists, dataset, start_position, progress_file_name, user_boundary)

	# Save user-specific dataset in the format expected by merge script
	user_dataset_path = os.path.join(out_dir, f"progress{quarter}.json")
	print(f"Saving {args.user}'s dataset...")
	
	# Wrap the dataset in the format expected by merge_progress_files.py
	dataset_wrapper = {"dataset": final_dataset}
	
	with open(user_dataset_path, "w", encoding="utf-8") as f:
		json.dump(dataset_wrapper, f, ensure_ascii=False, indent=2)
	
	# Clean up progress file if it exists
	if os.path.exists(progress_path):
		os.remove(progress_path)
	
	print(f"{args.user}'s dataset saved to: {user_dataset_path}")
	print(f"Total artists processed by {args.user}: {len(final_dataset)}")
	
	# Count total albums and songs
	total_albums = sum(len(artist_data.get("albums", {})) for artist_data in final_dataset.values())
	total_songs = sum(
		sum(len(album_data.get("songs", [])) for album_data in artist_data.get("albums", {}).values())
		for artist_data in final_dataset.values()
	)
	
	print(f"Total albums: {total_albums}")
	print(f"Total songs: {total_songs}")

	return 0


if __name__ == "__main__":
	try:
		sys.exit(main())
	except KeyboardInterrupt:
		print("\nEnd of scraping")
		sys.exit(0)
