import urllib.request as urllib2
import urllib.parse as urlparse
from bs4 import BeautifulSoup
from .consts import *
import shutil
from urllib.error import URLError
import os
import eyed3
from pkg_resources import resource_stream

from .database.song_reg import SongREG


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
        if database_enabled:
            print("Database is enabled")
            song_database = SongREG(database_host, database_username, database_password, database_name)
            downloadable = song_database.store(values)
            print("Song downloadable:", downloadable)
        else:
            print("Database is not enabled")
            downloadable = True

        if not downloadable or os.path.isfile(name):
            print("File already there.. Going to next :)")
            return
        else:
            if not os.path.exists(directory):
                os.makedirs(directory)

        try:
            print("Request URL: ", url)
            response = urllib2.urlopen(url)
            with open(name, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

            print("Successfully download Song: ", name)

            if update_mp3_tag:
                self.mp3_tag_update(name, values)
                print("Successfully MP3 tags updated")
        except URLError as e:
            if hasattr(e, 'reason'):
                print('We failed to reach a server.')
                print('Reason: ', e.reason)
            elif hasattr(e, 'code'):
                print('The server couldn\'t fulfill the request.')
                print('Error code: ', e.code)
        except Exception as e:
            print("Error Occurred. Reason:\n", e)

    def download_file_from_url(self, url: str, name: str, artist: str, artist_url: str):
        self.set_soup(url)
        source = self.__soup.find('div', id='tsmp3-player').find(class_='player-source')

        if source is None or source.get('data-src') is None or source.get('data-src') == '#':
            print('Source URL: ', source, 'does not have a valid  url')
            return

        source_link = source.get('data-src')
        directory = "{}/{}".format(self.__download_dir, artist)
        file_name = "{}/{}{}".format(directory, name, '.mp3')

        try:
            source_id = urlparse.parse_qs(urlparse.urlparse(source_link).query)['id'][0]
            song_artist_details = self.__soup.find('ul', class_='song_details').select('li')[1].find(text=True,
                                                                                                     recursive=False).strip()
        except:
            print("Error occurred when downloading Song:", name)
            return

        song_values = {
            'source_id': source_id,
            'artist_description': song_artist_details,
            'artist_name': artist,
            'artist_url': artist_url,
            'song_name': name,
            'song_url': source_link,
            'song_description': '',
            'path': file_name
        }

        self.__download_file(source_link, directory, file_name, song_values)

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

    def get_songs_list_from_url(self, url: str, artist: str, get_next_page: bool = True, page: int = 1):
        self.set_soup(url)
        songs_name_list = self.__soup.find('ol', class_='list_of_songs').find_all('a', attrs={'class': None})
        songs_list = []
        for i, song in enumerate(songs_name_list):
            print('Song Name: ', song.text)
            values = {
                'page': int(page),
                'index': (songs_per_page * int(page - 1)) + int(i + 1),
                'artist': artist,
                'artist_url': url,
                'song': song.text,
                'url': base_url + song.get('href').split('/', 1)[-1]
            }
            songs_list.append(values)

        if get_next_page:
            next_pages = self.__soup.find(class_='bottom_navigation_bar').find_all(class_='bnav_button')

            for next_page in next_pages:
                next_page_url = base_artist_url + next_page.get('href')

                if next_page.text.lower() == 'previous' or next_page.text.lower() == 'next':
                    continue

                next_page_no = int(next_page.text)
                next_page_songs_list = self.get_songs_list_from_url(next_page_url, artist, False, next_page_no)

                for next_page_name in next_page_songs_list:
                    songs_list.append(next_page_name)

        return songs_list

    def mp3_tag_update(self, path: str, song_values: dict):
        song_file = eyed3.load(path)

        if song_file is not None:
            if song_file.tag is None:
                song_file.initTag()

            song_file.tag.title = song_values['song_name']
            song_file.tag.album = song_values['artist_description']
            song_file.tag.comments.set(song_values['artist_description'])

            song_file.tag.images.remove('AlbumArt')
            song_file.tag.images.set(3, resource_stream(__name__, 'resources/artwork.jpg').read(), 'image/jpeg',
                                     'AlbumArt')

            song_file.tag.save()
