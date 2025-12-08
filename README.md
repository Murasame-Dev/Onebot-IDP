# Onebot-IDP

基于 Onebot-V11、FastAPI 和 OAuth2 的 QQ 账号绑定服务。

## 功能特性

- 🤖 基于 Onebot V11 协议，支持多种 QQ 机器人框架
- 🔐 标准 OAuth2 授权码流程，安全可靠
- 🔗 通过 SSO 服务器验证用户身份
- 💾 JSON 文件持久化存储绑定关系
- 🌐 FastAPI 提供 Web 服务

## 工作流程

1. 用户在 QQ 中发送 `/bind 用户名`
2. 机器人生成唯一的绑定链接并回复用户
3. 用户点击链接，重定向到 SSO 服务器进行 OAuth2 授权
4. 授权成功后，系统验证 SSO 返回的用户名是否与期望匹配
5. 匹配成功则完成绑定，并将绑定信息写入 JSON 文件

## 安装

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/Onebot-IDP.git
cd Onebot-IDP
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制示例配置文件并修改：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下参数：

```env
# Onebot 配置
ONEBOT_WS_URL=ws://127.0.0.1:8080    # Onebot WebSocket 地址
ONEBOT_ACCESS_TOKEN=                  # 访问令牌（如果有）

# FastAPI 服务配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
BASE_URL=https://idp.xxx.com          # 服务的公网地址

# OAuth2 配置
OAUTH2_CLIENT_ID=your_client_id       # OAuth2 客户端 ID
OAUTH2_CLIENT_SECRET=your_client_secret
OAUTH2_AUTHORIZE_URL=https://sso.xxx.com/oauth2/authorize
OAUTH2_TOKEN_URL=https://sso.xxx.com/oauth2/token
OAUTH2_USERINFO_URL=https://sso.xxx.com/oauth2/userinfo
OAUTH2_REDIRECT_URI=https://idp.xxx.com/callback  # 回调地址
OAUTH2_SCOPE=openid profile

# 绑定链接有效期(秒)
BIND_LINK_EXPIRE_SECONDS=300
```

### 4. 启动服务

```bash
python main.py
```

## 命令列表

| 命令 | 说明 |
|------|------|
| `/bind <用户名>` | 发起绑定请求 |
| `/unbind` | 解除当前绑定 |
| `/status` | 查询绑定状态 |

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务状态 |
| `/bind/{bind_code}` | GET | 绑定页面入口 |
| `/callback` | GET | OAuth2 回调 |
| `/api/bindings` | GET | 获取所有绑定 |
| `/api/binding/{qq_id}` | GET | 查询特定绑定 |

## 项目结构

```
Onebot-IDP/
├── main.py           # 主程序入口
├── config.py         # 配置管理
├── server.py         # FastAPI 服务端
├── bot.py            # Onebot 机器人客户端
├── oauth2_client.py  # OAuth2 客户端
├── storage.py        # 数据存储
├── requirements.txt  # 依赖列表
├── .env.example      # 环境变量示例
├── bindings.json     # 绑定数据存储
└── README.md
```

## 数据存储格式

`bindings.json` 文件格式：

```json
{
  "123456789": {
    "qq_id": "123456789",
    "username": "example_user",
    "bound_at": 1702108800.0
  }
}
```

## 部署建议

1. **反向代理**: 建议使用 Nginx 反向代理，配置 HTTPS
2. **Onebot 实现**: 推荐使用 go-cqhttp、Lagrange.Core 等
3. **SSO 服务器**: 支持标准 OAuth2 授权码流程的服务均可

### Nginx 配置示例

```nginx
server {
    listen 443 ssl;
    server_name idp.xxx.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 许可证

MIT License
基于Onebot V11的身份提供者,集成 FastAPI
