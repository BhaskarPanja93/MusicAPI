from gevent.monkey import patch_all


patch_all()


from typing import Any, Dict
from flask import make_response, request, send_from_directory
from customisedLogs import CustomisedLogs
from jinja2 import Template


from Hidden.dynamicWebsite import DynamicWebsite
from Hidden.Secrets import ServerSecrets, CoreValues


from Classes.Holders.UrlTypes import UrlTypes
from Classes.Holders.FileInvolved import Files, Folders
from Classes.Processors.URLHandler import URLHandler
from Classes.Processors.WSGIElements import WSGIRunner
from Classes.Processors.DBHolder import DBHolder
from Classes.Processors.FileCache import FileCache
from Classes.Processors.SongProcessor import SongCache, SongData


def viewerConnectedCallback(viewer:DynamicWebsite.Viewer):
    print("Connected: ", viewer.viewerID)
    sendFormCSRF(viewer)


def viewerDisconnectedCallback(viewer:DynamicWebsite.Viewer):
    print("Disconnected: ", viewer.viewerID)


def formReceivedCallback(viewer:DynamicWebsite.Viewer, form:Dict):
    print("Form: ", viewer.viewerID, form)
    if "PURPOSE" not in form: return
    purpose = form.pop("PURPOSE")
    if purpose == "SEARCH_SONG":
        if "STRING" in form and form.get("STRING"):
            songID = SongCache.getSongID(form.get("STRING"))
            viewer.updateHTML(Template(FileCache.fetchStaticHTML(Files.HTML.preparing)).render(songID=songID), "SONG-RESULT", DynamicWebsite.UpdateMethods.update)
            song:SongData = SongCache.getSongData(songID)
            if song is not None: viewer.updateHTML(Template(FileCache.fetchStaticHTML(Files.HTML.prepared)).render(songName=song.songName, thumbnail=song.thumbnail, duration=song.duration, audioURL=song.audioURL, lyrics=song.lyrics, YT=URLHandler.merge(UrlTypes.YT_URL, song.YT), spotify=URLHandler.merge(UrlTypes.SPOTIFY_URL, song.spotify)), "SONG-RESULT", DynamicWebsite.UpdateMethods.update)
            else: viewer.updateHTML(FileCache.fetchStaticHTML(Files.HTML.songNotFound), "SONG-RESULT", DynamicWebsite.UpdateMethods.update)
            sendFormCSRF(viewer)


def customMessageReceivedCallback(viewer:DynamicWebsite.Viewer, message:Any):
    print("Custom: ", viewer.viewerID, message)


def firstPageRenderer():
    return make_response(Template(FileCache.fetchStaticHTML(Files.HTML.index)).render(title=CoreValues.appName, baseURI="" if request.path=="/" else request.path))


def sendFormCSRF(viewer:DynamicWebsite.Viewer):
    viewer.updateHTML(viewer.createCSRF("SEARCH_SONG"), "SEARCH-CSRF", DynamicWebsite.UpdateMethods.update)


Logger = CustomisedLogs()
SQLConn = DBHolder(Logger)
FileCache = FileCache()
URLHandler = URLHandler()
SongCache = SongCache(SQLConn.useDB(), Logger, URLHandler)
DWApps = DynamicWebsite(firstPageRenderer, viewerConnectedCallback, viewerDisconnectedCallback, formReceivedCallback, customMessageReceivedCallback, ServerSecrets.fernetKey, CoreValues.appName, CoreValues.webRoute)


@DWApps.baseApp.get(f"{CoreValues.prepareAPIRoute}/<string>")
def _prepareAPI(string):
    string = Template(string).render()
    newID = SongCache.getSongID(string)
    return {"ID": newID}


@DWApps.baseApp.get(f"{CoreValues.fetchAPIRoute}/<songID>")
def _fetchAPI(songID):
    songID = Template(songID).render()
    song = SongCache.getSongData(songID)
    if song is None: return {"ERROR": "Song not found"}
    return song.fullDict()


@DWApps.baseApp.get("/cd")
def _cd():
    if request.args.get("type") == "js":
        if request.args.get("name") == "dynamicWebsite.js":
            return send_from_directory(Folders.js, request.args.get("name"), as_attachment=True), 200
        elif request.args.get("name") == "hotwire.js":
            return send_from_directory(Folders.js, request.args.get("name"), as_attachment=True), 200
    return ""


@DWApps.baseApp.before_request
def _modHeadersBeforeRequest():
    """
    Before any request goes to any route, it passes through this function.
    Applies user remote address correctly (received from proxy)
    :return:
    """
    if request.remote_addr == "127.0.0.1":
        if request.environ.get("HTTP_X_FORWARDED_FOR") is not None:
            address = request.environ.get("HTTP_X_FORWARDED_FOR")
        else: address = "LOCALHOST"
        request.remote_addr = address
    if request.environ.get("HTTP_X_FORWARDED_PATH") is not None:
        request.path = request.environ.get("HTTP_X_FORWARDED_PATH")
    else:
        request.path = ""
    if request.environ.get("HTTP_X_FORWARDED_PROTO") is not None:
        request.scheme = request.environ.get("HTTP_X_FORWARDED_PROTO")


WSGIRunner(DWApps.baseApp, CoreValues.webPort, CoreValues.webRoute, Logger)

