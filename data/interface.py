from .states import *
from .consts import *
from .data_loader import DataLoader

import re


class Interface(object):

    def __init__(self):
        self.__data_loader = DataLoader('./downloads')
        self.__state = NO_STATE
        self.__cmds = []
        self.__page_id = 1
        self.__artist_name_letter = None

    def __print_initial_msg(self, cmd='none'):
        print("Welcome to Top Sinhala MP3 Downloader..\nEnter your commands below...\n")
        print("Anytime, if you want to go back enter 99 and if you want to start from the beginning enter 999..")
        print("Also you can exit the software by typing quit...")
        print("Do you need to search by:\n\t1) Artist Letter \n\t2) Artist Name \n\t3) All Artists")
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
            print('Invalid character (%s). Please try again' % cmd)

    def __search(self, cmd: str):
        if cmd in '1)':
            print("Enter the first letter of the Artists")
            self.__state = ARTIST_LETTER
        elif cmd in '2)':
            print("Enter the first letter of the Artists")
            self.__state = ARTIST_NAME_ENTERED
        elif cmd in '3)':
            print("Enter the first letter of the name of the artist")
            self.__state = ALL_DOWNLOAD
        else:
            self.__handle_back(cmd, self.__print_initial_msg)

    def __show_results_name(self, cmd):
        item_list = self.__data_loader.get_name_list_from(cmd, self.__page_id)
        if item_list is None:
            if self.__page_id == 1:
                print("There is no song starts with the given character %s", cmd)
                self.__handle_back('99', self.__search, True)
                return
            print('The given id is not valid. Starting from the beginning')
            self.__page_id = 1
            name_list, page_info = self.__data_loader.get_name_list_from(cmd, self.__page_id)
        name_list, page_info = item_list
        print(
            '\n'.join(['%d) %s [downloads: %d]' % (item['index'], item['name'], item['count']) for item in name_list]))
        print(page_info)
        print('\nEnter nn to goto next page. pp to previous page. id<num> to goto page given by <num>.')
        print('To select a song type sel<num> to download the song given by <num> in the list')

    def __name_c_entered(self, cmd: str):
        if cmd in first_chrs:
            self.__page_id = 1
            self.__state = NAME_CHR_ENTERED
            self.__show_results_name(cmd)
        else:
            self.__handle_back(cmd, self.__search)

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
            print("{}) {}".format(artist['index'], artist['name']))

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

        songs_list = []
        for artist in artist_list:
            if artist['url'] is not None and artist['name'] is not None:
                print('Getting Songs from Artist: ', artist['name'], 'URL: ', artist['url'])
                songs_name_list = self.__data_loader.get_songs_list_from_url(artist['url'], artist['name'])

                for song_name in songs_name_list:
                    songs_list.append(song_name)

        self.__download_songs(songs_list)

    def __artist_all_download(self, cmd: str):
        print("All Artist download")

        args = cmd.split()
        url = full_letter_url
        args = args[1:]
        count_lim = 0
        for arg in args:
            if arg.startswith('d'):
                try:
                    count_lim = int(arg[1:])
                except:
                    print('error number format. Try again as d<num>')
                    return
        if count_lim == 0:
            print("Downloading all songs..")
            print("Under Letter:")

        artist_list = self.__get_artists(url)
        if artist_list is None:
            return

        songs_list = []
        for artist in artist_list:
            if artist['url'] is not None and artist['name'] is not None:
                print('Getting Songs from Artist: ', artist['name'], 'URL: ', artist['url'])
                songs_name_list = self.__data_loader.get_songs_list_from_url(artist['url'], artist['name'])

                for song_name in songs_name_list:
                    songs_list.append(song_name)

        self.__download_songs(songs_list)

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

        songs_list = []
        for artist in artist_list:
            if artist['url'] is not None and artist['name'] is not None and artist['index'] == artist_index:
                print('Getting Songs from Artist: ', artist['name'], 'URL: ', artist['url'])
                songs_name_list = self.__data_loader.get_songs_list_from_url(artist['url'], artist['name'])

                for song_name in songs_name_list:
                    songs_list.append(song_name)

        self.__download_songs(songs_list)

        self.__artist_name_letter = None

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

    def __download_songs(self, song_list: list = []):
        for song in song_list:
            song_artist = song['artist']
            song_url = song['url']
            song_name = song['song']

            print("Song download: Artist:", song_artist, "Song:", song_name)
            if song_url is not None:
                self.__data_loader.download_file_from_url(song_url, song_name)

    def __redirect_to_function(self, cmd: str):
        cmd = cmd.strip()
        if cmd is None or cmd == '':
            return
        if self.__state == NO_STATE:
            self.__print_initial_msg()
        elif self.__state == INITIAL_STATE:
            self.__search(cmd)
        elif self.__state == SEARCH_SONG_BY_NAME:
            self.__name_c_entered(cmd)
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

    def begin(self):
        cmd = 'initial'
        while cmd not in ['exit', 'quit', 'close']:
            self.__redirect_to_function(cmd)
            cmd = input('> ').lower()
            self.__cmds.append(cmd)
