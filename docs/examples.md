# サンプルと例

このドキュメントでは、Windows 10 トースト通知機能付き MCP サーバーの使用例とサンプルコードを提供します。

## 目次

1. [基本的な使用例](#基本的な使用例)
2. [通知タイプの例](#通知タイプの例)
3. [カスタム設定の例](#カスタム設定の例)
4. [クライアント連携の例](#クライアント連携の例)
5. [スクリプト例](#スクリプト例)

## 基本的な使用例

### サーバーの起動

最も基本的な使用方法は、デフォルト設定でサーバーを起動することです：

```bash
python mcp_server.py
```

これにより、サーバーは `localhost:8000` でリッスンを開始します。

### カスタムホストとポートでの起動

特定のホストとポートでサーバーを起動するには：

```bash
python mcp_server.py --host 0.0.0.0 --port 9000
```

これにより、サーバーはすべてのネットワークインターフェース上でポート 9000 でリッスンを開始します。

### デバッグモードでの起動

詳細なログを表示するデバッグモードでサーバーを起動するには：

```bash
python mcp_server.py --debug
```

または：

```bash
python mcp_server.py --log-level debug
```

### 設定ファイルを使用した起動

設定ファイルを使用してサーバーを起動するには：

```bash
python mcp_server.py --config config.json
```

設定ファイルの例：

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 9000,
    "max_connections": 20,
    "timeout": 120
  },
  "logging": {
    "level": "info",
    "file": "server.log"
  },
  "notification": {
    "default_duration": 7,
    "default_type": "info"
  }
}
```

## 通知タイプの例

### 情報通知

情報通知を表示するための MCP コマンド：

```json
{
  "type": "command",
  "command": "show_notification",
  "params": {
    "title": "情報",
    "message": "これは情報通知です。",
    "type": "info",
    "duration": 5
  }
}
```

### 警告通知

警告通知を表示するための MCP コマンド：

```json
{
  "type": "command",
  "command": "show_notification",
  "params": {
    "title": "警告",
    "message": "これは警告通知です。",
    "type": "warning",
    "duration": 7
  }
}
```

### エラー通知

エラー通知を表示するための MCP コマンド：

```json
{
  "type": "command",
  "command": "show_notification",
  "params": {
    "title": "エラー",
    "message": "これはエラー通知です。",
    "type": "error",
    "duration": 10
  }
}
```

### 成功通知

成功通知を表示するための MCP コマンド：

```json
{
  "type": "command",
  "command": "show_notification",
  "params": {
    "title": "成功",
    "message": "これは成功通知です。",
    "type": "success",
    "duration": 5
  }
}
```

## カスタム設定の例

### Windows 固有の設定

Windows でカスタムアイコンを使用した通知：

```json
{
  "type": "command",
  "command": "show_notification",
  "params": {
    "title": "カスタムアイコン",
    "message": "これはカスタムアイコンを使用した通知です。",
    "type": "info",
    "duration": 5,
    "icon_path": "path/to/icon.ico"
  }
}
```

### macOS 固有の設定

macOS でサブタイトルと通知音を使用した通知：

```json
{
  "type": "command",
  "command": "show_notification",
  "params": {
    "title": "macOS 通知",
    "message": "これはサブタイトルと通知音を使用した通知です。",
    "type": "info",
    "duration": 5,
    "subtitle": "サブタイトル",
    "sound": true
  }
}
```

## クライアント連携の例

### Python クライアント

Python を使用して通知を送信する例：

```python
import socket
import json

def send_notification(host, port, title, message, notification_type="info", duration=5, **kwargs):
    """
    MCP サーバーに通知を送信する
    
    Args:
        host: サーバーのホスト名または IP アドレス
        port: サーバーのポート番号
        title: 通知のタイトル
        message: 通知のメッセージ
        notification_type: 通知のタイプ（"info", "warning", "error", "success"）
        duration: 通知の表示時間（秒）
        **kwargs: 追加のパラメータ（icon_path, subtitle, sound など）
        
    Returns:
        成功した場合は True、失敗した場合は False
    """
    try:
        # リクエストの作成
        params = {
            "title": title,
            "message": message,
            "type": notification_type,
            "duration": duration
        }
        
        # 追加のパラメータを追加
        params.update(kwargs)
        
        request = {
            "type": "command",
            "command": "show_notification",
            "params": params
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
    # 情報通知
    send_notification("localhost", 8000, "情報", "これは情報通知です。", "info")
    
    # 警告通知
    send_notification("localhost", 8000, "警告", "これは警告通知です。", "warning")
    
    # エラー通知
    send_notification("localhost", 8000, "エラー", "これはエラー通知です。", "error")
    
    # 成功通知
    send_notification("localhost", 8000, "成功", "これは成功通知です。", "success")
    
    # Windows 固有の設定
    send_notification("localhost", 8000, "カスタムアイコン", "これはカスタムアイコンを使用した通知です。", "info", 5, icon_path="path/to/icon.ico")
    
    # macOS 固有の設定
    send_notification("localhost", 8000, "macOS 通知", "これはサブタイトルと通知音を使用した通知です。", "info", 5, subtitle="サブタイトル", sound=True)
```

### Node.js クライアント

Node.js を使用して通知を送信する例：

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
 * @param {Object} additionalParams - 追加のパラメータ（icon_path, subtitle, sound など）
 * @returns {Promise<boolean>} - 成功した場合は true、失敗した場合は false
 */
function sendNotification(host, port, title, message, notificationType = "info", duration = 5, additionalParams = {}) {
  return new Promise((resolve, reject) => {
    try {
      // リクエストの作成
      const params = {
        title,
        message,
        type: notificationType,
        duration,
        ...additionalParams
      };
      
      const request = {
        type: "command",
        command: "show_notification",
        params
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
async function main() {
  try {
    // 情報通知
    await sendNotification("localhost", 8000, "情報", "これは情報通知です。", "info");
    
    // 警告通知
    await sendNotification("localhost", 8000, "警告", "これは警告通知です。", "warning");
    
    // エラー通知
    await sendNotification("localhost", 8000, "エラー", "これはエラー通知です。", "error");
    
    // 成功通知
    await sendNotification("localhost", 8000, "成功", "これは成功通知です。", "success");
    
    // Windows 固有の設定
    await sendNotification("localhost", 8000, "カスタムアイコン", "これはカスタムアイコンを使用した通知です。", "info", 5, { icon_path: "path/to/icon.ico" });
    
    // macOS 固有の設定
    await sendNotification("localhost", 8000, "macOS 通知", "これはサブタイトルと通知音を使用した通知です。", "info", 5, { subtitle: "サブタイトル", sound: true });
    
    console.log("All notifications sent successfully");
  } catch (err) {
    console.error(`Failed to send notifications: ${err.message}`);
  }
}

main();
```

### VSCode Cline の設定例

VSCode の `settings.json` の設定例：

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

## スクリプト例

### サーバーを起動するスクリプト（Windows）

```batch
@echo off
echo Starting MCP Server...
python mcp_server.py --host 0.0.0.0 --port 8000 --log-level info
```

### サーバーを起動するスクリプト（macOS/Linux）

```bash
#!/bin/bash
echo "Starting MCP Server..."
python mcp_server.py --host 0.0.0.0 --port 8000 --log-level info
```

### テスト通知を送信するスクリプト（Python）

```python
#!/usr/bin/env python3
"""
MCP サーバーにテスト通知を送信するスクリプト
"""

import socket
import json
import argparse
import sys

def send_notification(host, port, title, message, notification_type="info", duration=5, **kwargs):
    """
    MCP サーバーに通知を送信する
    
    Args:
        host: サーバーのホスト名または IP アドレス
        port: サーバーのポート番号
        title: 通知のタイトル
        message: 通知のメッセージ
        notification_type: 通知のタイプ（"info", "warning", "error", "success"）
        duration: 通知の表示時間（秒）
        **kwargs: 追加のパラメータ（icon_path, subtitle, sound など）
        
    Returns:
        成功した場合は True、失敗した場合は False
    """
    try:
        # リクエストの作成
        params = {
            "title": title,
            "message": message,
            "type": notification_type,
            "duration": duration
        }
        
        # 追加のパラメータを追加
        params.update(kwargs)
        
        request = {
            "type": "command",
            "command": "show_notification",
            "params": params
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

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="MCP サーバーにテスト通知を送信するスクリプト")
    parser.add_argument("--host", default="localhost", help="サーバーのホスト名または IP アドレス")
    parser.add_argument("--port", type=int, default=8000, help="サーバーのポート番号")
    parser.add_argument("--title", default="テスト通知", help="通知のタイトル")
    parser.add_argument("--message", default="これはテスト通知です。", help="通知のメッセージ")
    parser.add_argument("--type", default="info", choices=["info", "warning", "error", "success"], help="通知のタイプ")
    parser.add_argument("--duration", type=int, default=5, help="通知の表示時間（秒）")
    
    args = parser.parse_args()
    
    print(f"サーバー {args.host}:{args.port} にテスト通知を送信しています...")
    
    result = send_notification(
        host=args.host,
        port=args.port,
        title=args.title,
        message=args.message,
        notification_type=args.type,
        duration=args.duration
    )
    
    if result:
        print("通知が正常に送信されました。")
        sys.exit(0)
    else:
        print("通知の送信に失敗しました。")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

使用例：

```bash
python test_notification.py --host localhost --port 8000 --title "テスト" --message "これはテスト通知です。" --type info --duration 5
```
