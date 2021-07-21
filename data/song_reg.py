import mysql.connector

class SongREG:

    def __init__(self, host, user, passwd, db):
        self.conn = mysql.connector.connect(host=host, user=user, passwd=passwd, database = db)

    def store(self, arr):
        c = self.conn.cursor()
        c.execute(f'SELECT * FROM song WHERE source_id = {arr["source_id"]}')
        rst = c.fetchall()
        row_count = c.rowcount
        
        if row_count == 0:
            c.execute(f'INSERT INTO song(source_id, name, path, status, genre_idgenre) VALUES({arr["source_id"]}, "{arr["song_name"]}", "{arr["path"]}", 0, 1)')
            self.conn.commit()
            c.execute('SELECT idsong FROM song ORDER BY idsong DESC LIMIT 1')
            rst = c.fetchone()
            latest_song_id = rst[0]
            
            c.execute(f'SELECT artist_idartist FROM artist_name WHERE name = "{arr["artist_name"]}"')
            rst = c.fetchall()
            row_count = c.rowcount
            
            if row_count == 0:
                c.execute('INSERT INTO artist(idartist) VALUES(idartist)')
                self.conn.commit()
                c.execute('SELECT idartist FROM artist ORDER BY idartist DESC LIMIT 1')
                rst = c.fetchone()
                latest_artist_id = rst[0]
                c.execute(f'INSERT INTO artist_name(name, artist_idartist) VALUES("{arr["artist_name"]}", {latest_artist_id})')
                self.conn.commit()
                c.execute(f'INSERT INTO song_has_artist(song_idsong, artist_idartist) VALUES({latest_song_id}, {latest_artist_id})')
                self.conn.commit()
            elif row_count > 0:
                artist_id = rst[0][0]
                c.execute(f'INSERT INTO song_has_artist(song_idsong, artist_idartist) VALUES({latest_song_id}, {artist_id})')
                self.conn.commit()
        else:
            song_id = rst[0][0]
            c.execute(f'SELECT * FROM song_has_artist WHERE song_idsong = {song_id}')
            rst = c.fetchall()
            row_count = c.rowcount
            
            if row_count == 1:
                artist_id = rst[0][1]
                c.execute(f'SELECT * FROM artist_name WHERE artist_idartist = {artist_id} AND name = "{arr["artist_name"]}"')
                c.fetchall()
                row_count = c.rowcount
                
                if row_count == 0:
                    c.execute(f'INSERT INTO artist_name(name, artist_idartist) VALUES("{arr["artist_name"]}", {artist_id})')
                    self.conn.commit()
                else:
                    print('issue: multiple artist 01')
            else:
                print('issue: multiple artist 02')
                # for row in rst:
                #     artist_id = row.artist_idartist
                #     c.execute(f'SELECT * FROM artist_name WHERE artist_idartist = {artist_id} AND name = "{arr["artist_name"]}"')
                #     c.fetchall()
                #     row_count = c.rowcount

                #     if row_count == 0:
                #         c.execute(f'INSERT INTO artist_name(name, artist_artist_id) VALUES("{arr["artist_name"]}", {artist_id})')
                #     else:
                #         return 2
            


instance = SongREG("localhost", "root", "", "mp3_scraping")

# new song new artist
instance.store({"source_id":1, "song_name":"song1", "artist_name":"artist1", "path":"path1"})
# new song existing artist
instance.store({"source_id":2, "song_name":"song2", "artist_name":"artist2", "path":"path2"})
# new song new artist
instance.store({"source_id":3, "song_name":"song3", "artist_name":"artist2", "path":"path3"})
# existing song different name for artist
instance.store({"source_id":3, "song_name":"song3", "artist_name":"artist2 sec name", "path":"path3"})
# new song new artist
instance.store({"source_id":4, "song_name":"song4", "artist_name":"artist3", "path":"path4"})