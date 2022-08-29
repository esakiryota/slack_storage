import unittest
import sys
import os
import shutil
import json
import pprint
sys.path.append("../../repositories")
sys.path.append("../../storage")
from messagesRepository import MessagesRepository

class MessagesRepositryTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """各クラスが実行される直前に一度だけ呼び出される"""
        cls.rps = MessagesRepository()

        print("set up class called.")

    @classmethod
    def tearDownClass(cls):
        """各クラスが実行された直後に一度だけ呼び出される"""
        cls.rps = None
  
    def test_get_all_message_storages(self):
        message_list = self.rps.get_all_message_storages("team_id", "channel_id_1")
        self.assertEqual(len(message_list), 7)
    

    def test_create_message_storage(self):
        data = [{'blocks': [{'block_id': 'ytMK',
                            'elements': [{'elements': [{'text': 'message1', 'type': 'text'}],
                                          'type': 'rich_text_section'}],
                            'type': 'rich_text'}],
                'client_msg_id': 'c9be5620-25e5-4f91-9dfc-0b922a6be7f4',
                'team': 'T02BUF77V29',
                'text': 'message1',
                'ts': '1661501713.317699',
                'type': 'message',
                'user': 'U02C3MSRRM2'}]
        self.rps.create_channel_storage("team_id", "channel_id_4")
        self.rps.create_message_storage("team_id", "channel_id_4", data)
        message_list = self.rps.get_all_message_storages("team_id", "channel_id_4")
        files = os.listdir(f'./storage/team_id/')
        self.assertEqual(len(files), 4)
        self.assertEqual(len(message_list), 1)
    
    def test_delete_message_storage(self):
        self.rps.delete_message_storage("team_id", "channel_id_4")
        files = os.listdir(f'./storage/team_id/')
        self.assertEqual(len(files), 3)
    
    def test_search_message_in_storage_all_message(self):
        data = self.rps.search_message_in_storage("team_id", "channel_id_1", users=[], str="", ts_before="", ts_after="")
        self.assertEqual(len(data), 7)
    
    def test_search_message_in_storage_by_user(self):
        data = self.rps.search_message_in_storage("team_id", "channel_id_1", users=["U02C3MSRRM2"], str="", ts_before="", ts_after="")
        self.assertEqual(len(data), 6)
    
    def test_search_message_in_storage_range_time(self):
        data = self.rps.search_message_in_storage("team_id", "channel_id_1", users=["U02C3MSRRM2"], str="", ts_before=1661501338, ts_after=1661502092)
        self.assertEqual(len(data), 4)
    
    def test_create_message_block_and_text(self):
        data = self.rps.search_message_in_storage("team_id", "channel_id_1", users=["U02C3MSRRM2"], str="", ts_before=1661501338, ts_after=1661502092)
        users_info = {"U02C3MSRRM2" : {"name": "user", "icon": "icon"}}
        message = self.rps.create_message_block_and_text(data[0], users_info)
        self.assertEqual(message['text'], "message1")
        self.assertEqual(len(message['blocks']), 4)

    
    # def test_delete_message_storage(self)::1661501337:1661502092
