import logging
import os
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class ManageChannel():

    def __init__(self) -> None:
        self.client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
        self.logger = logging.getLogger(__name__)

    def create_channel(self, name, client):
        try:
            result = client.conversations_create(
                name=name
            )
            self.logger.info(result)
            return result


        except SlackApiError as e:
            self.logger.error("Error creating conversation: {}".format(e))
    
    def archive_channel(self, channel_id, client):
        try:
            result = client.conversations_archive(
                channel=channel_id
            )
            self.logger.info(result)
            return result


        except SlackApiError as e:
            self.logger.error("Error deleting conversation: {}".format(e))

    def rename_channel(self, channel_id, name, client):
        try:
            result = client.conversations_rename(
                channel_id=channel_id,
                name=name
            )
            self.logger.info(result)


        except SlackApiError as e:
            self.logger.error("Error deleting conversation: {}".format(e))
    
    def get_channel_list(self, client):
        try:
            result = client.conversations_list()
            self.logger.info(result)
            return result["channels"]

        except SlackApiError as e:
            self.logger.error("Error deleting conversation: {}".format(e))

