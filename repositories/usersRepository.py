import json
import os
from unittest import result

class ChannelsRepository():
    def __init__(self) -> None:
        pass

    def create_user_storage(self,name):
        new_dir_pass_1 = f"./storage/users"
        os.mkdir(new_dir_pass_1)
        new_dir_pass_2 = f"./storage/users/{name}"
        os.mkdir(new_dir_pass_2)
        msg = {"message": "ストレージを作成しました"}
        return msg

    def create_user_storage(self, name, user, data):
        msg = {}
        with open(f'./storage/users/{name}/{user}.json', "w") as f:
            json.dump(data, f)
        return msg
    
    def get_user_storages(self, name, user):
        json_open = open(f'./storage/users/{name}/{user}.json', 'r')
        result = json.load(json_open)
        json_open.close()
        return result