# CLAUDE.md

ローカルネットワーク向け nginx HTTPS メディアサーバー。動画 (MP4) と音声 (MP3/M4A) + 同名 SRT 字幕を、スマホ等のブラウザから視聴する。

## 構成

- `nginx.conf` — HTTPS 配信、`/videos/` の autoindex(JSON)、`/api/` プロキシ
- `html/index.html` — UI 全体(CSS/JS 内包の単一ファイル)。一覧・再生・SRT 字幕表示
- `api/server.py` — 進捗保存/復元・視聴済移動 API(Python 標準ライブラリのみ)
- 本番は WSL2 ホスト側で `docker compose up -d`(nginx + api の2コンテナ)

## 開発環境の注意

- **この devcontainer には docker がない**。動作検証は `.claude/skills/verify/SKILL.md` の手順で nginx / python3 を直接起動して行う
- `data/videos/` には実運用中のメディアファイルがある。**テストで実ファイルを変更・移動しない**(フィクスチャにコピーして使う)
- `pmo/` は非公開の開発メモ(gitignore 済み)。経緯・決定事項ログはここに追記する。秘密情報や運用の内部事情は CLAUDE.md や README に書かない

## 規約

- コマンド表記は `docker compose`(V2)。`docker-compose` は使わない
- コミットメッセージ・ドキュメント・UI は日本語
- 字幕等のユーザー由来テキストの描画は textContent を使う(innerHTML 禁止)
- nginx.conf など単体ファイルの bind mount は編集で inode が変わると Docker Desktop がエラーになることがある → `docker compose down && up -d` で解消
