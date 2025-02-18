from datetime import datetime
from datetime import timedelta
from threading import Thread, Event
from time import sleep


from customisedLogs import CustomisedLogs
from pooledMySQL import PooledMySQL
from randomisedString import RandomisedString


from Classes.Holders.DBTables import DBTables
from Classes.Holders.SongData import SongData
from Classes.Holders.UrlTypes import UrlTypes
from Classes.Processors.SpotifyAPI import SpotifyAPICollection
from Classes.Processors.URLHandler import URLHandler
from Classes.Processors.YTDLP import YTDLP


class SongCache:
    def __init__(self, SQLConn:PooledMySQL, Logger:CustomisedLogs, URLHandler:URLHandler):
        self.SQLConn = SQLConn
        self.logger = Logger
        self.cache:dict[str, SongData] = {}
        self.YTDLP = YTDLP(self.logger)
        self.SpotifyAPI = SpotifyAPICollection(self.SQLConn)
        self.URLHandler = URLHandler


    def __addToDB(self, song:SongData):
        fetched = self.SQLConn.execute(f"SELECT {DBTables.SONGS.SONG_ID} FROM {DBTables.SONGS.TABLE_NAME} WHERE ({DBTables.SONGS.REAL_NAME}=? AND {'TRUE' if song.songName else 'FALSE'}) OR ({DBTables.SONGS.YT_ID}=? AND {'TRUE' if song.YT else 'FALSE'}) OR ({DBTables.SONGS.SPOTIFY_ID}=? AND {'TRUE' if song.spotify else 'FALSE'}) LIMIT 1", [song.songName, song.YT, song.spotify])
        if fetched:
            realID = fetched[0][DBTables.SONGS.SONG_ID].decode()
            print('duplicate found', song.songID, realID)
            if realID not in self.cache: self.__DBToCache(realID, True)
            realSong = self.cache[realID]
            song.realSong = realSong
            self.__resetExpiry(realSong, song.audioURL)
            self.SQLConn.execute(f"INSERT INTO {DBTables.ALIASES.TABLE_NAME} VALUES (?, ?)", [realID, song.searchName])
        else:
            print('adding to db', song.songID)
            self.SQLConn.execute(f"INSERT INTO {DBTables.SONGS.TABLE_NAME} VALUES (?, ?, ?, ?, ?, ?, ?, NOW())", [song.songID, song.songName, song.spotify, song.YT, song.duration, song.thumbnail, song.audioURL])
            if song.searchName != song.songName:
                self.SQLConn.execute(f"INSERT INTO {DBTables.ALIASES.TABLE_NAME} VALUES (?, ?)", [song.songID, song.searchName])


    def __newSongFetch(self, song:SongData, category:UrlTypes, string:str):
        if song.waiter is None:
            song.waiter = Event()
            song.waiter.clear()
        if category == UrlTypes.YT_URL:
            url = self.URLHandler.merge(category, string)
            r = self.YTDLP.fetch(url)
            song.songName = r.get("title")
            song.YT = string
            song.duration = r.get("duration")
            song.audioURL = r.get("url")
            song.thumbnail = None if r.get("thumbnails") is None else r.get("thumbnails")[0].get('url')

        elif category == UrlTypes.SPOTIFY_URL:
            details = self.SpotifyAPI.fetchAPI().API.track(string)
            artists = " ".join([_["name"] for _ in details['artists']])
            song.songName = details["name"] + " " + artists
            if song.songName:
                self.__newSongFetch(song, UrlTypes.UNKNOWN, song.songName)

        elif category == UrlTypes.UNKNOWN:
            r = self.YTDLP.fetch(string + " lyrics")
            song.YT = r['entries'][0]['id']
            song.songName = r["entries"][0]["title"]
            song.audioURL = r['entries'][0]['url']
            song.duration = r['entries'][0]['duration']
            song.thumbnail = r['entries'][0]['thumbnail'] if r['entries'][0]['thumbnail'] else None

        if not song.spotify:
            try:
                items = self.SpotifyAPI.fetchAPI().API.search(song.songName.lower(), type="track")['tracks']['items']
                chosen = items[1]
                for item in items:
                    if item["name"].lower() == song.songName.lower() or item["name"].lower() in song.songName.lower():
                        chosen = item
                        break
                song.spotify = chosen["id"]
            except:
                song.spotify = ""

        song.expiry = datetime.now() + timedelta(hours=5)
        self.__addToDB(song)
        if song.waiter is not None:
            song.waiter.set()
            song.waiter = None
        Thread(target=self.__removeFromCache, args=(song,)).start()


    def __DBToCache(self, songID:str, asRepeat) -> SongData|None:
        fetched = self.SQLConn.execute(f"SELECT * FROM {DBTables.SONGS.TABLE_NAME} WHERE {DBTables.SONGS.SONG_ID}=?", [songID])
        if fetched:
            fetched = fetched[0]
            song = SongData()
            song.songID = songID
            if song.waiter is None:
                song.waiter = Event()
                song.waiter.clear()
            self.cache[songID] = song
            song.YT = fetched[DBTables.SONGS.YT_ID].decode()
            song.spotify = fetched[DBTables.SONGS.SPOTIFY_ID].decode()
            song.songName = fetched[DBTables.SONGS.REAL_NAME]
            song.duration = fetched[DBTables.SONGS.DURATION]
            song.audioURL = fetched[DBTables.SONGS.AUDIO_URL]
            song.thumbnail = fetched[DBTables.SONGS.THUMBNAIL]
            song.expiry = fetched[DBTables.SONGS.LAST_UPDATED] + timedelta(hours=5)
            print("DB TO CACHE", songID)
            if not asRepeat: self.__resetExpiry(song, None)
            Thread(target=self.__removeFromCache, args=(song,)).start()
            if song.waiter is not None:
                song.waiter.set()
                song.waiter = None
            return self.cache[songID]


    def __removeFromCache(self, song:SongData, seconds:int=3600*4):
        while (datetime.now() - song.lastFetched).total_seconds() < seconds+5: sleep(1)
        if song.songID in self.cache:
            del self.cache[song.songID]
            print("CLEARED FROM CACHE", song.songID)


    def __resetExpiry(self, song:SongData, url):
        if url:
            song.audioURL = url
            song.expiry = datetime.now()+timedelta(hours=5)
            song.lastFetched = datetime.now()
        elif datetime.now() > song.expiry:
            self.__newSongFetch(song, UrlTypes.YT_URL, song.YT)
        else: return
        self.SQLConn.execute(f"UPDATE {DBTables.SONGS.TABLE_NAME} SET {DBTables.SONGS.LAST_UPDATED}=NOW(), {DBTables.SONGS.AUDIO_URL}=? WHERE {DBTables.SONGS.SONG_ID}=?", [song.audioURL, song.songID])


    def getSongID(self, string:str):
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
                song.songID = songID
                self.cache[songID] = song
                song.searchName = self.URLHandler.merge(category, string)
                Thread(target=self.__newSongFetch, args=(song, category, string)).start()
                return songID


    def getSongData(self, songID:str)->SongData:
        if songID not in self.cache: song = self.__DBToCache(songID, False)
        else: song = self.cache[songID]
        if song is not None and song.waiter is not None:
            song.waiter.wait()
            if song.realSong is not None:
                song = song.realSong
                if song.waiter is not None:
                    song.waiter.wait()
            song.lastFetched = datetime.now()
            self.__resetExpiry(song, None)
        return song

