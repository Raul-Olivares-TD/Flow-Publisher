import hou # type: ignore
import os
import requests


class DiscordConnections:
    CHANNEL_ID = os.environ["DISCORD_CHANNEL"]
    USER_ID = os.environ["DISCORD_USER"]
    
    def __init__(self):
        token = os.environ["DISCORD_TOKEN_BOT"]

        self.headers = {
            "Authorization" : token
        }

    def flipbok_notifier(self, message):
        """Creates the flipbook upload notification for send it at discord.
        
        :param message: Message content for send at the notify.
        """
            
        endpoint = f"https://discordapp.com/api/channels/{self.CHANNEL_ID}/messages"


        payload = {
            "content" : message
        }

        try:
            # POST request
            response = requests.post(endpoint,json=payload, headers=self.headers)
            response.raise_for_status()
            
        except requests.RequestException as e:
            print(f"Error sending message to Discord: {e}")
    
    def notify_message_houdini(self, project, task):        
        """Message and data get from houdini to creates the content of notify.
        
        :param project: Name of the project work on at Houdini.
        :param task: Name of the task work on at Houdini.
        """
        
        message = (f"**{self.USER_ID}** uploaded a new flipbook version to "
            f"review of the task `{task}` from the project `{project}`") 
        
        return message
    
    def notify_asset_message(self, file_name):
        """Message and data get from houdini to creates the content of notify.
        
        :param asset_name: Name of the asset.
        :param version: The version of the asset.
        """
        
        message = (f"**{self.USER_ID}** uploaded a new asset version to "
            f"review`{file_name}`") 
        
        return message        
        
        