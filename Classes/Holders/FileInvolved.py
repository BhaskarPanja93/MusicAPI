from Hidden.Secrets import folderLocation


class Folders:
    static = folderLocation/"Static"

    temp = folderLocation/"Temp"
    autoTemp = temp/"AutoTemp"

    css = static/"css"
    font = static/"font"
    html = static/"html"
    image = static/"image"
    js = static/"js"
    text = static/"text"
    video = static/"video"


class Files:
    class HTML:
        index = Folders.html/"index.html"
    class JS:
        dynamicWebsite = Folders.js/"dynamicWebsite.js"
        hotwire = Folders.js/"hotwire.js"