import unittest
import sys
import os
import shutil
sys.path.append("../../repositories")
from channelsRepository import ChannelsRepository


class ChannelsRepositoryTest(unittest.TestCase):
    """test class of channelRepository.py
    """

    @classmethod
    def setUpClass(cls):
        """各クラスが実行される直前に一度だけ呼び出される"""
        cls.rps = ChannelsRepository()
        

        print("set up class called.")

    @classmethod
    def tearDownClass(cls):
        """各クラスが実行された直後に一度だけ呼び出される"""
        cls.rps = None
        
    def test_get_channels(self):
        channel_list = self.rps.get_channels("team_id")
        self.assertEqual(len(channel_list), 3)