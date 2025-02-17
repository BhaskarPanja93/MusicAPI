from re import compile as re_compile, search as re_search
from threading import Thread, Event
from time import sleep

from customisedLogs import CustomisedLogs
from pooledMySQL import PooledMySQL
from randomisedString import RandomisedString

from Classes.Holders.DBTables import DBTables
from Classes.Holders.SongData import SongData
from Classes.Holders.UrlTypes import UrlTypes


class SongProcessor:
    def __init__(self, SQLConn:PooledMySQL, logger:CustomisedLogs):
        self.SQLConn = SQLConn
        self.logger = logger
        self.cache:dict[str, SongData] = {}
        self.watchers:dict[str, Event] = {}


    @staticmethod
    def __isValidURL(string: str) -> bool:
        if not isinstance(string, str):
            return False
        regex = re_compile(r'^https?://')
        if not re_search(regex, string):
            return False
        forbidden_substrings = ["//", "playlist", "album", "artist"]
        for sub in forbidden_substrings:
            if sub in string:
                return False
        return True


    @staticmethod
    def __cleanedTrackName(trackName: str, cleanSymbols: bool = True, size=500) -> str:
        trackName = trackName.replace('"', "'")
        if cleanSymbols:
            for character in "!@#$%^&*()_+{}|:\"<>?[]\\;',./":
                trackName = trackName.replace(character, " ")
            while "  " in trackName:
                trackName = trackName.replace("  ", " ")
        trackNameWords = trackName.split()
        cleanedTrackName = ""
        for word in trackNameWords:
            if len(cleanedTrackName) + len(word) <= size and word.lower() not in ["official", "(official lyric video)", "(Lyric Video)", "video", "lyrics", "lyric", "audio", ",", "(", ")"]:
                cleanedTrackName += word + " "
        return cleanedTrackName.strip()


    def __strip(self, string: str) -> tuple[UrlTypes, str]:
        if self.__isValidURL(string):
            if "spotify.com" in string:
                if "track/" in string:
                    return UrlTypes.SPOTIFY_URL, string.split("track/")[-1].split("?")[0]
                elif "playlist/" in string:
                    return UrlTypes.SPOTIFY_PLAYLIST, string.split("playlist/")[-1].split("?")[0]
                elif "artist/" in string:
                    return UrlTypes.SPOTIFY_ARTIST, string.split("artist/")[-1].split("?")[0]
                elif "album/" in string:
                    return UrlTypes.SPOTIFY_ALBUM, string.split("album/")[-1].split("?")[0]
            elif "youtube.com" in string or "youtu.be" in string or "music.youtu" in string:
                string = string.replace("?si=", "")  # Remove si parameter if present
                if "playlist?list=" in string:
                    return UrlTypes.YT_PLAYLIST, string.split("?list=")[-1].split("&")[0]
                else:
                    return UrlTypes.YT_URL, string.split("?v=")[-1].split("&")[0]
        return UrlTypes.UNKNOWN, self.__cleanedTrackName(string)


    def __fetchNewSong(self, songID:str, category:UrlTypes, string:str):
        watcher = Event()
        watcher.set()
        self.watchers[songID] = watcher
        sleep(0.001)
        self.cache = SongData() #TODO:


    def __fetchSongFromDB(self, songID:str):
        self.cache[songID] = SongData() #TODO:
        return self.cache[songID]


    def getSongID(self, string:str):
        category, string = self.__strip(string)
        found = []
        if category == UrlTypes.UNKNOWN: found = self.SQLConn.execute(f"SELECT {DBTables.SONGS.SONG_ID} FROM {DBTables.SONGS.TABLE_NAME} WHERE {DBTables.SONGS.REAL_NAME}=? LIMIT 1", [string])
        elif category == UrlTypes.SPOTIFY_URL: found = self.SQLConn.execute(f"SELECT {DBTables.SONGS.SONG_ID} FROM {DBTables.SONGS.TABLE_NAME} WHERE {DBTables.SONGS.SPOTIFY_ID}=? LIMIT 1", [string])
        elif category == UrlTypes.YT_URL: found = self.SQLConn.execute(f"SELECT {DBTables.SONGS.SONG_ID} FROM {DBTables.SONGS.TABLE_NAME} WHERE {DBTables.SONGS.YT_ID}=? LIMIT 1", [string])
        if found: return found[0][DBTables.SONGS.SONG_ID]
        else: ## No real name matching
            found = self.SQLConn.execute(f"SELECT {DBTables.ALIASES.SONG_ID} FROM {DBTables.ALIASES.TABLE_NAME} WHERE {DBTables.ALIASES.STRING}=? LIMIT 1", [string])
            if found: return found[0][DBTables.ALIASES.SONG_ID]
            else: ## No alias name matching
                songID = RandomisedString().AlphaNumeric(30,30)
                Thread(target=self.__fetchNewSong, args=(songID, category, string,)).start()
                return songID


    def getSongData(self, songID:str)->SongData:
        if songID in self.watchers: self.watchers[songID].wait()
        if songID in self.cache: return self.cache[songID]
        else: return self.__fetchSongFromDB(songID)

