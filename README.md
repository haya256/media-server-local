# Media Server (Local)

主に家庭内での利用を想定した、他の機器（スマホなど）のブラウザからローカルネットワーク内の動画 (MP4) や音声 (MP3 / M4A) を視聴するための nginx HTTPS サーバー。音声ファイルは同名の SRT 字幕とセットで、字幕を表示しながら再生できる。

## セットアップ

### 1. 自己署名証明書の生成 (PowerShell)

`192.168.x.x` を実際の PC の IP アドレスに変更してから実行:

```powershell
$IP = "192.168.x.x"
docker run --rm -v "${PWD}/certs:/certs" alpine sh -c `
  "apk add --no-cache openssl && openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /certs/server.key -out /certs/server.crt -subj '/CN=$IP' -addext 'subjectAltName=IP:$IP'"
```

### 2. メディアファイルの配置

`videos/` フォルダに MP4 / MP3 / M4A ファイルをコピーする。

音声に字幕を付ける場合は、**拡張子以外が同じ名前**の SRT ファイルを同じ場所に置く:

```
videos/
  講義01.mp3
  講義01.srt   ← 自動でペアとして認識される
```

### 3. サーバーの起動

```powershell
docker compose up -d
```

### 4. Windows ファイアウォールの設定 (管理者 PowerShell)

```powershell
New-NetFirewallRule -DisplayName "Media Server HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
```

### 5. スマホなどからのアクセス

ブラウザで `https://192.168.x.x` にアクセスする。

**証明書警告の回避方法:**
- 「詳細」→「192.168.x.x にアクセスする（安全でない）」をタップ
- または、デバイスの設定から CA 証明書をインストールする

## 音声+字幕の再生

同名の SRT ファイルが置かれた音声を選択すると、再生画面に字幕が表示される:

- 現在のキューを中央に大きく表示し、前後1つのキューを上下にフェード気味に表示
- 前後のキューをクリック（タップ）すると、その位置にシークできる
- 再生位置の保存・復元、再生終了時の「視聴済」フォルダへの移動は動画と同様に動作し、移動時は字幕ファイルも一緒に移動される

SRT は UTF-8 を想定。BOM 付き、連番の欠落、`<i>` などの装飾タグ、タイムスタンプのカンマ/ピリオド表記のいずれにも対応している。

## ファイル構成

```
project/
  docker-compose.yml
  nginx.conf
  html/
    index.html     ← メディア一覧・再生 UI (字幕表示含む)
  api/
    server.py      ← 視聴進捗の保存・視聴済みフォルダへの移動 API
  certs/           ← 自己署名証明書 (gitignore 済み)
  videos/          ← MP4 / MP3 / M4A / SRT ファイル置き場 (gitignore 済み)
```

## 停止

```powershell
docker compose down
```

## トラブルシューティング

### Docker 再起動後に nginx が起動しない

Docker Desktop や OS を再起動した後、nginx コンテナが `Exited (127)` になる場合がある。これはコンテナが古くなったことによるもので、コンテナを作り直すことで解決する:

```bash
docker compose down
docker compose up -d
```

### 自動起動の設定 (Linux / WSL2)

systemd が使える環境では、OS 起動時に `docker compose up -d` を自動実行するサービスを登録することで安定した自動起動が実現できる。

`/etc/systemd/system/media-server-local.service` を以下の内容で作成:

```ini
[Unit]
Description=Media Server Local (docker compose)
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
User=YOUR_USERNAME
WorkingDirectory=/path/to/media-server-local
ExecStartPre=/bin/bash -c 'until /usr/bin/docker info > /dev/null 2>&1; do sleep 2; done'
ExecStart=/usr/bin/docker compose up -d --remove-orphans
ExecStop=/usr/bin/docker compose down

[Install]
WantedBy=multi-user.target
```

`YOUR_USERNAME` と `WorkingDirectory` のパスを環境に合わせて変更してから:

```bash
sudo systemctl daemon-reload
sudo systemctl enable media-server-local.service
sudo systemctl start media-server-local.service
```
