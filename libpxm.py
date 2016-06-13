from __future__ import print_function, unicode_literals
import biplist
import sqlite3
from collections import namedtuple
import uuid
import struct
import tempfile
import os.path

__author__ = 'Ethan Randall'


PXMLayerTypes = namedtuple('PXMLayerTypes',
                           ['bitmap', 'vector']
                           )('com.pixelmatorteam.pixelmator.layer.bitmap',
                             'com.pixelmatorteam.pixelmator.layer.vector')


class PXMFile(object):
    def __init__(self):
        self.root_plist = {}
        self.layers = []
        self.layers_dict = {}

    def build_layer_dict(self):
        for l in self.layers:
            assert isinstance(l, PXMLayer)
            self.layers_dict[l.uuid] = l


class PXMFileReader(object):
    def __init__(self, pxm_fp1):
        with open(pxm_fp1, 'rb') as pxm_fd1:
            assert (struct.unpack('<8s', pxm_fd1.read(8))[0] == 'PXMDMETA'), 'Invalid magic number.'
            h_pl_len = struct.unpack('<i', pxm_fd1.read(4))[0]
            h_pl = biplist.readPlistFromString(pxm_fd1.read(h_pl_len))

            d1 = dict(zip([(h_pl['$objects'][k]) for k in h_pl['$objects'][1]['NS.keys']],
                      [(h_pl['$objects'][v]) for v in h_pl['$objects'][1]['NS.objects']]))

            d1['PTImageIOFormatBasicMetaLayerNamesInfoKey'] = \
                [(h_pl['$objects'][v1].get('NS.string')) for v1 in
                 d1['PTImageIOFormatBasicMetaLayerNamesInfoKey']['NS.objects']]

            d1['PTImageIOFormatBasicMetaVersionInfoKey'] = \
                dict(zip([(h_pl['$objects'][k]) for k in d1['PTImageIOFormatBasicMetaVersionInfoKey']['NS.keys']],
                         [(h_pl['$objects'][v]) for v in d1['PTImageIOFormatBasicMetaVersionInfoKey']['NS.objects']]))

            d1['PTImageIOFormatBasicMetaVersionInfoKey']['PTImageIOPlatformMacOS'] = \
                dict(zip([(h_pl['$objects'][k]) for k in
                          d1['PTImageIOFormatBasicMetaVersionInfoKey']['PTImageIOPlatformMacOS']['NS.keys']],
                         [(h_pl['$objects'][v]) for v in
                          d1['PTImageIOFormatBasicMetaVersionInfoKey']['PTImageIOPlatformMacOS']['NS.objects']]))

            self.pmx_fo = PXMFile()
            self.pmx_fo.root_plist = d1

            pxm_fd1.read(43)

            sql_bytes = pxm_fd1.read()

        self.sql_db = PXMSqlDB(sql_bytes)

        for row1 in self.sql_db.cursor.execute(
            "SELECT layer_uuid, parent_uuid, index_at_parent, type from document_layer;"):
            self.pmx_fo.layers.append(PXMLayer.from_row(*row1))

        self.pmx_fo.build_layer_dict()
        for row2 in self.sql_db.cursor.execute("SELECT layer_uuid, name, value from layer_info;"):
            self.pmx_fo.layers_dict[row2[0]].traits[row2[1]] = row2[2]

        for l in self.pmx_fo.layers:
            l.parse_trait_plist()

        print("hi")


class PXMSqlDB(object):
    T_NAMES = ('document_info', 'document_layer', 'layer_info')

    def __init__(self, sql_db_bytes):
        self.temp_fd = tempfile.NamedTemporaryFile(mode='rwb', suffix=".db", delete=False)
        temp_fn = os.path.abspath(self.temp_fd.name)
        self.temp_fd.close()
        with open(temp_fn, 'wb') as db_fd:
            db_fd.write(sql_db_bytes)

        self.conn = sqlite3.connect(temp_fn)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        print(*self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';"))

    def __del__(self):
        self.conn.close()
        self.temp_fd.delete = True
        self.temp_fd.close()


class PXMDocInfo(object):
    def __init__(self):
        pass


class PXMLayer(object):
    def __init__(self):
        self.uuid = uuid.uuid4()
        self.parent_uuid = None
        self._index_at_parent = -1
        self._type = None
        self.traits = {}
        self.trait_plist = None

    @classmethod
    def from_row(cls, *cols):
        nlayer = cls()
        assert len(cols) == 4, 'Expected 4 columns'
        nlayer.uuid = cols[0]
        nlayer.parent_uuid = cols[1]
        nlayer.index_at_parent = cols[2]
        nlayer.type = cols[3]
        return nlayer

    @property
    def index_at_parent(self):
        if self._index_at_parent == -1:
            raise AttributeError(self._index_at_parent)
        else:
            return self._index_at_parent

    @index_at_parent.setter
    def index_at_parent(self, value):
        if isinstance(value, int) and value >= 0:
            self._index_at_parent = value
        else:
            raise ValueError('Not a valid index!')

    @property
    def type(self):
        if self._type is None:
            raise AttributeError(self._type)
        else:
            return self._type

    @type.setter
    def type(self, value):
        if value in PXMLayerTypes._fields:  # is 'bitmap' or 'vector'
            self._type = PXMLayerTypes[PXMLayerTypes._fields.index(value)]
        elif value in PXMLayerTypes:
            self._type = value
        else:
            raise ValueError('Not a valid layer type!')

    def parse_trait_plist(self):
        if 'PTImageIOFormatLayerSpecificDataInfoKey' in self.traits.keys():
            self.trait_plist = biplist.readPlistFromString(self.traits['PTImageIOFormatLayerSpecificDataInfoKey'])


TEST_PXM = "/Users/ethan/Pictures/RyanProjects/ReapersTouch/ReapersTouch 2/0Reaper.pxm"
pxm1 = PXMFileReader(TEST_PXM)
