---
name: verify
description: この repo の変更をエンドツーエンドで動作確認する手順(devcontainer には docker がない前提)
---

# media-server-local の動作検証

devcontainer(base:ubuntu24.04)には docker がないため、docker-compose は使わずスタックを直接起動して検証する。

## 前提ツール

```bash
sudo apt-get install -y nginx-core python3 npm   # 初回のみ
npm install playwright && npx playwright install --with-deps chromium  # ブラウザ検証する場合
```

## 起動手順

1. フィクスチャ用ディレクトリを作り、`/videos` と `/data` にシンボリックリンク(api/server.py がこのパスを直接参照):
   ```bash
   sudo ln -sfn <fixture>/videos /videos && sudo ln -sfn <fixture>/data /data
   chmod -R a+rX <fixture>   # nginx の www-data が読めるように。親ディレクトリの x ビットも必要
   ```
2. テスト用証明書を openssl で生成し、nginx.conf を sed で3点差し替えて起動:
   - `/etc/nginx/certs` → テスト証明書のパス
   - `http://api:8080/` → `http://127.0.0.1:8080/`
   - `/usr/share/nginx/html` → `/workspaces/media-server-local/html`
   ```bash
   sudo nginx -c <test-nginx.conf>   # 停止: sudo nginx -s stop
   ```
3. `nohup python3 api/server.py &`(ポート8080)

## 検証ポイント

- `curl -sk https://127.0.0.1/videos/` → autoindex JSON
- Playwright(`ignoreHTTPSErrors: true`)で UI を駆動。字幕キューの検証は **player を pause してから** currentTime を設定しないと再生進行で時刻がずれる
- Node から API を叩くときは `NODE_TLS_REJECT_UNAUTHORIZED=0`
- Playwright の chromium は H.264/AAC 非対応の可能性 → mp4/m4a は表示のみ確認、再生検証は mp3 で行う
- 実データ `data/videos/` は使わず、既存 mp3 をフィクスチャにコピーして使う

## 注意

- `pkill -f 'server.py'` は自分のシェルの `bash -c` コマンドラインにもマッチして自爆する。`pkill -f 'python3 api/server.py$'` などパターンに注意
- 片付け: `sudo nginx -s stop`、API プロセス kill、`sudo rm /videos /data`
