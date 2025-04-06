# クライアント設定ガイド

このドキュメントでは、Windows 10 トースト通知機能付き MCP サーバーと連携するクライアントの設定方法について説明します。

## 目次

1. [VSCode Cline の設定](#vscode-cline-の設定)
2. [カスタム MCP クライアントの開発](#カスタム-mcp-クライアントの開発)
3. [クライアント認証](#クライアント認証)
4. [クライアント固有の設定要件](#クライアント固有の設定要件)

## VSCode Cline の設定

[VSCode Cline](https://marketplace.visualstudio.com/items?itemName=vscodevim.vim) は、Visual Studio Code 用の Vim エミュレーションプラグインです。MCP プロトコルを使用して通知を送信する機能があります。

### 前提条件

- Visual Studio Code がインストールされていること
- VSCode Cline プラグインがインストールされていること

### 設定手順

1. Visual Studio Code の設定ファイル（`settings.json`）を開きます。

2. 以下の設定を追加します：

```json
{
  "vim.enableNotifications": true,
  "vim.notificationServer": {
    "host": "localhost",
    "port": 8000,
    "protocol": "mcp"
  }
}
```

3. ホストとポートを MCP サーバーの設定に合わせて調整します。

4. Visual Studio Code を再起動します。

### トラブルシューティング

- **通知が表示されない**: サーバーが実行中であることを確認し、ホストとポートの設定が正しいことを確認します。
- **接続エラー**: ファイアウォール設定を確認し、指定したポートが開放されていることを確認します。
- **プロトコルエラー**: VSCode Cline のバージョンが最新であることを確認します。

## カスタム MCP クライアントの開発

独自の MCP クライアントを開発する場合は、以下のガイドラインに従ってください。

### MCP プロトコルの実装

MCP プロトコルは JSON ベースのプロトコルで、以下の基本構造を持ちます：

1. **リクエスト**:

```json
{
  "type": "command",
  "command": "command_name",
  "params": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

2. **レスポンス**:

```json
{
  "type": "response",
  "success": true,
  "message": "Command executed successfully",
  "data": {
    "key1": "value1",
    "key2": "value2"
  }
}
```

3. **エラー**:

```json
{
  "type": "error",
  "code": "error_code",
  "message": "Error message"
}
```

### 通知コマンドの実装

通知を表示するには、以下のコマンドを送信します：

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

### クライアント接続の実装

1. サーバーに TCP 接続を確立します。
2. JSON メッセージを送信します。
3. レスポンスを受信して解析します。
4. 必要に応じてエラー処理を行います。

### サンプルコード（Python）

```python
import socket
import json

def send_notification(host, port, title, message, notification_type="info", duration=5):
    """
    MCP サーバーに通知を送信する
    
    Args:
        host: サーバーのホスト名または IP アドレス
        port: サーバーのポート番号
        title: 通知のタイトル
        message: 通知のメッセージ
        notification_type: 通知のタイプ（"info", "warning", "error", "success"）
        duration: 通知の表示時間（秒）
        
    Returns:
        成功した場合は True、失敗した場合は False
    """
    try:
        # リクエストの作成
        request = {
            "type": "command",
            "command": "show_notification",
            "params": {
                "title": title,
                "message": message,
                "type": notification_type,
                "duration": duration
            }
        }
        
        # サーバーに接続
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
            
            # リクエストの送信
            sock.sendall(json.dumps(request).encode() + b'\n')
            
            # レスポンスの受信
            response = sock.recv(4096).decode()
            
            # レスポンスの解析
            response_data = json.loads(response)
            
            # 成功したかどうかを確認
            if response_data.get("type") == "response" and response_data.get("success"):
                return True
            else:
                print(f"Error: {response_data.get('message')}")
                return False
                
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

# 使用例
if __name__ == "__main__":
    send_notification("localhost", 8000, "テスト通知", "これはテスト通知です。")
```

### サンプルコード（JavaScript）

```javascript
const net = require('net');

/**
 * MCP サーバーに通知を送信する
 * 
 * @param {string} host - サーバーのホスト名または IP アドレス
 * @param {number} port - サーバーのポート番号
 * @param {string} title - 通知のタイトル
 * @param {string} message - 通知のメッセージ
 * @param {string} notificationType - 通知のタイプ（"info", "warning", "error", "success"）
 * @param {number} duration - 通知の表示時間（秒）
 * @returns {Promise<boolean>} - 成功した場合は true、失敗した場合は false
 */
function sendNotification(host, port, title, message, notificationType = "info", duration = 5) {
  return new Promise((resolve, reject) => {
    try {
      // リクエストの作成
      const request = {
        type: "command",
        command: "show_notification",
        params: {
          title,
          message,
          type: notificationType,
          duration
        }
      };
      
      // サーバーに接続
      const client = new net.Socket();
      
      client.connect(port, host, () => {
        // リクエストの送信
        client.write(JSON.stringify(request) + '\n');
      });
      
      // レスポンスの受信
      client.on('data', (data) => {
        // レスポンスの解析
        const response = JSON.parse(data.toString());
        
        // 接続を閉じる
        client.destroy();
        
        // 成功したかどうかを確認
        if (response.type === "response" && response.success) {
          resolve(true);
        } else {
          console.error(`Error: ${response.message}`);
          resolve(false);
        }
      });
      
      // エラー処理
      client.on('error', (err) => {
        console.error(`Error: ${err.message}`);
        reject(err);
      });
      
    } catch (err) {
      console.error(`Error: ${err.message}`);
      reject(err);
    }
  });
}

// 使用例
sendNotification("localhost", 8000, "テスト通知", "これはテスト通知です。")
  .then((success) => {
    console.log(`Notification sent: ${success}`);
  })
  .catch((err) => {
    console.error(`Failed to send notification: ${err.message}`);
  });
```

## クライアント認証

現在、サーバーは基本的なクライアント認証をサポートしていません。ただし、将来のバージョンでは API キーベースの認証が実装される予定です。

### 認証の実装（将来のバージョン）

将来のバージョンでは、以下のような認証メカニズムが実装される予定です：

```json
{
  "type": "command",
  "command": "authenticate",
  "params": {
    "api_key": "your_api_key_here"
  }
}
```

## クライアント固有の設定要件

### VSCode Cline

- **プロトコルバージョン**: MCP プロトコル v1.0 以上
- **接続タイプ**: TCP
- **認証**: 不要（現在のバージョン）
- **特記事項**: Visual Studio Code の再起動が必要

### カスタム MCP クライアント

- **プロトコルバージョン**: MCP プロトコル v1.0 以上
- **接続タイプ**: TCP
- **認証**: 不要（現在のバージョン）
- **特記事項**: 
  - 各コマンドの後に改行（`\n`）を送信する必要があります
  - レスポンスは JSON 形式で返されます
  - エラー処理を適切に実装する必要があります
