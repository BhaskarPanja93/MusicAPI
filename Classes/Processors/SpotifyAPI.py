from pooledMySQL import PooledMySQL
from rateLimitedQueues import RateLimitedQueues
from spotipy import Spotify, SpotifyClientCredentials, CacheFileHandler
from itertools import cycle


from Classes.Holders.DBTables import DBTables
from Classes.Holders.FileInvolved import Folders


class SpotifyAPI:
    def __init__(self, API:Spotify, rateLimiter:RateLimitedQueues):
        self.API = API
        self.rate_limiter = rateLimiter


class SpotifyAPICollection:
    """
    Holds all Spotify APIS
    """
    def __init__(self, SQLConn:PooledMySQL):
        self.__apis:list[SpotifyAPI] = []
        self.apis = cycle(self.__apis)
        for client_creds in SQLConn.execute(f"SELECT {DBTables.SPOTIFY_APIS.CLIENT_ID}, {DBTables.SPOTIFY_APIS.SECRET} from {DBTables.SPOTIFY_APIS.TABLE_NAME}"):
            client_id = client_creds[DBTables.SPOTIFY_APIS.CLIENT_ID]
            secret = client_creds[DBTables.SPOTIFY_APIS.SECRET]
            self.__apis.append(SpotifyAPI(Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=secret, cache_handler=CacheFileHandler(Folders.autoTemp / client_id))), RateLimitedQueues(1)))


    def fetch_api(self):
        """
        Fetch an API when called for
        :return:
        """
        return self.apis.__next__()