from customisedLogs import CustomisedLogs
from yt_dlp import YoutubeDL, cookies

from Classes.Holders.FileInvolved import Files


class YTDLP:
    """
    Holds YTLP downloaders
    """
    def __init__(self, logger:CustomisedLogs):
        self.logger = logger
        self.HEADER_FOR_REQUEST = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.4664.110 Safari/537.36'}
        self.downloaders:list[YoutubeDL] = [
            YoutubeDL({'title': True,
                       'default_search': 'auto',
                       'format': 'bestaudio',
                       "silent": 1,
                       "retries": "infinite",
                       "extractor_retries": 100,
                       "file_access_retries": "infinite",
                       "fragment_retries": "infinite",
                       "socket_timeout":30}),
            YoutubeDL({'title': True,
                       'default_search': 'auto',
                       "silent": 1,
                       "retries": "infinite",
                       "extractor_retries": 100,
                       "file_access_retries": "infinite",
                       "fragment_retries": "infinite",
                       "socket_timeout":30})
        ]
        for downloader in self.downloaders: cookies.load_cookies(Files.COOKIE.YT, None, downloader)


    def get_downloader(self, stringValue:str):
        """
        Try with all downloaders based on their priority till the final data is received
        :param stringValue:
        :return:
        """
        for downloader in self.downloaders:
            try:
                return downloader.extract_info(stringValue, download=False)
            except:
                pass
