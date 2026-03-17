# Media Server (Local)

主に家庭内での利用を想定した、他の機器（スマホなど）のブラウザからローカルネットワーク内の MP4 動画を視聴するための nginx HTTPS サーバー。

## セットアップ

### 1. 自己署名証明書の生成 (PowerShell)

`192.168.x.x` を実際の PC の IP アドレスに変更してから実行:

```powershell
$IP = "192.168.x.x"
docker run --rm -v "${PWD}/certs:/certs" alpine sh -c `
  "apk add --no-cache openssl && openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /certs/server.key -out /certs/server.crt -subj '/CN=$IP' -addext 'subjectAltName=IP:$IP'"
```

### 2. 動画ファイルの配置

`videos/` フォルダに MP4 ファイルをコピーする。

### 3. サーバーの起動

```powershell
docker-compose up -d
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

## ファイル構成

```
project/
  docker-compose.yml
  nginx.conf
  html/
    index.html     ← 動画一覧 UI
  certs/           ← 自己署名証明書 (gitignore 済み)
  videos/          ← MP4 ファイル置き場 (gitignore 済み)
```

## 停止

```powershell
docker-compose down
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
