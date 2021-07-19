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

    def __print_initial_msg(self, cmd='none'):
        print("Welcome to Top Sinhala MP3 Downloader..\nEnter your commands below...\n")
        print("Anytime, if you want to go back enter 99 and if you want to start from the beginning enter 999..")
        print("Also you can exit the software by typing quit...")
        print("Do you need to search by:\n\t1) Artist Letter \n\t2) All Artists")
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

    def __name_results(self, cmd: str):
        show_result = True
        if cmd == 'nn':
            self.__cmds.pop()
            cmd = self.__cmds[-1]
            self.__page_id += 1
        elif cmd == 'pp':
            self.__cmds.pop()
            cmd = self.__cmds[-1]
            self.__page_id -= 1
            if self.__page_id < 1:
                self.__page_id = 1
        elif cmd.startswith('id'):
            try:
                self.__page_id = int(cmd[2:])
            except:
                print("Cannot identify a ID given. Going back to the beginning..")
                self.__page_id = 1
            self.__cmds.pop()
            cmd = self.__cmds[-1]
        elif cmd.startswith('sel'):
            pass
        else:
            show_result = False
            self.__handle_back(cmd, self.__search)
        if show_result:
            self.__show_results_name(cmd)

    def __custom_search(self, cmd: str):
        if cmd is not None and cmd != '':
            self.__state = ARTIST_LETTER
        else:
            self.__handle_back(cmd, self.__search)

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
            print("Input is not correct")
            return

        if count_lim == 0:
            print("Downloading all songs..")

        letter_list = self.__data_loader.get_artist_letters_from_url(url, letter)

        if letter_list is None:
            print('Some Error')
            return

        artist_list = []
        for letter in letter_list:
            if letter['url'] is not None and letter['url'].split('#')[0] not in full_letter_url:
                print('Getting Artists from Letter: ', letter['name'], 'URL: ', letter['url'])
                artist_name_list = self.__data_loader.get_name_list_from_url(letter['url'])

                for artist_name in artist_name_list:
                    artist_list.append(artist_name)

        songs_list = []
        for artist in artist_list:
            if artist['url'] is not None and artist['name'] is not None:
                print('Getting Songs from Artist: ', artist['name'], 'URL: ', artist['url'])
                songs_name_list = self.__data_loader.get_songs_list_from_url(artist['url'], artist['name'])

                for song_name in songs_name_list:
                    songs_list.append(song_name)

        print(songs_list)

    #             if item['count'] > count_lim:
    #                 print("downloading item: '%s' with %d downloads" % (item['name'], item['count']))
    #                 self.__data_loader.download_file_from_id(item['id'], '%s.mp3' % item['name'])

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

        letter_list = self.__data_loader.get_artist_letters_from_url(url)

        if letter_list is None:
            print('Some Error')
            return

        artist_list = []
        for letter in letter_list:
            if letter['url'] is not None and letter['url'].split('#')[0] not in full_letter_url:
                print('Getting Artists from Letter: ', letter['name'], 'URL: ', letter['url'])
                artist_name_list = self.__data_loader.get_name_list_from_url(letter['url'])

                for artist_name in artist_name_list:
                    artist_list.append(artist_name)

        songs_list = []
        for artist in artist_list:
            if artist['url'] is not None and artist['name'] is not None:
                print('Getting Songs from Artist: ', artist['name'], 'URL: ', artist['url'])
                songs_name_list = self.__data_loader.get_songs_list_from_url(artist['url'], artist['name'])

                for song_name in songs_name_list:
                    songs_list.append(song_name)

        print(songs_list)

    #             if item['count'] > count_lim:
    #                 print("downloading item: '%s' with %d downloads" % (item['name'], item['count']))
    #                 self.__data_loader.download_file_from_id(item['id'], '%s.mp3' % item['name'])

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
        elif self.__state == NAME_CHR_ENTERED:
            self.__name_results(cmd)
        elif self.__state == SEARCH_CUSTOM:
            self.__custom_search(cmd)
        elif self.__state == ARTIST_LETTER:
            self.__artist_letter_based(cmd)
        elif self.__state == ALL_DOWNLOAD:
            self.__artist_all_download(cmd)

    def begin(self):
        cmd = 'initial'
        while cmd not in ['exit', 'quit', 'close']:
            self.__redirect_to_function(cmd)
            cmd = input('> ').lower()
            self.__cmds.append(cmd)
