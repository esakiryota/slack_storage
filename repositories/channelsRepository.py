import json
import os
from unittest import result

class ChannelsRepository():
    def __init__(self) -> None:
        pass

    def create_storage_directory(self, name, channel):
        if os.path.exists(f"./storage/{name}") == False:
            self.create_team_storage(name)
        if os.path.exists(f"./storage/{name}/{channel}") == False:
            self.create_channel_storage(name, channel)
        
        msg = {"message": "ストレージを作成しました"}
        return msg


    def create_team_storage(self, name):
        new_dir_pass = f"./storage/{name}"
        os.mkdir(new_dir_pass)
        msg = {"message": "ストレージを作成しました"}
        return msg

    def create_channel_storage(self,name, channel):
        new_dir_pass = f"./storage/{name}/{channel}"
        os.mkdir(new_dir_pass)
        msg = {"message": "ストレージを作成しました"}
        return msg
    
    def get_channels(self, name):
        files = os.listdir(f'./storage/{name}/')
        return files

    def get_channels_info(self, client, name):
        channel_storage_list = self.get_channels(name)
        result = []
        channel_list = client.conversations_list()
        channel_list = channel_list["channels"]
        for channel in channel_list:
            if channel["id"] in channel_storage_list:
                channel_info = {"name": channel["name"], "id": channel["id"]}
                result.append(channel_info)
        
        return result

    def get_storage_bool(self, team_id):
        storages = os.listdir(f'./storage/')
        if team_id in storages:
            return True
        else:
            return False

                    
    