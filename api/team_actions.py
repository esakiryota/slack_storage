import logging
import os
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class TeamAnctions():

    def __init__(self) -> None:
        pass

    def get_team_info(self, client):
        try:
            result = client.team_info()
            return result
        except SlackApiError as e:
            logger.error("Error creating conversation: {}".format(e))
