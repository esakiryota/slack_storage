import logging
import os
from pprint import pprint
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class UserAnctions():

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def get_user_list(self, client):
        try:
            res = client.users_list()
            result = res["members"]
            return result
        except SlackApiError as e:
            self.logger.error("Error creating conversation: {}".format(e))
    
    def get_user_icon_and_name(self, client, user):
        all_user_info = self.get_user_info_for_message(client)
        user_info = all_user_info[user]
        return user_info
    
    def get_users_icon_and_name(self, client, users):
        users_info = {}
        all_user_info = self.get_user_info_for_message(client)
        for user in users:
            users_info[user] = all_user_info[user]
        
        return users_info

    
    def get_user_info_for_message(self, client):
        user_list = self.get_user_list(client)
        user_result = {}
        for user in user_list:
            user_result[user["id"]] = {"name": user["name"], "icon": user["profile"]["image_512"]}
        
        return user_result

