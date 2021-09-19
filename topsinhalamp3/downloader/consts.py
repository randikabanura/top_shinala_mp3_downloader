# Website consts
first_chrs = 'abcdefghijklmnopqrstuvwxyz0123456789()'
base_url = 'https://www.topsinhalamp3.com/'
base_letter_url = 'https://www.topsinhalamp3.com/music/'
full_letter_url = 'https://www.topsinhalamp3.com/music/artists-a-to-z.php'
base_artist_url = 'https://www.topsinhalamp3.com/artists/'
base_song_url = 'https://www.topsinhalamp3.com/songs/'
new_sinhala_base_url = 'https://www.newsinhalamp3.com/'
new_sinhala_categories_url = 'https://www.newsinhalamp3.com/categories/'
top_25_month_url = 'https://www.newsinhalamp3.com/categories/top-25-new-sinhala-mp3-songs.php'
new_sinhala_month_url = 'https://www.newsinhalamp3.com/categories/new-sinhala-mp3-songs.php'
artist_letter_based_regex = r"^[a-zA-Z]{1}$"
artists_per_page = 25
songs_per_page = 50

# Download configs
file_download_path = './downloads'
update_mp3_tag = True
cover_art_generation = True
cover_art_only_album = True
cover_art_delete_after_attached = True

# Database configs
database_enabled = False
database_host = 'localhost'
database_username = 'root'
database_password = ''
database_name = 'mp3_scraping'

# s3 upload
enabled_s3_upload = False
keep_local_file_after_download = False
bucket_name = 'media'  # Bucket must be available
bucket_endpoint = ''  # Can use AWS S3, DigitalOcean spaces, Wasabi S3 and other S3 compatible services
access_key = ''  # Need to have write access
secret_access_key = ''  # Need to have write access
