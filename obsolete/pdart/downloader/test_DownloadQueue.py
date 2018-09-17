import datetime
import unittest

from pdart.downloader.DownloaderDB import create_downloader_db_in_memory
from pdart.downloader.DownloadQueue import *

_INIT_DATE = datetime.datetime(1970, 1, 1)


class Test_DownloadQueue(unittest.TestCase):
    def setUp(self):
        # type: () -> None
        self.db = create_downloader_db_in_memory()
        self.db.create_tables()
        self.db.set_last_check(_INIT_DATE, set())
        self.db.set_last_update_datetime('hst_00123', _INIT_DATE)

    def test_get_last_update_datetime(self):
        # type: () -> None
        self.assertEqual(_INIT_DATE,
                         self.db.get_last_update_datetime('hst_00123'))

    def test_set_last_update_datetime(self):
        # type: () -> None
        NEW_DATE = datetime.datetime(2001, 4, 1)
        self.db.set_last_update_datetime('hst_00123', NEW_DATE)
        self.assertEqual(NEW_DATE,
                         self.db.get_last_update_datetime('hst_00123'))

        self.db.set_last_update_datetime('hst_00456', _INIT_DATE)
        self.assertEqual(NEW_DATE,
                         self.db.get_last_update_datetime('hst_00123'))
        self.assertEqual(_INIT_DATE,
                         self.db.get_last_update_datetime('hst_00456'))

    def test_get_last_check(self):
        # type: () -> None
        self.assertEqual((_INIT_DATE, set()), self.db.get_last_check())

    def test_set_last_check(self):
        # type: () -> None
        NEW_DATE = datetime.datetime(2001, 4, 1)
        self.db.set_last_check(NEW_DATE,
                               set(['hst_00666', 'hst_01776', 'hst_02001']))
        self.assertEqual((NEW_DATE,
                          set(['hst_02001', 'hst_01776', 'hst_00666'])),
                         self.db.get_last_check())