from os import stat
from Classes.Holders.FileInvolved import Folders


class FileCache:
    def __init__(self):
        self.knownElements:dict[str, dict[str, list[float|str|bytes]]] = {}


    def __updateCache(self, fileType, itemName):
        new = ""
        try: new = open(fileType / itemName, "r").read()
        except:
            try: new = open(fileType / itemName, "rb").read()
            except: pass
        self.knownElements[fileType][itemName] = [stat(fileType / itemName).st_mtime, new]


    def __fetchFile(self, fileType, itemName) -> str:
        if fileType not in self.knownElements: self.knownElements[fileType] = {}
        if itemName not in self.knownElements[fileType] or [stat(fileType / itemName).st_mtime != self.knownElements[fileType][itemName][0]]:
            self.__updateCache(fileType, itemName)
        return self.knownElements[fileType][itemName][1]


    def fetchStaticHTML(self, itemName: str) -> str:
        return self.__fetchFile(Folders.html, itemName)


    def fetchStaticJS(self, itemName: str) -> str:
        return self.__fetchFile(Folders.js, itemName)


    def fetchStaticCSS(self, itemName: str) -> str:
        return self.__fetchFile(Folders.css, itemName)