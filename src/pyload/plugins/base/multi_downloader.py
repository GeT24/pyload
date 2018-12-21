# -*- coding: utf-8 -*-
import re

from pyload.core.network.exceptions import Fail
from .simple_downloader import SimpleDownloader


class MultiDownloader(SimpleDownloader):
    __name__ = "MultiDownloader"
    __type__ = "downloader"
    __version__ = "0.67"
    __status__ = "stable"

    __pyload_version__ = "0.5"

    __pattern__ = r"^unmatchable$"
    __config__ = [
        ("enabled", "bool", "Activated", True),
        ("use_premium", "bool", "Use premium account if available", True),
        ("fallback", "bool", "Fallback to free download if premium fails", False),
        ("chk_filesize", "bool", "Check file size", True),
        ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10),
        ("revert_failed", "bool", "Revert to standard download if fails", True),
    ]

    __description__ = """Multi downloader plugin"""
    __license__ = "GPLv3"
    __authors__ = [
        ("Walter Purcaro", "vuolter@gmail.com"),
        ("GammaC0de", "nitzo2001[AT]yahoo[DOT]com"),
    ]

    OFFLINE_PATTERN = r"^unmatchable$"
    TEMP_OFFLINE_PATTERN = r"^unmatchable$"

    LEECH_HOSTER = False

    def init(self):
        self.PLUGIN_NAME = self.pyload.pluginManager.hosterPlugins.get(self.classname)[
            "name"
        ]

    def _log(self, level, plugintype, pluginname, args, kwargs):
        args = (self.PLUGIN_NAME,) + args
        return SimpleDownloader._log(self, level, plugintype, pluginname, args, kwargs)

    def setup(self):
        self.no_fallback = True
        self.chunk_limit = 1
        self.multiDL = bool(self.account)
        self.resume_download = self.premium

    # TODO: Recheck in 0.6.x
    def setup_base(self):
        klass = self.pyload.pluginManager.loadClass("downloader", self.classname)
        self.get_info = klass.get_info

        SimpleDownloader.setup_base(self)

    def _prepare(self):
        SimpleDownloader._prepare(self)

        if self.DIRECT_LINK is None:
            self.direct_dl = self.__pattern__ != r"^unmatchable$" and re.match(
                self.__pattern__, self.pyfile.url
            )

        else:
            self.direct_dl = self.DIRECT_LINK

    def _process(self, thread):
        try:
            SimpleDownloader._process(self, thread)

        except Fail as exc:
            hdict = self.pyload.pluginManager.hosterPlugins.get(
                self.pyfile.pluginname, {}
            )
            if self.config.get("revert_failed", True) and hdict.get("new_module"):
                tmp_module = hdict.pop("new_module", None)
                tmp_name = hdict.pop("new_name", None)

                self.pyfile.plugin = None
                self.pyfile.initPlugin()

                hdict["new_module"] = tmp_module
                hdict["new_name"] = tmp_name

                self.restart(self._("Revert to original hoster plugin"))

            else:
                raise

    def handle_premium(self, pyfile):
        return self.handle_free(pyfile)

    def handle_free(self, pyfile):
        if self.premium:
            raise NotImplementedError

        else:
            self.fail(self._("MultiDownloader download failed"))