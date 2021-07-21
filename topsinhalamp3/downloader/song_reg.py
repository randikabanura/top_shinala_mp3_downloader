import mysql.connector


class SongREG:

    def __init__(self, host, user, passwd, db):
        self.conn = mysql.connector.connect(host=host, user=user, passwd=passwd, database=db)

    def store(self, arr):
        c = self.conn.cursor()
        c.execute(f'SELECT * FROM song WHERE source_id = {arr["source_id"]}')
        rst = c.fetchall()
        row_count = c.rowcount

        if row_count == 0:
            c.execute(
                f'INSERT INTO song(source_id, name, path, song_desc, status, genre_idgenre) VALUES({arr["source_id"]}, "{arr["song_name"]}", "{arr["path"]}", "{arr["song_desc"]}", 0, 1)')
            self.conn.commit()
            c.execute('SELECT idsong FROM song ORDER BY idsong DESC LIMIT 1')
            rst = c.fetchone()
            latest_song_id = rst[0]

            c.execute(f'SELECT idartist FROM artist WHERE url = "{arr["artist_url"]}"')
            rst = c.fetchall()
            row_count = c.rowcount

            if row_count == 0:
                c.execute(f'INSERT INTO artist(idartist, url) VALUES(idartist, "{arr["artist_url"]}")')
                self.conn.commit()
                c.execute('SELECT idartist FROM artist ORDER BY idartist DESC LIMIT 1')
                rst = c.fetchone()
                latest_artist_id = rst[0]
                c.execute(
                    f'INSERT INTO artist_name(name, artist_idartist) VALUES("{arr["artist_name"]}", {latest_artist_id})')
                self.conn.commit()
                c.execute(
                    f'INSERT INTO song_has_artist(song_idsong, artist_idartist) VALUES({latest_song_id}, {latest_artist_id})')
                self.conn.commit()

                return True

            elif row_count > 0:
                artist_id = rst[0][0]
                c.execute(f'SELECT * FROM artist_name WHERE artist_idartist = "{artist_id}"')
                rst = c.fetchall()
                for row in rst:
                    if arr["artist_name"] != row[1]:
                        c.execute(
                            f'INSERT INTO artist_name(name, artist_idartist) VALUES("{arr["artist_name"]}", {artist_id})')
                        self.conn.commit()

                c.execute(
                    f'INSERT INTO song_has_artist(song_idsong, artist_idartist) VALUES({latest_song_id}, {artist_id})')
                self.conn.commit()

                return True
        else:
            song_id = rst[0][0]
            c.execute(f'SELECT * FROM song_has_artist WHERE song_idsong = {song_id}')
            rst = c.fetchall()
            row_count = c.rowcount

            if row_count == 1:
                artist_id = rst[0][1]
                c.execute(f'SELECT * FROM artist WHERE idartist = {artist_id} AND url = "{arr["artist_url"]}"')
                c.fetchall()
                row_count = c.rowcount

                if row_count != 0:
                    c.execute(
                        f'INSERT INTO artist_name(name, artist_idartist) VALUES("{arr["artist_name"]}", {artist_id})')
                    self.conn.commit()
                else:
                    c.execute(f'SELECT * FROM artist WHERE url = "{arr["artist_url"]}"')
                    rst = c.fetchall()
                    row_count = c.rowcount

                    if row_count == 0:
                        c.execute(f'INSERT INTO artist(url) VALUES("{arr["artist_url"]}")')
                        self.conn.commit()
                        c.execute('SELECT * FROM artist ORDER BY idartist DESC LIMIT 1')
                        rst = c.fetchone()
                        artist_id = rst[0]

                        c.execute(
                            f'INSERT INTO artist_name(name, artist_idartist) VALUES("{arr["artist_name"]}", {artist_id})')
                        self.conn.commit()
                        c.execute(
                            f'INSERT INTO song_has_artist(song_idsong, artist_idartist) VALUES({song_id}, {artist_id})')
                        self.conn.commit()

                        return False
                    else:
                        artist_id = rst[0][0]
                        c.execute(
                            f'SELECT * FROM artist_name WHERE artist_idartist = {artist_id} AND name = "{arr["artist_name"]}"')
                        c.fetchall()
                        row_count = c.rowcount

                        if row_count == 0:
                            c.execute(
                                f'INSERT INTO artist_name(name, artist_idartist) VALUES("{arr["artist_name"]}", {artist_id})')
                            self.conn.commit()
                            c.execute(
                                f'INSERT INTO song_has_artist(song_idsong, artist_idartist) VALUES({song_id}, {artist_id})')
                            self.conn.commit()

                            return False
                        else:
                            c.execute(
                                f'INSERT INTO song_has_artist(song_idsong, artist_idartist) VALUES({song_id}, {artist_id})')
                            self.conn.commit()

                            return False
            else:
                is_new = True
                for row in rst:
                    artist_id = row[1]
                    c.execute(f'SELECT * FROM artist WHERE idartist = {artist_id}')
                    rst = c.fetchone()

                    if arr["artist_url"] == rst[1]:
                        is_new = False

                if is_new:
                    c.execute(f'SELECT * FROM artist WHERE url = "{arr["artist_url"]}"')
                    rst = c.fetchone()
                    row_count = c.rowcount

                    if row_count == 0:
                        c.execute(f'INSERT INTO artist(url) VALUES("{arr["artist_url"]}")')
                        self.conn.commit()
                        c.execute('SELECT * FROM artist ORDER BY idartist DESC LIMIT 1')
                        rst = c.fetchone()

                        latest_artist_id = rst[0]
                        c.execute(
                            f'INSERT INTO artist_name(name, artist_idartist) VALUES("{arr["artist_name"]}", {latest_artist_id})')
                        self.conn.commit()
                        c.execute(
                            f'INSERT INTO song_has_artist(song_idsong, artist_idartist) VALUES({song_id}, {latest_artist_id})')
                        self.conn.commit()

                        return False
                    else:
                        artist_id = rst[0]
                        c.execute(
                            f'INSERT INTO artist_name(name, artist_idartist) VALUES("{arr["artist_name"]}", {artist_id})')
                        self.conn.commit()
                        c.execute(
                            f'INSERT INTO song_has_artist(song_idsong, artist_idartist) VALUES({song_id}, {artist_id})')
                        self.conn.commit()

                        return False
                else:
                    for row in rst:
                        artist_id = row[1]
                        c.execute(f'SELECT * FROM artist WHERE idartist = "{artist_id}"')
                        rst = c.fetchone()

                        if arr["artist_url"] == rst[1]:
                            c.execute(f'SELECT * FROM artist_name WHERE name = "{arr["artist_name"]}"')
                            c.fetchone()
                            row_count = c.rowcount

                            if row_count == 0:
                                c.execute(
                                    f'INSERT INTO artist_name(name, artist_idartist) VALUES("{arr["artist_name"]}", {artist_id})')
                                self.conn.commit()

                                return False


instance = SongREG("localhost", "root", "", "mp3_scraping")

# instance.store({"source_id":1, "song_name":"song1", "artist_name":"artist1", "path":"path1", "artist_url":"https://site.com/artists/artist1-song-mp3", "song_desc":"song1_desc"})

# instance.store({"source_id":2, "song_name":"song2", "artist_name":"artist2", "path":"path2", "artist_url":"https://site.com/artists/artist2-song-mp3", "song_desc":"song2_desc"})

# instance.store({"source_id":3, "song_name":"song3", "artist_name":"artist2", "path":"path3", "artist_url":"https://site.com/artists/artist2-song-mp3", "song_desc":"song3_desc"})

# instance.store({"source_id":4, "song_name":"song4", "artist_name":"artist2 v2", "path":"path4", "artist_url":"https://site.com/artists/artist2-song-mp3", "song_desc":"song4_desc"})

# instance.store({"source_id":5, "song_name":"song5", "artist_name":"artist3", "path":"path5", "artist_url":"https://site.com/artists/artist3-song-mp3", "song_desc":"song5_desc"})

# instance.store({"source_id":5, "song_name":"song5", "artist_name":"artist4", "path":"path5", "artist_url":"https://site.com/artists/artist4-song-mp3", "song_desc":"song5_desc"})

# instance.store({"source_id":6, "song_name":"song6", "artist_name":"artist5", "path":"path6", "artist_url":"https://site.com/artists/artist5-song-mp3", "song_desc":"song6_desc"})

# instance.store({"source_id":6, "song_name":"song6", "artist_name":"artist1", "path":"path6", "artist_url":"https://site.com/artists/artist1-song-mp3", "song_desc":"song6_desc"})

# instance.store({"source_id":6, "song_name":"song6", "artist_name":"artist3 v2", "path":"path6", "artist_url":"https://site.com/artists/artist3-song-mp3", "song_desc":"song6_desc"})

# instance.store({"source_id":7, "song_name":"song7", "artist_name":"artist6", "path":"path7", "artist_url":"https://site.com/artists/artist6-song-mp3", "song_desc":"song7_desc"})

# instance.store({"source_id":7, "song_name":"song7", "artist_name":"artist7", "path":"path7", "artist_url":"https://site.com/artists/artist7-song-mp3", "song_desc":"song7_desc"})
