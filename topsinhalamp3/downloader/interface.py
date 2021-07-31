from .states import *
from .consts import *
from .data_loader import DataLoader
from tqdm import tqdm

import re


class Interface(object):

    def __init__(self):
        self.__data_loader = DataLoader(file_download_path)
        self.__state = NO_STATE
        self.__cmds = []
        self.__page_id = 1
        self.__artist_name_letter = None

    def __print_initial_msg(self, cmd='none'):
        print("")
        print("===================================================================")
        print("Welcome to Top Sinhala MP3 Downloader..\nEnter your commands below...\n")
        print("Anytime, if you want to go back enter 99 and if you want to start from the beginning enter 999..")
        print("Also you can exit the software by typing quit...")
        print(
            "Do you need to search by:\n\t1) Artist Letter \n\t2) Artist Name \n\t3) All Artists \n\t4) Top 25 by "
            "Month \n\t5) All Top 25 by Month \n\t6) New by Month \n\t7) All New by Month")
        print("Please enter a number below")
        self.__state = INITIAL_STATE

    def __handle_back(self, cmd, func, hard_back=False):
        if (not hard_back) and self.__state != INITIAL_STATE:
            self.__cmds.pop()
        if cmd == '999':
            self.__cmds = []
            self.__print_initial_msg()
        elif cmd == '99':
            func(self.__cmds.pop())
        else:
            print("State: ", self.__state)
            print('Invalid character (%s). Please try again' % cmd)

    def __search(self, cmd: str):
        if cmd in '1)':
            print("Enter the first letter of the Artists")
            self.__state = ARTIST_LETTER
        elif cmd in '2)':
            print("Enter the first letter of the Artists")
            self.__state = ARTIST_NAME_ENTERED
        elif cmd in '3)':
            self.__state = ALL_DOWNLOAD
            self.__artist_all_download('')
        elif cmd in '4)':
            print("Enter the first letter of the Month")
            self.__state = TOP_25_BY_MONTH_ENTERED
            self.__top_25_month_results('')
        elif cmd in '5)':
            self.__state = ALL_TOP_25_BY_MONTH
            self.__top_25_all_download('')
        elif cmd in '6)':
            print("Enter the first letter of the Month")
            self.__state = NEW_BY_MONTH_ENTERED
            self.__new_month_results('')
        elif cmd in '7)':
            self.__state = ALL_NEW_BY_MONTH
            self.__new_all_download('')
        else:
            self.__handle_back(cmd, self.__print_initial_msg)

    def __custom_search(self, cmd: str):
        if cmd is not None and cmd != '':
            self.__state = ARTIST_LETTER
        else:
            self.__handle_back(cmd, self.__search)

    def __artist_name_results(self, cmd: str):
        print("Artist Name based show results")
        args = cmd.split()
        url = full_letter_url
        args = args[0:]
        letter = None
        for arg in args:
            matches = re.match(artist_letter_based_regex, arg, re.MULTILINE)
            if matches:
                letter = arg.lower()

        if letter is not None:
            print("Letter based: ", letter.upper())
        else:
            print("Input is not correct. Letter:", letter)
            return

        self.__artist_name_letter = letter

        artist_list = self.__get_artists(url, letter)
        if artist_list is None:
            return

        print("Select a number for the Artist")
        for artist in artist_list:
            print("{}) {} {}".format(artist['index'], artist['name'], artist['no_of_songs']))

        self.__state = ARTIST_NAME

    def __artist_letter_based(self, cmd: str):
        print("Artist Letter based download")

        args = cmd.split()
        url = full_letter_url
        args = args[0:]
        count_lim = 0
        letter = None
        for arg in args:
            if arg.startswith('d'):
                try:
                    count_lim = int(arg[1:])
                except:
                    print('error number format. Try again as d<num>')
                    return

            matches = re.match(artist_letter_based_regex, arg, re.MULTILINE)
            if matches:
                letter = arg.lower()

        if letter is not None:
            print("Letter based: ", letter.upper())
        else:
            print("Input is not correct. Letter:", letter)
            return

        if count_lim == 0:
            print("Downloading all songs..")

        artist_list = self.__get_artists(url, letter)
        if artist_list is None:
            return

        songs_list = self.__get_songs(artist_list)

        self.__download_songs(songs_list)
        self.__handle_back('999', self.__print_initial_msg)

    def __artist_all_download(self, cmd: str):
        print("All Artist download")

        url = full_letter_url
        print("Downloading all songs..")

        artist_list = self.__get_artists(url)
        if artist_list is None:
            return

        songs_list = self.__get_songs(artist_list)

        self.__download_songs(songs_list)
        self.__handle_back('999', self.__print_initial_msg)

    def __artist_name_based(self, cmd: str):
        print("Artist Name based download")

        letter = self.__artist_name_letter
        args = cmd.split()
        url = full_letter_url
        args = args[0:]
        count_lim = 0
        artist_index = args[0]

        for arg in args:
            if arg.startswith('d'):
                try:
                    count_lim = int(arg[1:])
                except:
                    print('error number format. Try again as d<num>')
                    return

        if artist_index is None:
            print("Input is not correct. Number:", artist_index)
            self.__artist_name_letter = None
            return
        else:
            artist_index = int(artist_index)

        if letter is not None:
            matches = re.match(artist_letter_based_regex, letter, re.MULTILINE)
            if matches:
                letter = letter
            else:
                print("Input is not correct. Letter:", letter)
                self.__artist_name_letter = None
                return

            print("Letter based: ", letter.upper())
        else:
            print("Input is not correct. Letter:", letter)
            self.__artist_name_letter = None
            return

        artist_list = self.__get_artists(url, letter)
        if artist_list is None:
            return

        songs_list = self.__get_songs(artist_list, True, artist_index)

        self.__download_songs(songs_list)

        self.__artist_name_letter = None
        self.__handle_back('999', self.__print_initial_msg)

    def __top_25_month_results(self, cmd):
        print("Month based show results")
        url = top_25_month_url

        months_list = self.__get_months(url)
        if months_list is None:
            return

        print("Select a number for the Month")
        for month in months_list:
            print("{}) {}".format(month['index'], month['name']))

        self.__state = TOP_25_BY_MONTH

    def __top_25_month_based(self, cmd):
        print("Month based download")

        args = cmd.split()
        url = top_25_month_url
        args = args[0:]
        month_index = args[0]

        if month_index is None:
            print("Input is not correct. Number:", month_index)
            return
        else:
            month_index = int(month_index)

        months_list = self.__get_months(url)

        if months_list is None:
            return

        songs_list = self.__get_songs(months_list, True, month_index, song_type='Month')
        self.__download_songs(songs_list, song_type='Month', folder_prefix='Top 25 Sinhala')

        self.__handle_back('999', self.__print_initial_msg)

    def __top_25_all_download(self, cmd):
        print("All Months download")

        url = top_25_month_url
        months_list = self.__get_months(url)

        if months_list is None:
            return

        songs_list = self.__get_songs(months_list, song_type='Month')
        self.__download_songs(songs_list, song_type='Month', folder_prefix='Top 25 Sinhala')

        self.__handle_back('999', self.__print_initial_msg)

    def __new_month_results(self, cmd):
        print("Month based show results")
        url = new_sinhala_month_url

        months_list = self.__get_months(url)
        if months_list is None:
            return

        print("Select a number for the Month")
        for month in months_list:
            print("{}) {}".format(month['index'], month['name']))

        self.__state = NEW_BY_MONTH

    def __new_month_based(self, cmd):
        print("Month based download")

        args = cmd.split()
        url = new_sinhala_month_url
        args = args[0:]
        month_index = args[0]

        if month_index is None:
            print("Input is not correct. Number:", month_index)
            return
        else:
            month_index = int(month_index)

        months_list = self.__get_months(url)

        if months_list is None:
            return

        songs_list = self.__get_songs(months_list, True, month_index, song_type='Month')
        self.__download_songs(songs_list, song_type='Month', folder_prefix='New Sinhala')

        self.__handle_back('999', self.__print_initial_msg)

    def __new_all_download(self, cmd):
        print("All Months download")

        url = new_sinhala_month_url
        months_list = self.__get_months(url)

        if months_list is None:
            return

        songs_list = self.__get_songs(months_list, song_type='Month')
        self.__download_songs(songs_list, song_type='Month', folder_prefix='New Sinhala')

        self.__handle_back('999', self.__print_initial_msg)

    def __get_months(self, url: str):
        months_list = self.__data_loader.get_months_list_from_url(url)

        return months_list

    def __get_artists(self, url: str, letter: str = None):
        letter_list = self.__data_loader.get_artist_letters_from_url(url, letter)

        if letter_list is None:
            print('Some Letter List Error')
            return

        artist_list = []
        for letter in letter_list:
            if letter['url'] is not None and letter['url'].split('#')[0] not in full_letter_url:
                print('Getting Artists from Letter: ', letter['name'], 'URL: ', letter['url'])
                artist_name_list = self.__data_loader.get_name_list_from_url(letter['url'])

                for artist_name in artist_name_list:
                    artist_list.append(artist_name)

        return artist_list

    def __get_songs(self, url_list: list = [], one_url: bool = False, index_number: int = None,
                    song_type: str = 'Artist'):
        songs_list = []
        for item in url_list:

            if item['url'] is not None and item['name'] is not None and (
                    not one_url or item['index'] == index_number):
                print('Getting Songs from Item: ', item['name'], 'URL: ', item['url'])
                songs_name_list = self.__data_loader.get_songs_list_from_url(item['url'], item['name'],
                                                                             song_type=song_type)

                if songs_name_list is None:
                    return songs_list

                for song_name in songs_name_list:
                    songs_list.append(song_name)

        return songs_list

    def __download_songs(self, song_list: list = [], song_type: str = 'Artist', folder_prefix: str = ''):
        for song in tqdm(song_list):
            song_item = "{} {}".format(folder_prefix, song['item']).strip()
            song_url = song['url']
            song_name = song['song']
            song_item_url = song['item_url']

            print("Song download: Item:", song_item, "Song:", song_name)
            if song_url is not None:
                self.__data_loader.download_file_from_url(song_url, song_name, song_item, song_item_url, song_type)

    def __redirect_to_function(self, cmd: str):
        cmd = cmd.strip()
        if cmd is None or cmd == '':
            return
        if self.__state == NO_STATE:
            self.__print_initial_msg()
        elif self.__state == INITIAL_STATE:
            self.__search(cmd)
        elif self.__state == ARTIST_NAME_ENTERED:
            self.__artist_name_results(cmd)
        elif self.__state == SEARCH_CUSTOM:
            self.__custom_search(cmd)
        elif self.__state == ARTIST_LETTER:
            self.__artist_letter_based(cmd)
        elif self.__state == ARTIST_NAME:
            self.__artist_name_based(cmd)
        elif self.__state == ALL_DOWNLOAD:
            self.__artist_all_download(cmd)
        elif self.__state == TOP_25_BY_MONTH_ENTERED:
            self.__top_25_month_results(cmd)
        elif self.__state == TOP_25_BY_MONTH:
            self.__top_25_month_based(cmd)
        elif self.__state == ALL_TOP_25_BY_MONTH:
            self.__top_25_all_download(cmd)
        elif self.__state == NEW_BY_MONTH_ENTERED:
            self.__new_month_results(cmd)
        elif self.__state == NEW_BY_MONTH:
            self.__new_month_based(cmd)
        elif self.__state == ALL_NEW_BY_MONTH:
            self.__new_all_download(cmd)

    def begin(self):
        cmd = 'initial'
        while cmd not in ['exit', 'quit', 'close', 'exit()', 'quit()', 'close()']:
            self.__redirect_to_function(cmd)
            cmd = input('>>> ').lower()
            self.__cmds.append(cmd)
