from Classes.Holders.UrlTypes import UrlTypes
from re import compile as re_compile, search as re_search


class URLHandler:


    @staticmethod
    def isValidURL(string: str) -> bool:
        correct = True
        regex = re_compile("https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|%[0-9a-fA-F][0-9a-fA-F])+")
        if not re_search(regex, string):
            correct = False
        else:
            for sub in ["//", "playlist", "album", "artist"]:
                if string.count(sub)>1:
                    correct = False
                    break
        return correct


    @staticmethod
    def cleanedTrackName(trackName: str, cleanSymbols: bool = True, size=500) -> str:
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


    def strip(self, string: str) -> tuple[UrlTypes, str]:
        if self.isValidURL(string):
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
        return UrlTypes.UNKNOWN, self.cleanedTrackName(string)


    @staticmethod
    def merge(category:UrlTypes, string:str) -> str:
        if category == UrlTypes.SPOTIFY_URL:
            return "https://open.spotify.com/track/" + string
        elif category == UrlTypes.SPOTIFY_PLAYLIST:
            return "https://open.spotify.com/playlist/" + string
        elif category == UrlTypes.SPOTIFY_ARTIST:
            return "https://open.spotify.com/artist/" + string
        elif category == UrlTypes.SPOTIFY_ALBUM:
            return "https://open.spotify.com/album/" + string
        elif category == UrlTypes.YT_URL:
            return "https://youtube.com/watch?v=" + string
        elif category == UrlTypes.YT_PLAYLIST:
            return "https://youtube.com/playlist?list=" + string
        elif category == UrlTypes.UNKNOWN:
            return string