### 開発環境の構築
```
$ python3 -m venv env
$ source .venv/bin/activate
```

### アプリケーションの起動
```
$ python3 app.py
```

### Tokenの設定
```
$ export SLACK_BOT_TOKEN=xoxb-XXX
$ export SLACK_APP_TOKEN=xapp-XXX
```

### 本番環境
システムの再起動
```
$ sudo systemctl reload supervisor
$ sudo systemctl restart supervisor
```