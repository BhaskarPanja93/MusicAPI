from os import stat
from Classes.Holders.FileInvolved import Folders


class FileCache:
    def __init__(self):
        """
        File cache holder that auto-re-caches upon file modification
        """
        self.known_elements:dict[str, dict[str, list[float | str | bytes]]] = {}


    def __update_cache(self, fileType, itemName) -> None:
        """
        Adds filedata to cache when called for
        :param fileType: must be a known filetype with the folder
        :param itemName: filename in the folder
        :return:
        """
        new = ""
        try: new = open(fileType / itemName, "r").read()
        except:
            try: new = open(fileType / itemName, "rb").read()
            except: pass
        self.known_elements[fileType][itemName] = [stat(fileType / itemName).st_mtime, new]


    def fetch_file(self, file_type, item_name) -> str|bytes:
        """
        Fetch any filetype from any folder, given the folder is present
        :param file_type: known filetype with the folder
        :param item_name: filename in the folder
        :return: str or byte data of the file
        """
        if file_type not in self.known_elements: self.known_elements[file_type] = {}
        if item_name not in self.known_elements[file_type] or [stat(file_type / item_name).st_mtime != self.known_elements[file_type][item_name][0]]:
            self.__update_cache(file_type, item_name)
        return self.known_elements[file_type][item_name][1]


    def fetch_html(self, itemName: str) -> str:
        """
        Modification of FileCache.fetch_file specific to html filetype
        :param itemName: filename in the folder
        :return: str or byte data of the file
        """
        return self.fetch_file(Folders.html, itemName)


    def fetch_js(self, itemName: str) -> str:
        """
        Modification of FileCache.fetch_file specific to js filetype
        :param itemName: filename in the folder
        :return: str or byte data of the file
        """
        return self.fetch_file(Folders.js, itemName)


    def fetch_css(self, itemName: str) -> str:
        """
        Modification of FileCache.fetch_file specific to css filetype
        :param itemName: filename in the folder
        :return: str or byte data of the file
        """
        return self.fetch_file(Folders.css, itemName)