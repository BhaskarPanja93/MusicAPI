from datetime import datetime
from datetime import timedelta
from threading import Thread, Event
from time import sleep


from customisedLogs import CustomisedLogs
from pooledMySQL import PooledMySQL
from randomisedString import RandomisedString


from Classes.Holders.DBTables import DBTables
from Classes.Holders.UrlTypes import UrlTypes
from Classes.Processors.SongData import SongData
from Classes.Processors.SpotifyAPI import SpotifyAPICollection
from Classes.Processors.URLHandler import URLHandler
from Classes.Processors.YTDLP import YTDLP


class SongCache:
    """
    Processor to collect, renew and handle local and DB caches for all song data
    """
    def __init__(self, SQLConn:PooledMySQL, Logger:CustomisedLogs, URLHandler:URLHandler):
        self.SQLConn = SQLConn
        self.logger = Logger
        self.cache:dict[str, SongData] = {}
        self.YTDLP = YTDLP(self.logger)
        self.SpotifyAPICollection = SpotifyAPICollection(self.SQLConn)
        self.URLHandler = URLHandler


    def __save_to_db(self, song:SongData) -> None:
        """
        Store a new song to DB or mark as repeat
        :param song: SongData object with all values
        :return:
        """
        fetched = self.SQLConn.execute(f"SELECT {DBTables.SONGS.SONG_ID} FROM {DBTables.SONGS.TABLE_NAME} WHERE ({DBTables.SONGS.REAL_NAME}=? AND {'TRUE' if song.song_name else 'FALSE'}) OR ({DBTables.SONGS.YT_ID}=? AND {'TRUE' if song.yt else 'FALSE'}) OR ({DBTables.SONGS.SPOTIFY_ID}=? AND {'TRUE' if song.spotify else 'FALSE'}) LIMIT 1", [song.song_name, song.yt, song.spotify])
        if fetched:
            realID = fetched[0][DBTables.SONGS.SONG_ID].decode()
            if realID not in self.cache: self.__cache_from_db(realID, True)
            realSong = self.cache[realID]
            song.repeat_for = realSong
            self.__renew_expiry(realSong, song.audio_url)
            self.SQLConn.execute(f"INSERT INTO {DBTables.ALIASES.TABLE_NAME} VALUES (?, ?)", [realID, song.search_name])
        else:
            self.SQLConn.execute(f"INSERT INTO {DBTables.SONGS.TABLE_NAME} VALUES (?, ?, ?, ?, ?, ?, ?, NOW())", [song.song_id, song.song_name, song.spotify, song.yt, song.duration, song.thumbnail, song.audio_url])
            if song.search_name != song.song_name:
                self.SQLConn.execute(f"INSERT INTO {DBTables.ALIASES.TABLE_NAME} VALUES (?, ?)", [song.song_id, song.search_name])


    def __fetch_new(self, song:SongData, category:UrlTypes, string:str) -> None:
        """
        Fetch a new song from YTDLP or Spotipy based on category and name/url string implementing Event based waiting to prevent race conditions
        Also keeps track of audio url expiry and calls for refresh when needed
        :param song: the SongData object to fill
        :param category: category of the string
        :param string: name/url string
        :return:
        """
        if song.waiter is None:
            song.waiter = Event()
            song.waiter.clear()

        if category == UrlTypes.YT_URL:
            url = self.URLHandler.merge(category, string)
            r = self.YTDLP.get_downloader(url)
            song.song_name = r.get("title")
            song.yt = string
            song.duration = r.get("duration")
            song.audio_url = r.get("url")
            Thread(target=song.fetch_stream).start()
            song.thumbnail = None if r.get("thumbnails") is None else r.get("thumbnails")[0].get('url')

        elif category == UrlTypes.SPOTIFY_URL:
            details = self.SpotifyAPICollection.fetch_api().API.track(string)
            artists = " ".join([_["name"] for _ in details['artists']])
            song.song_name = details["name"] + " " + artists
            if song.song_name:
                self.__fetch_new(song, UrlTypes.UNKNOWN, song.song_name)

        elif category == UrlTypes.UNKNOWN:
            r = self.YTDLP.get_downloader(string + " lyrics")
            song.yt = r['entries'][0]['id']
            song.song_name = r["entries"][0]["title"]
            song.audio_url = r['entries'][0]['url']
            Thread(target=song.fetch_stream).start()
            song.duration = r['entries'][0]['duration']
            song.thumbnail = r['entries'][0]['thumbnail'] if r['entries'][0]['thumbnail'] else None

        if not song.spotify:
            try:
                items = self.SpotifyAPICollection.fetch_api().API.search(song.song_name.lower(), type="track")['tracks']['items']
                chosen = items[1]
                for item in items:
                    if item["name"].lower() == song.song_name.lower() or item["name"].lower() in song.song_name.lower():
                        chosen = item
                        break
                song.spotify = chosen["id"]
            except:
                song.spotify = ""

        song.expiry = datetime.now() + timedelta(hours=5)
        self.__save_to_db(song)
        if song.waiter is not None:
            song.waiter.set()
            song.waiter = None
        Thread(target=self.__remove_cache, args=(song,)).start()


    def __cache_from_db(self, songID:str, asRepeat) -> SongData | None:
        """
        Fetch a song data from DB
        :param songID: ID of the song
        :param asRepeat: if the song has to be marked as real for some other repeat song, which will define if it needs to be renewed
        :return: SongData object
        """
        fetched = self.SQLConn.execute(f"SELECT * FROM {DBTables.SONGS.TABLE_NAME} WHERE {DBTables.SONGS.SONG_ID}=?", [songID])
        if fetched:
            fetched = fetched[0]
            song = SongData()
            song.song_id = songID
            if song.waiter is None:
                song.waiter = Event()
                song.waiter.clear()
            self.cache[songID] = song
            song.yt = fetched[DBTables.SONGS.YT_ID].decode()
            song.spotify = fetched[DBTables.SONGS.SPOTIFY_ID].decode()
            song.song_name = fetched[DBTables.SONGS.REAL_NAME]
            song.duration = fetched[DBTables.SONGS.DURATION]
            song.audio_url = fetched[DBTables.SONGS.AUDIO_URL]
            Thread(target=song.fetch_stream).start()
            song.thumbnail = fetched[DBTables.SONGS.THUMBNAIL]
            song.expiry = fetched[DBTables.SONGS.LAST_UPDATED] + timedelta(hours=5)
            if not asRepeat: self.__renew_expiry(song, None)
            Thread(target=self.__remove_cache, args=(song,)).start()
            if song.waiter is not None:
                song.waiter.set()
                song.waiter = None
            return self.cache[songID]


    def __remove_cache(self, song:SongData, seconds:int= 3600 * 4):
        """
        If any song is not requested for n seconds, remove it from the cache
        :param song: the song to remove
        :param seconds: time to wait in seconds
        :return:
        """
        while (datetime.now() - song.last_fetched_at).total_seconds() < seconds+5: sleep(1)
        if song.song_id in self.cache:
            del self.cache[song.song_id]


    def __renew_expiry(self, song:SongData, url:str|None):
        """
        Wait for expiry and renew if required
        :param song: song to renew
        :param url: fetched audio_url to use the url directly or None to fetch it manually
        :return:
        """
        if url:
            song.audio_url = url
            Thread(target=song.fetch_stream).start()
            song.expiry = datetime.now()+timedelta(hours=5)
            song.last_fetched_at = datetime.now()
        elif datetime.now() > song.expiry:
            self.__fetch_new(song, UrlTypes.YT_URL, song.yt)
        else: return
        self.SQLConn.execute(f"UPDATE {DBTables.SONGS.TABLE_NAME} SET {DBTables.SONGS.LAST_UPDATED}=NOW(), {DBTables.SONGS.AUDIO_URL}=? WHERE {DBTables.SONGS.SONG_ID}=?", [song.audio_url, song.song_id])


    def get_song_id(self, string:str) -> str|None:
        """
        Find relevant song based on name or URL provided
        :param string: name or url to search for
        :return: 30-character unique ID for the song or None if the string is a playlist or other unknown type
        """
        category, string = self.URLHandler.strip(string)
        found = self.SQLConn.execute(f"SELECT {DBTables.ALIASES.SONG_ID} FROM {DBTables.ALIASES.TABLE_NAME} WHERE {DBTables.ALIASES.STRING}=? LIMIT 1", [string])
        if found: return found[0][DBTables.ALIASES.SONG_ID].decode()
        else: ## No real name matched
            if category == UrlTypes.UNKNOWN: found = self.SQLConn.execute(f"SELECT {DBTables.SONGS.SONG_ID} FROM {DBTables.SONGS.TABLE_NAME} WHERE {DBTables.SONGS.REAL_NAME}=? LIMIT 1", [string])
            elif category == UrlTypes.SPOTIFY_URL: found = self.SQLConn.execute(f"SELECT {DBTables.SONGS.SONG_ID} FROM {DBTables.SONGS.TABLE_NAME} WHERE {DBTables.SONGS.SPOTIFY_ID}=? LIMIT 1", [string])
            elif category == UrlTypes.YT_URL: found = self.SQLConn.execute(f"SELECT {DBTables.SONGS.SONG_ID} FROM {DBTables.SONGS.TABLE_NAME} WHERE {DBTables.SONGS.YT_ID}=? LIMIT 1", [string])
            else: return None
            if found: return found[0][DBTables.SONGS.SONG_ID].decode()
            else: ## No alias name matched
                songID = RandomisedString().AlphaNumeric(30,30)
                song = SongData()
                song.song_id = songID
                self.cache[songID] = song
                song.search_name = self.URLHandler.merge(category, string)
                Thread(target=self.__fetch_new, args=(song, category, string)).start()
                return songID


    def get_song_data(self, songID:str)->SongData:
        """
        Wait for song with the ID to be prepared and then return it
        :param songID: ID to search for
        :return:
        """
        if songID not in self.cache: song = self.__cache_from_db(songID, False)
        else: song = self.cache[songID]
        if song is not None and song.waiter is not None:
            song.waiter.wait()
            if song.repeat_for is not None:
                song = song.repeat_for
                if song.waiter is not None:
                    song.waiter.wait()
            song.last_fetched_at = datetime.now()
            self.__renew_expiry(song, None)
        return song

