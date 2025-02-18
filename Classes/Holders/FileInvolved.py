from Hidden.Secrets import folderLocation


class Folders:
    static = folderLocation/"Static"
    hidden = folderLocation/"Hidden"

    temp = folderLocation/"Temp"
    autoTemp = temp/"Auto"

    css = static/"css"
    font = static/"font"
    html = static/"html"
    image = static/"image"
    js = static/"js"
    text = static/"text"
    video = static/"video"


class Files:
    class HTML:
        index = Folders.html/"Index.html"
        preparing = Folders.html/"Preparing.html"
        prepared = Folders.html/"Prepared.html"
        songNotFound = Folders.html/"SongNotFound.html"

    class JS:
        dynamicWebsite = Folders.js/"dynamicWebsite.js"
        hotwire = Folders.js/"hotwire.js"

    class COOKIE:
        YT = Folders.hidden/"YT-COOKIES"