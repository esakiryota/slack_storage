from concurrent.futures import thread
from email import message
from http import client
import os
import json
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from api.channel_actions import ManageChannel
from api.team_actions import TeamAnctions
from api.user_actions import UserAnctions
from api.message_actions import MessageAction
from repositories.messagesRepository import MessagesRepository
from repositories.channelsRepository import ChannelsRepository
from slack_sdk.errors import SlackApiError
import pprint
import datetime

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# 'hello' を含むメッセージをリッスンします
# 指定可能なリスナーのメソッド引数の一覧は以下のモジュールドキュメントを参考にしてください：
# https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
    # views.publish is the method that your app uses to push a view to the Home tab
        client.views_publish(
            # the user that opened your app's app home
            user_id=event["user"],
            # the view object that appears in the app home
            view={
                "type": "home",
                "callback_id": "home_view",

                # body of the view
                "blocks": [
                    {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "説明",
			}
		},
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "このアプリでは削除、または非表示となったメッセージを保存し、管理するアプリです。フリープランでslackを使っている方や、slackのメッセージのバックアップを取っておきたい方におすすめです。\n"
                        }
                    },{
                        "type": "divider"
                    },{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "始め方",
			}
		},
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "1. ストレージを作成をクリック\n2. ストレージを登録をクリック\n3. 保存したいチャンネルを選ぶ\n"
                        }
                    },{
                        "type": "divider"
                    },{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "ストレージの管理",
			}
		},
        {
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
				},{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "ストレージの登録"
					},
					"value": "register",
					"action_id": "register_storage_action"
				},{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "ストレージの削除"
					},
					"value": "delete",
					"action_id": "delete_storage_action"
				}
			]
		},{
                        "type": "divider"
                    },{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "メッセージ",
			}
		},{
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
		},{
                        "type": "divider"
                    },{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "テストの実行"
					},
					"value": "test_action",
					"action_id": "test_action"
				}
			]
		}
    
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

@app.action('test_action')
def handle_test_action(ack, body, logger, client):
    ack()
    ch_rps = ChannelsRepository()
    team_id = body["team"]["id"]
    storage_name = "test_" + team_id
    storage_result = ch_rps.create_team_storage(storage_name)
    user = body["user"]["id"]
    ch_act = ManageChannel()
    create_channel_result = ch_act.create_channel("test_channel", client)
    test_channel_id = create_channel_result["channel"]["id"]
    client.conversations_join(channel=test_channel_id)
    result_async = client.chat_postMessage(
            channel=test_channel_id,
            text=f"message0"
    )
    msg_act = MessageAction()
    msg_rps = MessagesRepository()
    result = msg_act.get_all_message_list(client, test_channel_id, 100)
    msg_rps.create_storage_directory(storage_name, test_channel_id)
    msg_rps.create_message_storage(storage_name, test_channel_id, result)
    #test
    message_list_1 = msg_rps.get_all_message_storages(storage_name, test_channel_id)
    if (len(message_list_1) != 2):
        print("テスト失敗")
    else :
        print("テスト成功: メッセージは正しく保存されています")

    client.chat_postMessage(
            channel=user,
            text="テストが完了しました。test_channelを削除してください"
        )
    
    msg_rps.delete_message_storage(storage_name, test_channel_id)

    files = ch_rps.get_channels(storage_name)
    if (test_channel_id not in files):
        print("テスト成功: ストレージは正しく削除されています")
    else :
        print("テスト失敗")

    msg_rps.delete_team_storage(storage_name)

@app.event('message')
def hundle_message_event(ack, body, say, logger, client):
    ack()
    try:
        print("message")
        channel_id = body["event"]["channel"]
        channels_rps = ChannelsRepository()
        team_id = body["team_id"]
        channel_storage_list = channels_rps.get_channels(team_id)
        if channel_id in channel_storage_list:
            result = client.conversations_history(channel=channel_id, limit=1)
            data = result["messages"]
            thread_ts = data[0]["ts"]
            thread_result = client.conversations_replies(channel=channel_id, ts=thread_ts)
            final_data = thread_result["messages"]
            rps = MessagesRepository()
            result = rps.add_data_to_storage(team_id, channel_id, data)
    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))

@app.action("search_message")
def handle_search_message_action(ack, body, logger, client):
    ack()
    logger.info(body)
    channel_rps = ChannelsRepository()
    team_id = body["team"]["id"]
    channel_list = channel_rps.get_channels_info(client, team_id)

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
        

    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "view_search_message",
	"title": {
		"type": "plain_text",
		"text": "My App"
	},
	"submit": {
		"type": "plain_text",
		"text": "検索"
	},
	"close": {
		"type": "plain_text",
		"text": "閉じる",
	},
	"blocks": [
		{
			"type": "input",
            "block_id": "user_input",
			"element": {
				"type": "multi_users_select",
				"placeholder": {
					"type": "plain_text",
					"text": "ユーザーを選択",
				},
				"action_id": "input_user"
			},
			"label": {
				"type": "plain_text",
				"text": "ユーザー",
			}
		},
		{
			"type": "input",
            "block_id": "date_before_input",
			"element": {
				"type": "datepicker",
				"initial_date": "2022-08-22",
				"placeholder": {
					"type": "plain_text",
					"text": "日付を選択"
				},
				"action_id": "input_date_before"
			},
			"label": {
				"type": "plain_text",
				"text": "日付（前）"
			}
		},
        {
			"type": "input",
            "block_id": "date_after_input",
			"element": {
				"type": "datepicker",
				"initial_date": "2022-08-22",
				"placeholder": {
					"type": "plain_text",
					"text": "日付を選択"
				},
				"action_id": "input_date_after"
			},
			"label": {
				"type": "plain_text",
				"text": "日付（後）"
			}
		},
        {
			"type": "input",
            "block_id": "channel_input",
			"element": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "チャンネル名"
				},
				"options": options,
				"action_id": "input_channel"
			},
            "label": {
				"type": "plain_text",
				"text": "チャンネル"
			}
        }
	]
        }
    )

@app.view("view_search_message")
def hundle_view_search_message_action(ack, body, logger, client):
    ack()
    logger.info(body)
    selected_user_list = body["view"]["state"]["values"]["user_input"]["input_user"]["selected_users"]
    date_before = body["view"]["state"]["values"]["date_before_input"]["input_date_before"]["selected_date"]
    date_after = body["view"]["state"]["values"]["date_after_input"]["input_date_after"]["selected_date"]
    channel = body["view"]["state"]["values"]["channel_input"]["input_channel"]["selected_option"]["value"]

    team_id = body["team"]["id"]

    user = body["user"]["id"]

    ts_date_before = datetime.datetime.strptime(date_before, '%Y-%m-%d').timestamp()
    ts_date_after = datetime.datetime.strptime(date_after, '%Y-%m-%d').timestamp()
    messag_rps = MessagesRepository()
    user_actions = UserAnctions()

    messages_result = messag_rps.search_message_in_storage(team_id, channel, selected_user_list, key_word, ts_date_before, ts_date_after)

    users_info = user_actions.get_users_icon_and_name(client, selected_user_list)

    for result in messages_result:
        blocks_and_text = messag_rps.create_message_block_and_text(result, users_info)
        result = client.chat_postMessage(
            channel=user,
            blocks=blocks_and_text["blocks"],
            text=blocks_and_text["text"],
            unfurl_links=True,
            unfurl_media=True
        )
        ts = result["message"]["ts"]
        for reply in blocks_and_text["thread"]:
            blocks_and_text = messag_rps.create_message_block_and_text(reply, users_info)
            client.chat_postMessage(
            channel=user,
            blocks=blocks_and_text["blocks"],
            text=blocks_and_text["text"],
            thread_ts=ts,
            unfurl_links=True,
            unfurl_media=True
        )

@app.action("create_storage_action")
def create_storage_action(ack, body, logger, client):
    ack()
    try :
        ch_rps = ChannelsRepository()
        team_id = body["team"]["id"]
        storage_result = ch_rps.create_team_storage(team_id)
    except SlackApiError as e:
        pprint.pprint("Error creating conversation: {}".format(e))    


@app.action("register_storage_action")
def register_storage_action(ack, body, logger, client):
    ack()
    rps = ManageChannel()
    ch_rps = ChannelsRepository()
    team_id = body["team"]["id"]
    channel_list = ch_rps.get_channels(team_id)
    channels = rps.get_channel_list(client)
    options = []
    user = body["user"]["id"]
    for channel in channels:
        if channel["is_archived"] == False and channel["id"] not in channel_list:
            option = {
						"text": {
							"type": "plain_text",
							"text": channel["name"]
						},
						"value": channel["id"]
					}
            options.append(option)

    if not options:
        msg = "登録するチャンネルがありません。"
        client.chat_postMessage(channel=user, text=msg)
    else :
        client.views_open(
        # 受け取りから 3 秒以内に有効な trigger_id を渡す
        trigger_id=body["trigger_id"],
        # ビューのペイロード
        view={
            "type": "modal",
            # ビューの識別子
            "callback_id": "view_create",
            "title": {"type": "plain_text", "text":"My App"},
            "submit": {"type": "plain_text", "text":"登録"},
            "blocks": [
                {
			"type": "input",
            "block_id": "input_create",
			"element": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select an item"
				},
				"options": options,
				"action_id": "create_input"
			},
			"label": {
				"type": "plain_text",
				"text": "チャンネル"
			}
		}
            ]
        }
    )

@app.view("view_create")
def handle_view_create_events(ack, body, logger, client):
    ack()
    logger.info(body)
    user = body["user"]["id"]
    try :
        rps = ManageChannel()
        value = body["view"]["state"]["values"]["input_create"]["create_input"]["selected_option"]["text"]["text"]
        channel_id = body["view"]["state"]["values"]["input_create"]["create_input"]["selected_option"]["value"]
        team_id = body["team"]["id"]
        client.conversations_join(channel=channel_id)
        result_message_rps = MessagesRepository()
        message_act_rps = MessageAction()
        result = message_act_rps.get_all_message_list(client, channel_id, 100)
        result_message_rps.create_storage_directory(team_id, channel_id)
        result_message_rps.create_message_storage(team_id, channel_id, result)

    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))
        msg = f"チャンネル{name}を作成できませんでした。"
        client.chat_postMessage(channel=user, text=msg)

@app.action("delete_storage_action")
def delete_storage_action(ack, body, client):
    ack()
    rps = ManageChannel()
    ch_rps = ChannelsRepository()
    team_id = body["team"]["id"]
    channel_list = ch_rps.get_channels(team_id)
    channels = rps.get_channel_list(client)
    options = []
    user = body["user"]["id"]
    for channel in channels:
        if channel["is_archived"] == False and channel["id"] in channel_list:
            option = {
						"text": {
							"type": "plain_text",
							"text": channel["name"]
						},
						"value": channel["id"]
					}
            options.append(option)

    if not options:
        msg = "削除するチャンネルがありません。"
        client.chat_postMessage(channel=user, text=msg)
    else :
        client.views_open(
        # 受け取りから 3 秒以内に有効な trigger_id を渡す
        trigger_id=body["trigger_id"],
        # ビューのペイロード
        view={
            "type": "modal",
            # ビューの識別子
            "callback_id": "view_delete",
            "title": {"type": "plain_text", "text":"My App"},
            "submit": {"type": "plain_text", "text":"削除"},
            "blocks": [
                {
			"type": "input",
            "block_id": "input_delete",
			"element": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select an item"
				},
				"options": options,
				"action_id": "delete_input"
			},
			"label": {
				"type": "plain_text",
				"text": "Label"
			}
		}
            ]
        }
    )

@app.view("view_delete")
def handle_view_delete_events(ack, body, logger, client):
    ack()
    # hopes_and_dreams = view["state"]["values"]["input_c"]["create_input"]
    logger.info(body)
    user = body["user"]["id"]
    # client.chat_postMessage(channel=user, text=hopes_and_dreams)
    try :
        messages_rps = MessagesRepository()
        channel_id = body["view"]["state"]["values"]["input_delete"]["delete_input"]["selected_option"]["value"]
        name = body["view"]["state"]["values"]["input_delete"]["delete_input"]["selected_option"]["text"]["text"]
        team_id = body["team"]["id"]
        messages_rps.delete_message_storage(team_id, channel_id)

    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))
        msg = f"チャンネル{name}をアーカイブできませんでした。"
        client.chat_postMessage(channel=user, text=msg)

# アプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
