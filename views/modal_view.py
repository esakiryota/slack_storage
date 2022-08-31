import os
import json


class ModalView():
    def __init__(self) -> None:
        pass

    def init_search_message_modal_view(self, options):
        modal_view = {
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

        return modal_view

    def init_register_storage_modal_view(self, options):
        modal_view = {
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

        return modal_view

    def init_delete_storage_modal_view(self, options):
        modal_view = {
        "type": "modal",
                # ビューの識別子
                "callback_id": "view_delete",
        "title": {"type": "plain_text", "text": "My App"},
        "submit": {"type": "plain_text", "text": "削除"},
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


        return modal_view
