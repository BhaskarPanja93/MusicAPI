from gevent.monkey import patch_all


patch_all()


from typing import Any, Dict
from flask import make_response, request
from customisedLogs import CustomisedLogs
from jinja2 import Template
from threading import Thread


from Hidden.dynamicWebsite import DynamicWebsite
from Hidden.Secrets import ServerSecrets, CoreValues


from Classes.Holders.FileInvolved import Folders, Files
from Classes.Holders.DBTables import DBTables
from Classes.Holders.UrlTypes import UrlTypes
from Classes.Processors.WSGIElements import WSGIRunner
from Classes.Processors.DBHolder import DBHolder
from Classes.Processors.FileCache import FileCache
from Classes.Processors.SongProcessor import SongProcessor













def viewerConnectedCallback(viewer:DynamicWebsite.Viewer):
    print("Connected: ", viewer.viewerID)


def viewerDisconnectedCallback(viewer:DynamicWebsite.Viewer):
    print("Disconnected: ", viewer.viewerID)


def formReceivedCallback(viewer:DynamicWebsite.Viewer, form:Dict):
    print("Form: ", viewer.viewerID, form)


def customMessageReceivedCallback(viewer:DynamicWebsite.Viewer, message:Any):
    print("Custom: ", viewer.viewerID, message)


def firstPageRenderer():
    return make_response(Template(FileCache.fetchStaticHTML(Files.HTML.index)).render(title=CoreValues.appName, baseURI=request.path))


Logger = CustomisedLogs()
SQLConn = DBHolder(Logger)
FileCache = FileCache()
SongProcessor = SongProcessor(SQLConn.useDB(), Logger)
DWApps = DynamicWebsite(firstPageRenderer, viewerConnectedCallback, viewerDisconnectedCallback, formReceivedCallback, customMessageReceivedCallback, ServerSecrets.fernetKey, CoreValues.appName, CoreValues.webRoute)


@DWApps.baseApp.get(f"{CoreValues.prepareAPIRoute}/<string>")
def _prepareAPI(string):
    string = Template(string).render()
    newID = SongProcessor.getSongID(string)
    return {"ID": newID}


@DWApps.baseApp.get(f"{CoreValues.prepareAPIRoute}/<songID>")
def _fetchAPI(songID):
    songID = Template(songID).render()
    song = SongProcessor.getSongData(songID)
    return song.fullDict()


WSGIRunner(DWApps.baseApp, CoreValues.webPort, CoreValues.webRoute, Logger)

