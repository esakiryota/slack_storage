import logging
import os
from pprint import pprint
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .user_actions import UserAnctions
import time

class MessageAction() :

    def __init__(self) -> None:
        self.client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
        self.logger = logging.getLogger(__name__)
    
    def post_message(self, client, channel, msg):
        try:
            result = client.chat.postMessage(
                channel=channel,
                text=msg
            )
            return result


        except SlackApiError as e:
            self.logger.error("Error creating conversation: {}".format(e))
    
    def scheduled_message(self, client, channel, post_at, msg):
        try:
            result = client.chat_scheduleMessage(
                channel=channel, 
                post_at=post_at,
                text=msg
            )
            return result


        except SlackApiError as e:
            self.logger.error("Error creating conversation: {}".format(e))
    
    def ephemeral_message(self, client, user, channel, msg):
        try:
            result = client.chat_postEphemeral(
                channel=channel,
                user=user,
                text=msg
            )
            return result


        except SlackApiError as e:
            self.logger.error("Error creating conversation: {}".format(e))
    
    def get_message_list(self, client, channel):
        try:
            result = client.conversations_history(
                channel=channel
            )
            return result


        except SlackApiError as e:
            self.logger.error("Error creating conversation: {}".format(e))

    def get_scheduled_message_list(self, client, channel):
        try:
            result = client.chat_scheduledMessages_list(
                channel=channel
            )
            return result

        except SlackApiError as e:
            self.logger.error("Error creating conversation: {}".format(e))

    
    def remove_message(self, client, channel, ts):
        try:
            result = client.conversations_create(
                channel=channel,
                ts=ts
            )
            return result


        except SlackApiError as e:
            self.logger.error("Error creating conversation: {}".format(e))
    
    def ephemeral_message_on_storage(self, client, user, channel, message_data):
        try:
            result = {}
            user_actions = UserAnctions()
            user_info_for_msg = user_actions.get_user_info_for_message(client)
            for message in message_data:
                if "type" in message:
                    if "user" in message:
                        if "blocks" in message:
                            result = client.chat_postEphemeral(
                                channel=channel,
                                user=user,
                                text=message["text"],
                                block=message["blocks"],
                                username=user_info_for_msg[message["user"]]["name"],
                                icon_user=user_info_for_msg[message["user"]]["icon"]
                            )
                        else:
                            result = client.chat_postEphemeral(
                                channel=channel,
                                user=user,
                                text=message["text"],
                                username=user_info_for_msg[message["user"]]["name"],
                                icon_user=user_info_for_msg[message["user"]]["icon"]
                            )
                    else:
                        if "blocks" in message:
                            result = client.chat_postEphemeral(
                                channel=channel,
                                user=user,
                                text=message["text"],
                                block=message["blocks"]
                            )
                        else:
                            result = client.chat_postEphemeral(
                                channel=channel,
                                user=user,
                                text=message["text"]
                            )
                else:
                    continue
            
            return result
        
        except SlackApiError as e:
            self.logger.error("Error creating conversation: {}".format(e))
    
    def get_all_message_list(self, client, channel, limit):
        try:
            result = []
            num = limit
            ts = time.time()
            while num == limit:
                messages_result = client.conversations_history(channel=channel,limit=limit, latest=ts)
                messages = messages_result["messages"]
                num = len(messages)
                result.extend(messages)
                ts = result[-1]["ts"]

            thread_result = []
            
            for message in result:
                if "thread_ts" in message:
                    thread_message_res = client.conversations_replies(channel=channel, ts=message["thread_ts"])
                    thread_message = thread_message_res["messages"]
                    del thread_message[0]
                    thread_result.extend(thread_message)

            result.extend(thread_result)

            sorted_result = sorted(result, key=lambda x: x['ts'])

            return sorted_result


        except SlackApiError as e:
            self.logger.error("Error creating conversation: {}".format(e))