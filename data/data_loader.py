import urllib.request as urllib2
from bs4 import BeautifulSoup
from .consts import *
import shutil
from urllib.error import URLError
import os


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

    def __download_file(self, url: str, file_name: str):
        file_name = '%s/%s' % (self.__download_dir, file_name)
        if os.path.isfile(file_name):
            print("File already there.. Going to next :)")
            return
        try:
            with urllib2.urlopen(url) as response, open(file_name, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        except URLError as e:
            if hasattr(e, 'reason'):
                print('We failed to reach a server.')
                print('Reason: ', e.reason)
            elif hasattr(e, 'code'):
                print('The server couldn\'t fulfill the request.')
                print('Error code: ', e.code)
        except IOError as e:
            print("Error while accessing file\nReason:", e.strerror)

    def download_file_from_id(self, id: str, file_name: str):
        self.__download_file(download_url % id, file_name)

    def get_name_list_from(self, c: str, pid: int=1):
        url = song_by_name % (c, pid)
        return self.get_name_list_from_url(url, False)
    
    def get_name_list_from_all(self, pid: int):
        url = all_song_url % pid
        return self.get_name_list_from_url(url)

    def get_artist_letters_from_url(self, url: str, letter: str=None, any: bool=True):
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

    def get_name_list_from_url(self, url: str, any: bool=True, next: bool=True, page: int=1):
        self.set_soup(url)
        artist_name_list = self.__soup.find('ol', class_='list_of_songs').find_all('a', attrs={'class': None})
        artist_list = []
        for i, artist in enumerate(artist_name_list):
            print('Artist Name: ', artist.text)
            values = {
                'page': int(page),
                'index': int(i + 1),
                'name': artist.text,
                'url': base_url + artist.get('href').split('/', 1)[-1]
            }
            artist_list.append(values)

        if next:
            next_pages = self.__soup.find(class_ = 'bottom_navigation_bar').find_all(class_ = 'bnav_button')

            for next_page in next_pages:
                next_page_url = base_letter_url + next_page.get('href')

                if next_page.text.lower() == 'previous' or next_page.text.lower() == 'next':
                    continue

                next_page_no = int(next_page.text)
                next_page_artist_list = self.get_name_list_from_url(next_page_url, True, False, next_page_no)

                for next_page_name in next_page_artist_list:
                    artist_list.append(next_page_name)


        return artist_list

    def get_songs_list_from_url(self, url: str, artist: str, any: bool=True, next: bool=True, page: int=1):
            self.set_soup(url)
            songs_name_list = self.__soup.find('ol', class_='list_of_songs').find_all('a', attrs={'class': None})
            songs_list = []
            for i, song in enumerate(songs_name_list):
                print('Song Name: ', song.text)
                values = {
                    'page': int(page),
                    'index': int(i + 1),
                    'artist': artist,
                    'song': song.text,
                    'url': base_url + song.get('href').split('/', 1)[-1]
                }
                songs_list.append(values)

            if next:
                next_pages = self.__soup.find(class_ = 'bottom_navigation_bar').find_all(class_ = 'bnav_button')

                for next_page in next_pages:
                    next_page_url = base_artist_url + next_page.get('href')

                    if next_page.text.lower() == 'previous' or next_page.text.lower() == 'next':
                        continue

                    next_page_no = int(next_page.text)
                    next_page_songs_list = self.get_songs_list_from_url(next_page_url, artist, True, False, next_page_no)

                    for next_page_name in next_page_songs_list:
                        songs_list.append(next_page_name)


            return songs_list

