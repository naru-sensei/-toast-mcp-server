# 使用方法ガイド

このドキュメントでは、Windows 10 トースト通知機能付き MCP サーバーの基本的な使用方法と機能について説明します。

## 目次

1. [インストール](#インストール)
2. [サーバーの起動](#サーバーの起動)
3. [基本的な使用方法](#基本的な使用方法)
4. [通知タイプ](#通知タイプ)
5. [コマンドリファレンス](#コマンドリファレンス)
6. [クライアント連携](#クライアント連携)

## インストール

### 前提条件

- Python 3.8 以上
- Windows 10（通知機能を使用する場合）または macOS
- pip（Python パッケージマネージャー）

### インストール手順

1. リポジトリをクローンします：

```bash
git clone https://github.com/naru-sensei/-toast-mcp-server.git
cd -toast-mcp-server
```

2. 依存関係をインストールします：

```bash
pip install -r requirements.txt
```

## サーバーの起動

サーバーを起動するには、以下のコマンドを実行します：

```bash
python mcp_server.py
```

デフォルトでは、サーバーは `localhost:8000` でリッスンします。

### 起動オプション

サーバーには以下のコマンドライン引数があります：

- `--host` または `-H`: リッスンするホスト（デフォルト: 127.0.0.1）
- `--port` または `-P`: リッスンするポート（デフォルト: 8000）
- `--log-level` または `-L`: ログレベル（デフォルト: info）
- `--config` または `-C`: 設定ファイルのパス

例：

```bash
python mcp_server.py --host 0.0.0.0 --port 9000 --log-level debug
```

## 基本的な使用方法

サーバーが起動すると、MCP クライアントからの接続を受け付けます。クライアントは MCP プロトコルを使用してサーバーと通信し、通知を表示するコマンドを送信できます。

### 通知の表示

通知を表示するには、クライアントから以下のような JSON メッセージを送信します：

```json
{
  "type": "command",
  "command": "show_notification",
  "params": {
    "title": "通知タイトル",
    "message": "通知メッセージ",
    "type": "info",
    "duration": 5
  }
}
```

### コマンド一覧の取得

利用可能なコマンドの一覧を取得するには、以下のメッセージを送信します：

```json
{
  "type": "command",
  "command": "list_commands",
  "params": {}
}
```

## 通知タイプ

サーバーは以下の通知タイプをサポートしています：

- `info`: 情報通知（デフォルト）
- `warning`: 警告通知
- `error`: エラー通知
- `success`: 成功通知

各通知タイプは、異なるアイコンと視覚的スタイルで表示されます。

## コマンドリファレンス

### show_notification

通知を表示します。

**パラメータ**:

- `title` (必須): 通知のタイトル
- `message` (必須): 通知のメッセージ内容
- `type` (オプション): 通知のタイプ（"info", "warning", "error", "success"）
- `duration` (オプション): 通知の表示時間（秒）
- `icon_path` (オプション): カスタムアイコンのパス（Windows のみ）
- `subtitle` (オプション): 通知のサブタイトル（macOS のみ）
- `sound` (オプション): 通知音を鳴らすかどうか（macOS のみ）

**レスポンス**:

```json
{
  "type": "response",
  "success": true,
  "message": "Notification displayed successfully"
}
```

### list_commands

利用可能なコマンドの一覧を取得します。

**パラメータ**: なし

**レスポンス**:

```json
{
  "type": "response",
  "success": true,
  "message": "Commands retrieved successfully",
  "data": {
    "commands": [
      {
        "name": "show_notification",
        "description": "Display a Windows 10 toast notification"
      },
      {
        "name": "list_commands",
        "description": "List available commands"
      }
    ]
  }
}
```

## クライアント連携

サーバーは以下のクライアントと連携できます：

- VSCode Cline
- カスタム MCP クライアント

クライアント固有の設定については、[クライアント設定](client_configuration.md)を参照してください。
