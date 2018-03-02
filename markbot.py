#!/usr/bin/env python
import os
import time
import re
import random
from slackclient import SlackClient


RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

oauth_token = "OAUTH_TOKEN_HERE"
slack_client = SlackClient(oauth_token)
starterbot_id = None
msg_count = 0

with open("insults.txt") as i:
	insults = list(i.read().splitlines())
with open("general.txt") as g:
	general = list(g.read().splitlines())


def parse_bot_commands(slack_events):
	global msg_count
	for event in slack_events:
		if event["type"] == "message" and not "subtype" in event:
			user_id, message = parse_direct_mention(event["text"])
			user = event["user"]
			msg_count +=1
			if msg_count > 23:
				periodic_post(event["channel"])
				msg_count=0
			if user_id == starterbot_id:
				handle_command(message, channel, user)
	return None, None

def parse_direct_mention(message_text):
	matches = re.search(MENTION_REGEX, message_text)
	# the first group contains the username, the second group contains the remaining message
	return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel, user):
	# Finds and executes the given command, filling in response
	response = None
	# This is where you start to implement more commands!
	if command.startswith("msg"):
		response = command[3:]
	else:
		response = "<@%s> %s" % (user, random.choice(insults).encode('ascii', 'ignore'))

	# Sends the response back to the channel
	slack_client.api_call(
		"chat.postMessage",
		channel="general",
		text=response
	)

def periodic_post(channel):
	slack_client.api_call(
		"chat.postMessage",
		channel=channel,
		text=random.choice(general).encode('ascii', 'ignore')
	)


if __name__ == "__main__":
	if slack_client.rtm_connect(with_team_state=False):
		print("MarkBot Connected")
		starterbot_id = slack_client.api_call("auth.test")["user_id"]
		
		while True:
			command, channel = parse_bot_commands(slack_client.rtm_read())
			time.sleep(RTM_READ_DELAY)
	else:
		print("Connection failed. Exception traceback printed above.")
