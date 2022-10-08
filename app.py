from concurrent.futures import thread
from email import message
from http import client
from itertools import chain
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
from views.app_home_view import AppHomeView
from views.modal_view import ModalView

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
json_open = open(f'env.json', 'r')
result = json.load(json_open)
SLACK_BOT_TOKEN = result["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = result["SLACK_APP_TOKEN"]
app = App(token=SLACK_BOT_TOKEN)

# 'hello' を含むメッセージをリッスンします
# 指定可能なリスナーのメソッド引数の一覧は以下のモジュールドキュメントを参考にしてください：
# https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
@app.event("app_home_opened")
def update_home_tab(client, body, event, logger):
    try:
    # views.publish is the method that your app uses to push a view to the Home tab
        ch_rps = ChannelsRepository()
        msg_rps = MessagesRepository()
        usr_act = UserAnctions()
        # pprint.pprint(body)
        team_id = body["team_id"]
        storage_bool = ch_rps.get_storage_bool(team_id)
        if storage_bool == False:
            ch_rps.create_team_storage(team_id)
        channel_list = ch_rps.get_channels_info(client, team_id)
        messages_info_list = msg_rps.get_messasges_info_list(team_id, channel_list)
        view_cls = AppHomeView()
        view = view_cls.init_app_home_view(storage_bool, messages_info_list, channel_list)
        client.views_publish(
            # the user that opened your app's app home
            user_id=event["user"],
            # the view object that appears in the app home
            view=view
        )
        # 自分に向けてDMで知らせる
        # client.chat_postMessage(channel="U01TNJL4PQ9", text="ホームが開かれました")
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")
        # client.chat_postMessage(channel="U01TNJL4PQ9", text=f"Error publishing home tab: {e}")


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
        client.chat_postMessage(channel="U01TNJL4PQ9", text=f"Error publishing home tab: {e}")

@app.action("search_message")
def handle_search_message_action(ack, body, logger, client):
    try : 
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
            
        view_cls = ModalView()
        view = view_cls.init_search_message_modal_view(options)
        client.views_open(
            trigger_id=body["trigger_id"],
            view=view
        )
    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))
        client.chat_postMessage(channel="U01TNJL4PQ9", text=f"Error publishing home tab: {e}")

@app.view("view_search_message")
def hundle_view_search_message_action(ack, body, logger, client):
    try :
        ack()
        logger.info(body)
        selected_user_list = body["view"]["state"]["values"]["user_input"]["input_user"]["selected_users"]
        date_before = body["view"]["state"]["values"]["date_before_input"]["input_date_before"]["selected_date"]
        date_after = body["view"]["state"]["values"]["date_after_input"]["input_date_after"]["selected_date"]
        channel = body["view"]["state"]["values"]["channel_input"]["input_channel"]["selected_option"]["value"]

        team_id = body["team"]["id"]

        user = body["user"]["id"]

        # pprint.pprint(body)

        ts_date_before = datetime.datetime.strptime(date_before, '%Y-%m-%d').timestamp()
        ts_date_after = datetime.datetime.strptime(date_after, '%Y-%m-%d').timestamp()
        messag_rps = MessagesRepository()
        user_actions = UserAnctions()

        messages_result = messag_rps.search_message_in_storage(team_id, channel, selected_user_list,  ts_date_before, ts_date_after)

        users_info = user_actions.get_users_icon_and_name(client, selected_user_list)

        block_list = []

        view_cls = AppHomeView()

        for result in messages_result:
            blocks_and_text = view_cls.create_message_block_view(result, users_info)
            block_list.extend(blocks_and_text["blocks"])
            for reply in blocks_and_text["thread"]:
                blocks_and_text = view_cls.create_message_block_view(reply, users_info)
                block_list.extend(blocks_and_text["blocks"])
        ch_rps = ChannelsRepository()
        msg_rps = MessagesRepository()
        storage_bool = ch_rps.get_storage_bool(team_id)
        channel_list = ch_rps.get_channels_info(client, team_id)
        messages_info_list = msg_rps.get_messasges_info_list(team_id, channel_list)
        view_cls = AppHomeView()
        view = view_cls.init_app_home_view(storage_bool, messages_info_list, channel_list, block_list)
        client.views_publish(
                user_id=user,
                view=view
        )
    except SlackApiError as e:
        pprint.pprint("Error creating conversation: {}".format(e))
        client.chat_postMessage(channel="U01TNJL4PQ9", text=f"Error publishing home tab: {e}")



@app.action("create_storage_action")
def create_storage_action(ack, body, logger, client):
    ack()
    try :
        ch_rps = ChannelsRepository()
        team_id = body["team"]["id"]
        storage_result = ch_rps.create_team_storage(team_id)
    except SlackApiError as e:
        pprint.pprint("Error creating conversation: {}".format(e))
        client.chat_postMessage(channel="U01TNJL4PQ9", text=f"Error publishing home tab: {e}")

@app.action("register_storage_action")
def register_storage_action(ack, body, logger, client):
    try : 
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
        view_cls = ModalView()
        view = view_cls.init_register_storage_modal_view(options)

        if not options:
            msg = "登録するチャンネルがありません。"
            client.chat_postMessage(channel=user, text=msg)
        else :
            client.views_open(
            # 受け取りから 3 秒以内に有効な trigger_id を渡す
            trigger_id=body["trigger_id"],
            # ビューのペイロード
            view=view
        )
    except SlackApiError as e:
        pprint.pprint("Error creating conversation: {}".format(e))
        client.chat_postMessage(channel="U01TNJL4PQ9", text=f"Error publishing home tab: {e}")

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
        client.chat_postMessage(channel="U01TNJL4PQ9", text=f"Error publishing home tab: {e}")

@app.action("delete_storage_action")
def delete_storage_action(ack, body, logger, client):
    try :
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
        
        view_cls = ModalView()
        view = view_cls.init_delete_storage_modal_view(options)
        if not options:
            msg = "削除するチャンネルがありません。"
            client.chat_postMessage(channel=user, text=msg)
        else :
            client.views_open(
            # 受け取りから 3 秒以内に有効な trigger_id を渡す
            trigger_id=body["trigger_id"],
            # ビューのペイロード
            view=view
        )
    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))
        client.chat_postMessage(channel="U01TNJL4PQ9", text=f"Error publishing home tab: {e}")


@app.view("view_delete")
def handle_view_delete_events(ack, body, logger, client):
    ack()
    logger.info(body)
    user = body["user"]["id"]
    try :
        messages_rps = MessagesRepository()
        channel_id = body["view"]["state"]["values"]["input_delete"]["delete_input"]["selected_option"]["value"]
        name = body["view"]["state"]["values"]["input_delete"]["delete_input"]["selected_option"]["text"]["text"]
        team_id = body["team"]["id"]
        messages_rps.delete_message_storage(team_id, channel_id)

    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))
        client.chat_postMessage(channel="U01TNJL4PQ9", text=f"Error publishing home tab: {e}")

@app.action("send_message_action")
def handle_send_message_action(ack, body, logger, client):
    try :
        ack()
        ts = body["actions"][0]["value"]
        msg_rps = MessagesRepository()
        ch_rps = ChannelsRepository()
        team_id = body["team"]["id"]
        user = body["user"]["id"]
        channel_list = ch_rps.get_channels(team_id)
        data = msg_rps.get_message_by_ts(team_id, channel_list, ts)
        blocks_and_text = msg_rps.create_message_block_and_text(data)
        result = client.chat_postMessage(
                channel=user,
                blocks=blocks_and_text["blocks"],
                text=blocks_and_text["text"],
                unfurl_links=True,
                unfurl_media=True
            )
    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))
        # client.chat_postMessage(channel="U01TNJL4PQ9", 

@app.action("data_download")
def handle_data_download_action(ack, body, logger, client):
    try :
        ack()
        user = body["user"]["id"]
        team_id = body["team"]["id"]
        ch_rps = ChannelsRepository()
        pprint.pprint(body)
        channel_id = body["actions"][0]["value"]
        channel_name = ch_rps.get_channel_name_by_id(client, channel_id)
        client.chat_postMessage(channel=user, text="OK")
        msg_rps = MessagesRepository()
        usr_act = UserAnctions()
        users_list = usr_act.get_user_info_for_message(client)
        message_data = msg_rps.message_data_for_export_file(team_id, channel_id)
        arrange_message_data = msg_rps.arrange_message_data(message_data, users_list)
        export_file = msg_rps.create_export_file(team_id, channel_id, channel_name, arrange_message_data)
        new_file = client.files_upload(channels=user, title="メッセージファイル",file=f"./storage/{team_id}/{channel_id}/{channel_name}.json" )
    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))
        client.chat_postMessage(channel=user, text=f"Error publishing home tab: {e}")

# アプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
