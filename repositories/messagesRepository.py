from dataclasses import dataclass
import json
import os
from pprint import pprint
from unittest import result
import datetime
import shutil
from .channelsRepository import ChannelsRepository

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
    
    def search_message_in_storage(self, name, channel, users=[], ts_before="", ts_after=""):
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

            if ts_before != "" and ts_after != "":
                if data_to_send["ts"] < ts_before or data_to_send["ts"] > ts_after:
                    continue

            if "thread_ts" in data_to_send:
                continue
            message_to_send_after.append(data_to_send)
        
        return message_to_send_after
    
    def create_message_block_and_text(self, data, users_info={}):
        blocks = []
        text = ""
        result = {}
        json_file_content = {}
        json_file_content_list = []
        if "user" in data and users_info != {}:
            user_text = f"送信者: {users_info[data['user']]['name']}"
            block = {"type": "context","elements": [{"type": "plain_text","text":  user_text}]}
            json_file_content["user"] = users_info[data['user']]['name']
            blocks.append(block)
        if "text" in data:
            text = ""
            if data["text"] == "":
                text = "no text"
            else :
                text = data["text"]
            block = {
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": text
				}
			]
		}
            text += data["text"]
            json_file_content["text"] = data["text"]
            blocks.append(block)
        if "files" in data:
            for file in data["files"]:
                text += ", " + file
            json_file_content["files"] = text
        ts_text = f"送信日時: {datetime.datetime.fromtimestamp(data['ts']).replace(microsecond = 0)}"
        json_file_content["time"] = ts_text
        block = {"type": "context","elements": [{"type": "plain_text","text":  ts_text}]}
        blocks.append(block)
        divider = {"type": "divider"}
        blocks.append(divider)

        result["blocks"] = blocks 
        result["text"] = text
        result["thread"] = data["thread"]

        json_file_content_list.append()
        
        return result

    def get_messasges_info(self, name, channel, channel_name):
        messages = self.get_all_message_storages(name, channel)
        ch_rps = ChannelsRepository()
        channel_list = ch_rps.get_channels_info
        latest_ts = 0
        oldest_ts = 10000000000
        file_num = 0
        for message in messages:
            if float(message["ts"]) > latest_ts:
                latest_ts = float(message["ts"])
            if float(message["ts"]) < oldest_ts:
                oldest_ts = float(message["ts"])
            if "files" in message:
                file_num += len(message["files"])
        message_num = len(messages)
        message_info = {
                        "name": channel_name,
                        "id": channel,
                        "latest": datetime.datetime.fromtimestamp(latest_ts).replace(microsecond = 0),
                        "oldest": datetime.datetime.fromtimestamp(oldest_ts).replace(microsecond = 0), 
                        "message_num": message_num, 
                        "file_num": file_num
                        }
        return message_info

    def get_messasges_info_list(self, name, channel_list):
        messages_info_list = []
        for channel_info in channel_list:
            messages_info = self.get_messasges_info(name, channel_info["id"], channel_info["name"])
            messages_info_list.append(messages_info)
        
        return messages_info_list
    
    def get_message_by_ts(self, name, channel_list, ts):
        all_messages = []
        for channel in channel_list:
            messages = self.get_all_message_storages(name, channel)
            all_messages.extend(messages)
        message_data = {"type": "", "user": ""}
        for message in all_messages:
            if str(ts) == message["ts"]:
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
                break
        
        return message_data


    def create_export_file(self, name, channel, channel_name, data):
        msg = {}
        with open(f'./storage/{name}/{channel}/{channel_name}.json', "w") as f:
            json.dump(data, f)
            msg["message"] = "作成しました"
        return msg
    
    def message_data_for_export_file(self, name, channel):
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
                    if "url_private_download" in file:
                        files.append(file["url_private_download"])
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
        
        return message_to_send_before

    def create_message_block_for_export(self, data, users_info):
        text = ""
        data_for_export = {}
        file_num = 0
        if "user" in data and data["user"] in users_info:
            user_text = f"送信者: {users_info[data['user']]['name']}"
            data_for_export["user"] = user_text
        if "text" in data:
            text = ""
            if data["text"] == "":
                text = "no text"
            else :
                text = data["text"]
            block = {
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": text
				}
			]
		}
            text += data["text"]
        if "files" in data:
            file_link = []
            for file in data["files"]:
                file_num += 1
                file_link.append(file)
            block = {"text": f"ファイル数: {str(file_num)}個", "download_link": file_link}
            data_for_export["file_info"] = block
        data_for_export["text"] = text
        ts_text = f"送信日時: {datetime.datetime.fromtimestamp(data['ts']).replace(microsecond = 0)}"
        data_for_export["time"] = ts_text
        
        return data_for_export

    def arrange_message_data(self, message_data, user_info):
        result = []
        for data in message_data:
            block = self.create_message_block_for_export(data, user_info)
            result.append(block)

        return result





            
        







            

    