from customisedLogs import CustomisedLogs
from rateLimitedQueues import RateLimitedQueues
from yt_dlp import YoutubeDL, cookies

from Hidden.Secrets import folderLocation


class YTDLP:
    def __init__(self, logger:CustomisedLogs):
        self.logger = logger
        self.queue = RateLimitedQueues()
        self.cookiejarCookies = cookies.load_cookies(f"{folderLocation}temp/auto/cookies.txt", None, None)
        self.HEADER_FOR_REQUEST = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.4664.110 Safari/537.36'}
        self.downloaders:list[YoutubeDL] = [
            YoutubeDL({'title': True,
                       'default_search': 'auto',
                       'format': 'bestaudio',
                       "quiet": 1,
                       "retries": "infinite",
                       "extractor_retries": 100,
                       "file_access_retries": "infinite",
                       "fragment_retries": "infinite",
                       "socket_timeout":30}),
            YoutubeDL({'title': True,
                       'default_search': 'auto',
                       "quiet": 1,
                       "retries": "infinite",
                       "extractor_retries": 100,
                       "file_access_retries": "infinite",
                       "fragment_retries": "infinite",
                       "socket_timeout":30})
        ]
        for downloader in self.downloaders: downloader.cookiejar.set_cookie(self.cookiejarCookies)


    def fetchYTDLP(self, stringValue:str):
        for downloader in self.downloaders:
            try:
                return downloader.extract_info(stringValue, download=False)
            except:
                pass
