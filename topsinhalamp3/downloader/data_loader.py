import urllib.request as urllib2
import urllib.parse as urlparse
import boto3
from botocore.exceptions import ClientError
from bs4 import BeautifulSoup
from .consts import *
import shutil
from urllib.error import URLError
import os
import eyed3
from pkg_resources import resource_stream

from .covers.covers import generate_covers
from .database.song_reg import SongREG
from .utils import get_cover_art_image_path, get_cover_art_from_s3, update_covers_config


class DataLoader(object):

    def __init__(self, download_dir: str):
        page = urllib2.urlopen(base_url).read()
        soup = BeautifulSoup(page, 'html.parser')
        soup.prettify()
        self.__soup = soup
        self.__download_dir = download_dir

    def set_soup(self, url: str):
        try:
            page = urllib2.urlopen(url).read()
            soup = BeautifulSoup(page, 'html.parser')
            soup.prettify()
            self.__soup = soup
        except URLError as e:
            if hasattr(e, 'reason'):
                print('We failed to reach a server.')
                print('Reason: ', e.reason)
            elif hasattr(e, 'code'):
                print('The server couldn\'t fulfill the request.')
                print('Error code: ', e.code)
        except Exception as e:
            print("Error Occurred. Reason:\n", e)

    def __download_file(self, url: str, directory: str, name: str, values: dict):
        try:
            if database_enabled:
                print("Database is enabled")
                song_database = SongREG(database_host, database_username, database_password, database_name)
                downloadable = song_database.store(values)

                if downloadable is None:
                    downloadable = False

                if downloadable is False and (not os.path.isfile(name)):
                    downloadable = True

                print("Song downloadable:", downloadable)
            else:
                print("Database is not enabled")
                downloadable = True

            if (not downloadable or os.path.isfile(name)) and force_downloadable is False:
                print("File already there.. Going to next :)")
                return
            else:
                if not os.path.exists(directory):
                    os.makedirs(directory)

            try:
                if enabled_s3_upload:
                    session = boto3.session.Session()
                    client = session.client('s3',
                                            endpoint_url=bucket_endpoint,
                                            aws_access_key_id=access_key,
                                            aws_secret_access_key=secret_access_key)

                    client.head_object(Bucket=bucket_name, Key=values['s3_directory'])
                else:
                    print("Request URL: ", url)
                    response = urllib2.urlopen(url)
                    with open(name, 'wb') as out_file:
                        shutil.copyfileobj(response, out_file)

                    print("Successfully download Song: ", name)

                    if update_mp3_tag:
                        self.mp3_tag_update(name, values)
                        print("Successfully MP3 tags updated")
            except ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print("Request URL: ", url)
                    response = urllib2.urlopen(url)
                    with open(name, 'wb') as out_file:
                        shutil.copyfileobj(response, out_file)

                    print("Successfully download Song: ", name)

                    if update_mp3_tag:
                        self.mp3_tag_update(name, values)
                        print("Successfully MP3 tags updated")

                    if enabled_s3_upload:
                        self.upload_to_s3_bucket(name, values)
                else:
                    raise e
            else:
                if enabled_s3_upload and force_downloadable is False:
                    print("File already there.. Going to next :)")
                else:
                    print("Request URL: ", url)
                    response = urllib2.urlopen(url)
                    with open(name, 'wb') as out_file:
                        shutil.copyfileobj(response, out_file)

                    print("Successfully download Song: ", name)

                    if update_mp3_tag:
                        self.mp3_tag_update(name, values)
                        print("Successfully MP3 tags updated")

                    if enabled_s3_upload:
                        self.upload_to_s3_bucket(name, values)

        except URLError as e:
            if hasattr(e, 'reason'):
                print('We failed to reach a server.')
                print('Reason: ', e.reason)
            elif hasattr(e, 'code'):
                print('The server couldn\'t fulfill the request.')
                print('Error code: ', e.code)
        except Exception as e:
            print("Error Occurred. Reason:\n", e)

    def upload_to_s3_bucket(self, path: str, values: dict = {}):
        print('Upload to S3 bucket initiated')

        try:
            s3_directory = values['s3_directory']
            s3_folder_image_directory = values['s3_folder_image_directory']
            folder_image_directory = os.path.join(values['directory'], "folder.jpg")

            session = boto3.session.Session()
            client = session.client('s3',
                                    endpoint_url=bucket_endpoint,
                                    aws_access_key_id=access_key,
                                    aws_secret_access_key=secret_access_key)

            try:
                client.head_object(Bucket=bucket_name, Key=s3_directory)
            except ClientError as e:
                if e.response['Error']['Code'] == "404":
                    client.upload_file(path, bucket_name, s3_directory)
                    print('Upload to S3 successful')
                else:
                    raise e
            else:
                if force_downloadable is False:
                    print('File already exists')
                else:
                    client.upload_file(path, bucket_name, s3_directory)
                    print('Upload to S3 successful')

            try:
                client.head_object(Bucket=bucket_name, Key=s3_folder_image_directory)
            except ClientError as e:
                if e.response['Error']['Code'] == "404":
                    client.upload_file(folder_image_directory, bucket_name, s3_folder_image_directory)
                    print('Upload folder image to S3 successful')
                else:
                    raise e
            else:
                print('File folder image already exists')

        except Exception as e:
            print("Upload unsuccessful. Error Occurred. Reason:\n", e)

        if not keep_local_file_after_download:
            os.remove(path)

    def download_file_from_url(self, song_details: dict = {}):
        self.set_soup(song_details['url'])

        if song_details['song_type'].lower() == 'month':
            source = self.__soup.find('div', id='nsmp3-player').find(class_='player-source')
        else:
            source = self.__soup.find('div', id='tsmp3-player').find(class_='player-source')

        if source is None or source.get('data-src') is None or source.get('data-src') == '#':
            print('Source URL: ', source, 'does not have a valid  url')
            return

        source_link = source.get('data-src')

        try:
            source_id = urlparse.parse_qs(urlparse.urlparse(source_link).query)['id'][0]
            song_artist_details = self.__soup.find('ul', class_='song_details').select('li')[1].find(text=True,
                                                                                                     recursive=False).strip()
            song_description = self.__soup.find('ul', class_='song_raw_data').select('li')[2].find(text=True,
                                                                                                   recursive=False).strip()
            song_genre = self.__soup.find('ul', class_='song_raw_data').select('li')[5].find(text=True,
                                                                                             recursive=False).strip()

            if song_details['song_type'].lower() == 'month':
                directory = "{}/{}/{}".format(self.__download_dir, 'NewSinhalaMP3', song_details['artist'])
                s3_directory_format = "{}/{}".format('NewSinhalaMP3', song_details['artist'])
            else:
                directory = "{}/{}/{}".format(self.__download_dir, 'TopSinhalaMP3', song_details['artist'])
                s3_directory_format = "{}/{}".format('TopSinhalaMP3', song_details['artist'])

            file_name = "{}/{}{}".format(directory, song_details['name'], '.mp3')
            s3_directory = "{}/{}{}".format(s3_directory_format, song_details['name'], '.mp3')
            s3_folder_image_directory = "{}/{}".format(s3_directory_format, 'folder.jpg')

            directory = os.path.expandvars(directory)
            file_name = os.path.expandvars(file_name)
        except:
            print("Error occurred when downloading Song:", song_details['name'])
            return

        song_values = {
            'source_id': source_id,
            'artist_description': song_artist_details,
            'artist_name': song_details['artist'],
            'item_url': song_details['item_url'],
            'song_name': song_details['name'],
            'song_url': source_link,
            'song_description': song_description,
            's3_directory': s3_directory,
            'path': file_name,
            'type': song_details['song_type'],
            'image_url': song_details['song_image_url'],
            's3_folder_image_directory': s3_folder_image_directory,
            'directory': directory,
            'bar': song_details['bar']
        }

        self.__download_file(source_link, directory, file_name, song_values)

    def get_months_list_from_url(self, url):
        self.set_soup(url)
        months_list = []
        count = 0

        months_container_list = self.__soup.find_all('div', class_="months_container")
        for i, month_container in enumerate(months_container_list):
            if month_container is None:
                continue

            year_month_list = month_container.find_all('a', attrs={'class': None})
            for j, year_month in enumerate(year_month_list):
                if year_month is None or year_month.get('href') == '#':
                    continue

                count += 1

                values = {
                    'index': count,
                    'name': year_month.text,
                    'url': new_sinhala_categories_url + year_month.get('href')
                }

                months_list.append(values)

        return months_list

    def get_artist_letters_from_url(self, url: str, letter: str = None):
        self.set_soup(url)
        artist_letter_list = self.__soup.find_all('a', class_='artist_letter')
        letter_list = []
        for i, artist_letter in enumerate(artist_letter_list):
            if letter is not None and artist_letter.text.lower() != letter:
                continue

            print('Artist Letter: ', artist_letter.text)

            if artist_letter.get('href') is None or artist_letter.get('href') == '#':
                print('Artist Letter: ', artist_letter.text, 'does not have a valid  url')
                continue

            values = {
                'index': int(i),
                'name': artist_letter.text,
                'url': base_letter_url + artist_letter.get('href')
            }
            letter_list.append(values)
        return letter_list

    def get_name_list_from_url(self, url: str, get_next_page: bool = True, page: int = 1):
        self.set_soup(url)
        artist_name_list = self.__soup.find('ol', class_='list_of_songs').find_all('a', attrs={'class': None})
        artist_list = []
        for i, artist in enumerate(artist_name_list):
            print('Artist Name: ', artist.text)
            values = {
                'page': int(page),
                'index': (artists_per_page * int(page - 1)) + int(i + 1),
                'name': artist.text,
                'url': base_url + artist.get('href').split('/', 1)[-1],
                'no_of_songs': artist.next_sibling.next_sibling.text or ''
            }
            artist_list.append(values)

        if get_next_page:
            next_pages = self.__soup.find(class_='bottom_navigation_bar').find_all(class_='bnav_button')

            for next_page in next_pages:
                next_page_url = base_letter_url + next_page.get('href')

                if next_page.text.lower() == 'previous' or next_page.text.lower() == 'next':
                    continue

                next_page_no = int(next_page.text)
                next_page_artist_list = self.get_name_list_from_url(next_page_url, False, next_page_no)

                for next_page_name in next_page_artist_list:
                    artist_list.append(next_page_name)

        return artist_list

    def get_songs_list_from_url(self, url: str, artist: str, get_next_page: bool = True, page: int = 1,
                                song_type: str = 'Artist', image_url: str = ''):
        self.set_soup(url)
        songs_name_list = self.__soup.find('ol', class_='list_of_songs').find_all('a', attrs={'class': None})
        songs_list = []
        if cover_art_generation:
            if page == 1 and (keep_cover_in_s3_bucket is False):
                print("Please enter a url for a '{}' image (Otherwise default image will be used)".format(artist))
                image_url = input('>>> ')
        else:
            image_url = None

        if image_url is None or image_url.strip() == '':
            image_url = None

        for i, song in enumerate(songs_name_list):
            print('Song Name: ', song.text)

            values = {
                'page': int(page),
                'index': (songs_per_page * int(page - 1)) + int(i + 1),
                'item': artist,
                'item_url': url,
                'song': song.text,
                'url': base_url + song.get('href').split('/', 1)[-1],
                'image_url': image_url
            }

            if song_type.lower() == 'month':
                values['url'] = new_sinhala_base_url + song.get('href').split('/', 1)[-1]

            songs_list.append(values)

        if get_next_page:
            navigation_bar = self.__soup.find(class_='bottom_navigation_bar')
            if navigation_bar is None:
                return songs_list

            next_pages = navigation_bar.find_all(class_='bnav_button')

            for next_page in next_pages:
                if song_type.lower() == 'month':
                    next_page_url = new_sinhala_categories_url + next_page.get('href')
                else:
                    next_page_url = base_artist_url + next_page.get('href')

                if next_page.text.lower() == 'previous' or next_page.text.lower() == 'next':
                    continue

                next_page_no = int(next_page.text)
                next_page_songs_list = self.get_songs_list_from_url(next_page_url, artist, False, next_page_no,
                                                                    song_type, image_url)

                for next_page_name in next_page_songs_list:
                    songs_list.append(next_page_name)

        return songs_list

    def mp3_tag_update(self, path: str, song_values: dict):
        song_file = eyed3.load(path)

        cover_art_image_path = get_cover_art_image_path(song_values)
        cover_art_path = os.path.join(os.path.dirname(__file__), cover_art_image_path)

        if cover_art_generation and (os.path.exists(cover_art_path) is False):
            if keep_cover_in_s3_bucket is True:
                get_cover_art_from_s3(cover_art_path, song_values)

                if os.path.exists(cover_art_path) is False:
                    bar = song_values['bar']

                    print("Please enter a url for a '{}' image (Otherwise default image will be used)".format(
                        song_values['artist_name']))
                    song_values['image_url'] = input('>>> ')
                    update_covers_config(song_values)
                    generate_covers(song_values=song_values)
            else:
                update_covers_config(song_values)
                generate_covers(song_values=song_values)

        elif os.path.exists(cover_art_path):
            print("Cover Art already exists")
            song_directory = os.path.join(song_values['directory'], "folder.jpg")
            if not os.path.exists(song_directory) or force_downloadable:
                shutil.copy(cover_art_path, song_directory)

        if song_file is not None:
            if song_file.tag is None:
                song_file.initTag()

            song_file.tag.title = song_values['song_name']
            song_file.tag.album = song_values['artist_name']
            song_file.tag.album_artist = 'Various Artists' if str(song_values['type']).lower() == 'month' else \
                song_values['artist_name']
            song_file.tag.comments.set(song_values['artist_description'])

            song_file.tag.images.remove('CoverArt')
            song_file.tag.images.remove('AlbumArt')

            if cover_art_generation and os.path.exists(cover_art_path):
                song_file.tag.images.set(3, resource_stream(__name__, cover_art_image_path).read(), 'image/jpeg',
                                         'CoverArt')
            else:
                print("Custom cover art does not exists. Using the default cover art")
                song_file.tag.images.set(3, resource_stream(__name__, 'resources/artwork.jpg').read(), 'image/jpeg',
                                         'CoverArt')

            song_file.tag.save()

            if cover_art_delete_after_attached and os.path.exists(cover_art_path) and (cover_art_only_album is False):
                os.remove(cover_art_path)
