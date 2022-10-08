import os
import json
import pprint
import sys
import datetime

class AppHomeView():

    def __init__(self) -> None:
        pass

    def init_app_home_view(self, storage_bool=False, messages_info_list=[], channel_list=[], message_list=[]):
        storage_manage_blocks = [{"type": "header","text": {"type": "plain_text","text": "ストレージの管理"}}]
        if storage_bool == False:
            storage_manage_blocks.append({
			"type": "actions",
			"elements": [
				{
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "ストレージの作成"
                                },
                                "value": "create",
                                "action_id": "create_storage_action"
                            }
			]
		})
        else :
            storage_manage_blocks.append({
			"type": "actions",
			"elements": [
				{
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "ストレージの登録"
                                },
                                "value": "register",
                                "action_id": "register_storage_action"
                            }
			]
		})
        divider = {
            "type": "divider"
        }

        storage_manage_blocks.append(divider)

        message_search_block = self.message_search_view(channel_list)

        view = {
            "type": "home",
            "callback_id": "home_view",

            # body of the view
            "blocks": []
        }

        message_info_blocks = self.storage_infomation_view(messages_info_list)

        search_condition_block = self.search_condition_view()
        view["blocks"].extend(message_search_block)
        if message_list != []:
            view["blocks"].extend(message_list)
        view["blocks"].extend(storage_manage_blocks)
        view["blocks"].extend(message_info_blocks)
        # view["blocks"].extend(search_condition_block)
        return view

    def storage_infomation_view(self, message_infomation_list):
        blocks = [
        ]
        for message_info in message_infomation_list:
            block = [{
                "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*#{message_info['name']}*\nメッセージ数: {message_info['message_num']}\n日付範囲: {message_info['oldest']}〜{message_info['latest']}\nファイル数: {message_info['file_num']}"
                        }
                        },
            {
			"type": "actions",
			"elements": [

				{

					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Download",
						"emoji": True
					},
					"style": "primary",
					"value": f"{message_info['id']}",
                    "action_id": "data_download"
				},
				# {
				# 	"type": "button",
				# 	"text": {
				# 		"type": "plain_text",
				# 		"text": "削除",
				# 		"emoji": True
				# 	},
                #     "style": "danger",
				# 	"value": "details"
				# },
			]
		},
        {
			"type": "divider"
		}
        ]
            blocks.extend(block)
        
        return blocks

    def message_search_view(self, channel_list):
        options = []
        for channel in channel_list:
            option = {
                    "text": {
                        "type": "plain_text",
                 							"text": channel["name"]
                    },
                    "value": channel["id"]
                }
            options.append(option)
        message_search_block = [{
            "type": "header",
         			"text": {
                                    "type": "plain_text",
                                				"text": "メッセージ",
                                }
        }, {
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "メッセージの検索"
					},
					"value": "search_message",
					"action_id": "search_message"
				}
			]
		}, {
            "type": "divider"
        }]

        return message_search_block

    def search_condition_view(self):
        block = [
            {
                
                "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "検索条件"
                        }
            },
            {
			"type": "actions",
			"elements": [
				{
					"type": "users_select",
					"placeholder": {
						"type": "plain_text",
						"text": "Select a user",
						"emoji": True
					},
					"action_id": "actionId-2"
				},
				{
					"type": "static_select",
					"placeholder": {
						"type": "plain_text",
						"text": "Select an item",
						"emoji": True
					},
					"options": [
						{
							"text": {
								"type": "plain_text",
								"text": "*this is plain_text text*",
								"emoji": True
							},
							"value": "value-0"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "*this is plain_text text*",
								"emoji": True
							},
							"value": "value-1"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "*this is plain_text text*",
								"emoji": True
							},
							"value": "value-2"
						}
					],
					"action_id": "actionId-3"
				}
			]
		}
        ]

        return block
    
    def create_message_block_view(self, data, users_info):
        blocks = []
        text = ""
        result = {}
        file_num = 0
        if "user" in data and data["user"] in users_info:
            user_text = f"送信者: {users_info[data['user']]['name']}"
            block = {"type": "context","elements": [{"type": "plain_text","text":  user_text}]}
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
            blocks.append(block)
        if "files" in data:
            for file in data["files"]:
                file_num += 1
            block = {"type": "context","elements": [{"type": "plain_text","text": f"ファイル数: {str(file_num)}個" }]}
            blocks.append(block)
            
        ts_text = f"送信日時: {datetime.datetime.fromtimestamp(data['ts']).replace(microsecond = 0)}"
        block = {"type": "context","elements": [{"type": "plain_text","text":  ts_text}]}
        blocks.append(block)
        # action_btn_block = {
		# 	"type": "actions",
		# 	"elements": [
		# 		{
        #                         "type": "button",
        #                         "text": {
        #                             "type": "plain_text",
        #                             "text": "ダイレクトメッセージに送信"
        #                         },
        #                         "value": str(data['ts']),
        #                         "action_id": "send_message_action"
        #                     }
		# 	]
		# }
        divider = {"type": "divider"}
        # blocks.append(action_btn_block)
        blocks.append(divider)

        result["blocks"] = blocks 
        result["text"] = text
        result["thread"] = data["thread"]
        
        return result