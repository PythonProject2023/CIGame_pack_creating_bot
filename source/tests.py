"""Module with functions tests."""

import unittest
import xml.etree.ElementTree as ET
import xml_parser
import os
import shutil

unittest.TestLoader.sortTestMethodsUsing = None


class RedisStorageMock(object):
    """Object that is used like Redis storage (singletone)."""

    dictionary = {}

    def __new__(cls):  # noqa: D102
        if not hasattr(cls, 'instance'):
            cls.instance = super(type(cls), cls).__new__(cls)
        return cls.instance

    def get_value(self, chat_id, user_id, key):  # noqa: D102
        return self.dictionary[(chat_id, user_id)][key]

    def set_data(self, chat_id, user_id, key, value):  # noqa: D102
        if (chat_id, user_id) not in self.dictionary.keys():
            self.dictionary[(chat_id, user_id)] = {}
        self.dictionary[(chat_id, user_id)][key] = value


class TestFileFunctions(unittest.TestCase):
    """Class with tests."""

    def ChangeRedisStorageToMock(self):
        """Change usual Redis storage to mock one."""
        xml_parser.CreateRedisStorage = lambda: RedisStorageMock()

    def test1CreatePack(self):
        """Test creating pack."""
        xml_parser.CreateNewPack(1111, 2222, 'sample_pack')
        path_to_pack = os.path.join(xml_parser.packs_directory,
                                    '2222', 'sample_pack')
        assert os.path.exists(path_to_pack)
        assert os.path.exists(os.path.join(path_to_pack, 'content.xml'))
        try:
            ET.parse(os.path.join(path_to_pack, 'content.xml'))
        except Exception:
            raise AssertionError

    def test2GetPacks(self):
        """Test getting packs list."""
        xml_parser.CreateNewPack(1111, 2222, 'sample_pack')
        path_to_arc = os.path.join(xml_parser.packs_directory, '2222',
                                   'sample_pack.siq')
        with open(path_to_arc, "w") as file:
            file.write('ababab')
        assert xml_parser.GetUserPacks(1111, 2222) == ['sample_pack']
        os.remove(path_to_arc)

    def test3DeletePack(self):
        """Test deleting pack."""
        xml_parser.DeletePack(1111, 2222, 'sample_pack')
        path_to_pack = os.path.join(xml_parser.packs_directory,
                                    '2222', 'sample_pack')
        assert not os.path.exists(path_to_pack)

    def test4CreateNewRound(self):
        """Test creating new round."""
        self.ChangeRedisStorageToMock()
        RedisStorageMock().set_data(1111, 2222, 'pack', 'sample_pack')
        xml_parser.CreateNewPack(1111, 2222, 'sample_pack')
        xml_parser.CreateNewRound(1111, 2222, 'round1')
        tree = ET.parse(os.path.join(xml_parser.packs_directory, '2222',
                                     'sample_pack', 'content.xml'))
        root = tree.getroot()
        rounds = root.find('rounds')
        assert len(rounds.findall('round')) == 1

    def test5GetRounds(self):
        """Test getting rounds list."""
        self.ChangeRedisStorageToMock()
        assert xml_parser.GetRounds(1111, 2222) == ['round1']

    def test6DeleteRound(self):
        """Test deleting round."""
        self.ChangeRedisStorageToMock()
        xml_parser.DeleteRound(1111, 2222, 'round1')
        tree = ET.parse(os.path.join(xml_parser.packs_directory, '2222',
                                     'sample_pack', 'content.xml'))
        root = tree.getroot()
        rounds = root.find('rounds')
        assert len(rounds.findall('round')) == 0

    @classmethod
    def tearDownClass(cls):
        """Delete sample user folder."""
        shutil.rmtree(os.path.join(xml_parser.packs_directory, '2222'))
