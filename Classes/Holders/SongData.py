from datetime import datetime


class SongData:
    def __init__(self):
        self.songID:str = ""
        self.requestedBy:str = ""
        self.songName:str = ""
        self.requestName:str = ""
        self.YT:str = ""
        self.spotify:str = ""
        self.duration:datetime|None = None
        self.audioURL:str = ""
        self.thumbnail:str = ""
        self.expiry:datetime|None = None
        self.lyrics:str = "No Lyrics LOL :)"
        self.lastFetched:datetime|None = None


    def fullDict(self):
        return {
            "ID":self.songID,
            "SONG_NAME":self.songName,
            "YT_ID":self.YT,
            "SPOTIFY_ID":self.spotify,
            "DURATION":self.duration,
            "AUDIO_URL":self.audioURL,
            "THUMBNAIL":self.thumbnail,
            "EXPIRY":self.expiry,
            "LYRICS":self.lyrics
        }


    def read(self, source:dict):
        self.songID = source.get("ID")
        self.songName = source.get("SONG_NAME")
        self.YT = source.get("YT_ID")
        self.spotify = source.get("SPOTIFY_ID")
        self.duration = float(source.get("DURATION"))
        self.audioURL = source.get("AUDIO_URL")
        self.thumbnail = source.get("THUMBNAIL")
        self.expiry = source.get("EXPIRY")
        self.lyrics = source.get("LYRICS")

