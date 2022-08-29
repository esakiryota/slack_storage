from dataclasses import dataclass
import json
import os
from pprint import pprint
from unittest import result
import datetime
import shutil

class MessagesRepository():
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

    def create_message_storage(self, name, channel, data):
        msg = {}
        with open(f'./storage/{name}/{channel}/messages.json', "w") as f:
            json.dump(data, f)
            msg["message"] = "作成しました"
        return msg

    def get_all_message_storages(self, name, channel):
        json_open = open(f'./storage/{name}/{channel}/messages.json', 'r')
        result = json.load(json_open)
        json_open.close()
        return result

    def delete_message_storage(self, name, channel):
        shutil.rmtree(f'./storage/{name}/{channel}')
        msg = {"message": "削除しました"}
        return msg

    def delete_team_storage(self, name):
        shutil.rmtree(f'./storage/{name}')
        msg = {"message": "削除しました"}
        return msg

    def add_data_to_storage(self, name, channel, data):
        cur_data = self.get_all_message_storages(name, channel)
        for message in data:
            cur_data.append(message)
        result = self.create_message_storage(name, channel, cur_data)

        return result
    
    def search_message_in_storage(self, name, channel, users=[], str="", ts_before="", ts_after=""):
        messages = self.get_all_message_storages(name, channel)
        message_to_send_before = []
        for message in messages:
            message_data = {"type": "", "user": ""}
            if "type" in message:
                message_data["type"] = message["type"]
            if "user" in message:
                message_data["user"] = message["user"]
            if "blocks" in message:
                message_data["blocks"] = message["blocks"]
            if "files" in message:
                files = []
                for file in message["files"]:
                    if "permalink" in file:
                        files.append(file["permalink"])
                message_data["files"] = files
            if "ts" in message:
                message_data["ts"] = float(message["ts"])
            if "thread_ts" in message and "reply_count" not in message:
                message_data["thread_ts"] = float(message["thread_ts"])
            message_data["text"] = message["text"]
            message_data["thread"] = []
            message_to_send_before.append(message_data)

        for data_to_send in message_to_send_before:
            if "thread_ts" in data_to_send:
                i = 0
                for message in message_to_send_before:
                    if data_to_send["thread_ts"] == message["ts"]:
                        message_to_send_before[i]["thread"].append(data_to_send)
                    i += 1

        message_to_send_after = []
        for data_to_send in message_to_send_before:
            if users != []:
                if data_to_send["user"] not in users:
                    continue

            if str != "":
                if str not in data_to_send["text"]:
                    continue

            if ts_before != "" and ts_after != "":
                if data_to_send["ts"] < ts_before or data_to_send["ts"] > ts_after:
                    continue

            if "thread_ts" in data_to_send:
                continue
            message_to_send_after.append(data_to_send)
        
        return message_to_send_after
    
    def create_message_block_and_text(self, data, users_info):
        blocks = []
        text = ""
        result = {}
        if "user" in data:
            user_text = f"送信者: {users_info[data['user']]['name']}"
            block = {"type": "context","elements": [{"type": "plain_text","text":  user_text}]}
            blocks.append(block)
        if "text" in data:
            block = {
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": data["text"]
				}
			]
		}
            text += data["text"]
            blocks.append(block)
        if "files" in data:
            for file in data["files"]:
                text += ", " + file
        ts_text = f"送信日時: {datetime.datetime.fromtimestamp(data['ts']).replace(microsecond = 0)}"
        block = {"type": "context","elements": [{"type": "plain_text","text":  ts_text}]}
        blocks.append(block)
        divider = {"type": "divider"}
        blocks.append(divider)

        result["blocks"] = blocks 
        result["text"] = text
        result["thread"] = data["thread"]
        
        return result





            

    