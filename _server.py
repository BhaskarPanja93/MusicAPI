from gevent.monkey import patch_all


patch_all()


from typing import Any, Dict
from flask import make_response, request, send_from_directory, Response
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
    """
    Called when a new viewer is connected.
    :param viewer: DynamicWebsite.Viewer holding all parameters of the viewer.
    :return:
    """
    print("Connected: ", viewer.viewerID)
    sendFormCSRF(viewer)


def viewerDisconnectedCallback(viewer:DynamicWebsite.Viewer):
    """
    Called when a new viewer is disconnected.
    :param viewer: DynamicWebsite.Viewer holding all parameters of the viewer.
    :return:
    """
    print("Disconnected: ", viewer.viewerID)


def formReceivedCallback(viewer:DynamicWebsite.Viewer, form:Dict):
    """
    Called when a new viewer is sends a form.
    :param viewer: DynamicWebsite.Viewer holding all parameters of the viewer.
    :param form: The JSON form received
    :return:
    """
    print("Form: ", viewer.viewerID, form)
    if "PURPOSE" not in form: return
    purpose = form.pop("PURPOSE")
    if purpose == "SEARCH_SONG":
        if "STRING" in form and form.get("STRING"):
            songID = SongCache.get_song_id(form.get("STRING"))
            viewer.updateHTML(Template(FileCache.fetch_html(Files.HTML.preparing)).render(songID=songID), "SONG-RESULT", DynamicWebsite.UpdateMethods.update)
            song:SongData = SongCache.get_song_data(songID)
            if song is not None: viewer.updateHTML(Template(FileCache.fetch_html(Files.HTML.prepared)).render(songName=song.song_name, thumbnail=song.thumbnail, duration=song.duration, audioURL=f"/api/audio/{songID}", lyrics=song.lyrics, YT=URLHandler.merge(UrlTypes.YT_URL, song.yt), spotify=URLHandler.merge(UrlTypes.SPOTIFY_URL, song.spotify)), "SONG-RESULT", DynamicWebsite.UpdateMethods.update)
            else: viewer.updateHTML(FileCache.fetch_html(Files.HTML.songNotFound), "SONG-RESULT", DynamicWebsite.UpdateMethods.update)
            sendFormCSRF(viewer)


def customMessageReceivedCallback(viewer:DynamicWebsite.Viewer, message:Any):
    """
    Called when a new viewer sends a message via WS
    :param message: the message received
    :param viewer: DynamicWebsite.Viewer holding all parameters of the viewer.
    :return:
    """
    print("Custom: ", viewer.viewerID, message)


def firstPageRenderer():
    """
    The first page with head body and every element being sent when user first connects
    :return:
    """
    return make_response(Template(FileCache.fetch_html(Files.HTML.index)).render(title=CoreValues.appName, baseURI="" if request.path == "/" else request.path))


def sendFormCSRF(viewer:DynamicWebsite.Viewer):
    """
    Renew CSRF after every form submit
    :param viewer: DynamicWebsite.Viewer to refresh the CSRF for
    :return:
    """
    viewer.updateHTML(viewer.createCSRF("SEARCH_SONG"), "SEARCH-CSRF", DynamicWebsite.UpdateMethods.update)


Logger = CustomisedLogs()
SQLConn = DBHolder(Logger)
FileCache = FileCache()
URLHandler = URLHandler()
SongCache = SongCache(SQLConn.useDB(), Logger, URLHandler)
DWApps = DynamicWebsite(firstPageRenderer, viewerConnectedCallback, viewerDisconnectedCallback, formReceivedCallback, customMessageReceivedCallback, ServerSecrets.fernetKey, CoreValues.appName, CoreValues.webRoute)


@DWApps.baseApp.get(f"/api/prepare/<string>")
def _prepareAPI(string):
    """
    route to prepare/brew the song
    :param string: url/name to search for
    :return: JSON with the song ID
    """
    string = Template(string).render()
    newID = SongCache.get_song_id(string)
    return {"ID": newID}


@DWApps.baseApp.get(f"/api/fetch/<songID>")
def _fetchAPI(songID):
    """
    route to fetch the prepared song
    :param songID: ID of the song to fetch
    :return: JSON with the song data
    """
    songID = Template(songID).render()
    song = SongCache.get_song_data(songID)
    if song is None: return {"ERROR": "Song not found"}
    return song.full_dict()


@DWApps.baseApp.get(f"/api/audio/<songID>")
def _fetchAudio(songID):
    """
    route to fetch the song's audio as stream incase the default audio_url doesn't work
    :param songID:
    :return:
    """
    songID = Template(songID).render()
    song = SongCache.get_song_data(songID)
    return Response(song.fetch_data_from_stream())


@DWApps.baseApp.get("/cd")
def _cd():
    """
    Fetch dynamicWebsite or hotwire js
    :return:
    """
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

