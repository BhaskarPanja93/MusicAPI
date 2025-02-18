from pooledMySQL import PooledMySQL
from rateLimitedQueues import RateLimitedQueues
from spotipy import Spotify, SpotifyClientCredentials, CacheFileHandler


from Classes.Holders.DBTables import DBTables
from Classes.Holders.FileInvolved import Folders


class SpotifyAPI:
    def __init__(self, API:Spotify, rateLimiter:RateLimitedQueues):
        self.API = API
        self.rateLimiter = rateLimiter


class SpotifyAPICollection:
    def __init__(self, SQLConn:PooledMySQL):
        self.apis:list[SpotifyAPI] = []
        self.lastUsed = -1
        for clientCreds in SQLConn.execute(f"SELECT {DBTables.SPOTIFY_APIS.CLIENT_ID}, {DBTables.SPOTIFY_APIS.SECRET} from {DBTables.SPOTIFY_APIS.TABLE_NAME}"):
            clientID = clientCreds[DBTables.SPOTIFY_APIS.CLIENT_ID]
            secret = clientCreds[DBTables.SPOTIFY_APIS.SECRET]
            self.apis.append(SpotifyAPI(Spotify(auth_manager=SpotifyClientCredentials(client_id=clientID, client_secret=secret, cache_handler=CacheFileHandler(Folders.autoTemp/clientID))), RateLimitedQueues(1)))
    def fetchAPI(self):
        self.lastUsed += 1
        if self.lastUsed == len(self.apis): self.lastUsed = 0
        return self.apis[self.lastUsed]