# Onebot-IDP

基于 Onebot-V11、FastAPI 和 OAuth2 的 QQ 账号绑定与身份认证服务。

## ✨ 功能特性

- 🤖 **Onebot V11 协议** - 支持多种 QQ 机器人框架（go-cqhttp、Lagrange、NapCat 等）
- 🔐 **OAuth2 客户端模式** - 通过 SSO 服务器验证用户身份，完成 QQ 账号绑定
- 🆔 **OAuth2 IDP 模式** - 作为身份提供者，让第三方应用通过 QQ 验证码认证用户
- 🔗 **双向 WebSocket** - 支持 client（主动连接）和 server（等待连接）两种模式
- 💾 **持久化存储** - JSON 文件存储绑定关系，支持自定义额外字段
- 🌐 **FastAPI 后端** - 高性能异步 Web 服务
- 🎨 **Vue 3 前端** - 现代化的 Web 管理界面（新增）
- ⚙️ **高度可配置** - 命令名称、字段输出等均可自定义

## 📋 工作流程

### QQ 账号绑定流程

```
用户 ──/bind 用户名──> 机器人 ──生成链接──> 用户点击
                                              │
                                              ▼
用户 <──绑定成功通知──  机器人 <──授权成功──  SSO服务器
```

1. 用户在 QQ 中发送 `/bind 用户名`（或 `/bind` 私聊自动跳转）
2. 机器人生成唯一的绑定链接并回复用户
3. 用户点击链接，重定向到 SSO 服务器进行 OAuth2 授权
4. 授权成功后，系统验证用户名是否匹配（如指定）
5. 匹配成功则完成绑定，机器人通知用户

### IDP 登录流程（第三方应用认证）

```
第三方应用 ──重定向──> 授权页面(显示验证码)
                           │
用户 ──/login 验证码──> 机器人 ──授权成功──> 页面自动跳转
                                              │
                                              ▼
第三方应用 <──code──  回调地址 <──重定向──  授权页面
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/Murasame-Dev/Onebot-IDP.git
cd Onebot-IDP
```

### 2. 安装依赖

#### 后端依赖

```bash
# 使用 pip
pip install -r requirements.txt

# 或使用 uv（推荐）
uv sync
```

#### 前端依赖（可选，仅开发时需要）

```bash
cd frontend
npm install
```

> 💡 如果只需要运行服务，前端已预构建，无需安装前端依赖

### 3. 配置

首次运行会自动生成 `.env` 配置文件：

```bash
python main.py
```

编辑 `.env` 文件，配置必要参数。

### 4. 启动服务

```bash
python main.py
```

## ⚙️ 配置说明

### Onebot 配置

```env
# 连接模式: client(主动连接) 或 server(等待连接)
ONEBOT_MODE=client

# client 模式: Onebot 服务器 WebSocket 地址
ONEBOT_WS_URL=ws://127.0.0.1:8080

# server 模式: WebSocket 服务端监听配置
ONEBOT_WS_HOST=0.0.0.0
ONEBOT_WS_PORT=8080

# 访问令牌（如果 Onebot 实现配置了）
ONEBOT_ACCESS_TOKEN=

# WebSocket 心跳配置
ONEBOT_WS_PING_INTERVAL=20
ONEBOT_WS_PING_TIMEOUT=20
```

### FastAPI 服务配置

```env
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
BASE_URL=https://idp.example.com  # 服务公网地址
```

### OAuth2 客户端配置

```env
OAUTH2_CLIENT_ID=your_client_id
OAUTH2_CLIENT_SECRET=your_client_secret
OAUTH2_AUTHORIZE_URL=https://sso.example.com/oauth2/authorize
OAUTH2_TOKEN_URL=https://sso.example.com/oauth2/token
OAUTH2_USERINFO_URL=https://sso.example.com/oauth2/userinfo
OAUTH2_REDIRECT_URI=https://idp.example.com/callback
OAUTH2_SCOPE=openid profile email
OAUTH2_USERNAME_FIELD=preferred_username  # 用户信息中作为用户名的字段
```

### OAuth2 IDP 配置

```env
# 启用 IDP 功能
IDP_ENABLED=true

# 第三方应用凭证
IDP_CLIENT_ID=your_app_client_id
IDP_CLIENT_SECRET=your_app_client_secret

# 允许的回调地址（逗号分隔）
IDP_ALLOWED_REDIRECT_URIS=https://app1.com/callback,https://app2.com/callback

# userinfo 端点输出字段
IDP_USERINFO_OUTPUT_FIELDS=sub,preferred_username,username,uin,email,name

# 登录验证码有效期（秒）
LOGIN_CODE_EXPIRE_SECONDS=180
```

### 数据存储配置

```env
DATA_FILE=./data/bindings.json
BIND_LINK_EXPIRE_SECONDS=300

# 绑定时额外记录的用户信息字段
BIND_RECORD_FIELDS=email,email_verified,name,nickname
```

### 命令配置

```env
CMD_PREFIX=/
CMD_BIND=bind
CMD_BIND_CANCEL=bind_cancel
CMD_UNBIND=unbind
CMD_STATUS=status
CMD_LOGIN=login
```

## 📝 命令列表

| 命令 | 说明 |
|------|------|
| `/bind [用户名]` | 发起绑定请求（私聊可省略用户名） |
| `/bind_cancel` | 取消当前进行中的绑定请求 |
| `/unbind` | 解除当前绑定 |
| `/status` | 查询绑定状态 |
| `/login <验证码>` | 授权第三方应用登录（IDP 模式） |

> 💡 所有命令名称均可在配置中自定义

## 🔌 API 接口

### 绑定相关

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务状态 |
| `/bind/{bind_code}` | GET | 绑定页面入口 |
| `/callback` | GET | OAuth2 回调处理 |
| `/api/bindings` | GET | 获取所有绑定（调试用） |
| `/api/binding/{uin}` | GET | 查询特定 QQ 的绑定 |

### OAuth2 IDP 端点

| 接口 | 方法 | 说明 |
|------|------|------|
| `/oauth/authorize` | GET | 授权端点 |
| `/oauth/token` | POST | Token 端点 |
| `/oauth/userinfo` | GET | 用户信息端点 |
| `/oauth/check_status` | GET/POST | 检查授权状态（供前端轮询） |

## 🎨 Web 前端界面

项目已集成 Vue 3 前端界面，提供以下功能：

### 功能页面

- **首页** (`/`) - 服务状态展示、功能介绍、命令列表
- **绑定管理** (`/admin/bindings`) - 查看和管理所有 QQ 账号绑定
- **绑定页面** (`/bind/:code`) - QQ 账号绑定流程
- **授权页面** (`/oauth/authorize`) - OAuth2 登录验证

### 前端开发

如需修改前端代码：

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器（热重载）
npm run dev

# 构建生产版本
npm run build
```

前端开发服务器会在 `http://localhost:5173` 启动，并自动代理 API 请求到后端。

更多信息请查看 [frontend/README.md](frontend/README.md)

## 📁 项目结构

```
Onebot-IDP/
├── main.py                    # 主程序入口
├── config.py                  # 配置管理
├── core/                      # 核心模块
│   ├── server.py              # FastAPI 服务端
│   ├── onebot.py              # Onebot WebSocket 客户端/服务端
│   ├── bot.py                 # 机器人消息处理器
│   ├── oauth2_client.py       # OAuth2 客户端
│   └── storage.py             # 数据存储
├── apps/                      # 应用模块
│   ├── base/                  # 基础功能（绑定、回调等）
│   └── oauth2_server/         # OAuth2 IDP 功能
├── text/                      # 文本模块
│   ├── text.py                # 消息文本配置
│   └── config_example_generator.py  # 默认配置模板
├── frontend/                  # Vue 前端（新增）
│   ├── src/                   # 源代码
│   │   ├── views/             # 页面组件
│   │   ├── router/            # 路由配置
│   │   ├── api/               # API 服务
│   │   └── main.js            # 入口文件
│   ├── dist/                  # 构建产物
│   └── package.json           # 前端依赖
├── data/                      # 数据目录
│   └── bindings.json          # 绑定数据存储
├── requirements.txt           # 依赖列表
├── pyproject.toml             # 项目配置
└── .env                       # 环境变量配置
```

## 💾 数据存储格式

`bindings.json` 文件格式：

```json
{
  "123456789": {
    "uin": "123456789",
    "username": "example_user",
    "bound_at": 1702108800.0,
    "email": "user@example.com",
    "name": "Example User"
  }
}
```

## 🔧 第三方应用接入

### Python 示例

```python
import requests

# 1. 重定向用户到授权页面
auth_url = "https://idp.example.com/oauth/authorize"
params = {
    "client_id": "your_client_id",
    "redirect_uri": "https://your-app.com/callback",
    "response_type": "code",
    "scope": "openid profile",
    "state": "random_state"
}
# redirect user to: auth_url + "?" + urlencode(params)

# 2. 用户授权后，在回调地址获取 code，换取 token
token_response = requests.post("https://idp.example.com/oauth/token", data={
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": "https://your-app.com/callback",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret"
})
access_token = token_response.json()["access_token"]

# 3. 获取用户信息
userinfo = requests.get("https://idp.example.com/oauth/userinfo", headers={
    "Authorization": f"Bearer {access_token}"
}).json()

# 返回示例:
# {
#   "sub": "123456789",
#   "preferred_username": "example_user",
#   "username": "example_user",
#   "uin": "123456789",
#   "email": "user@example.com"
# }
```

## 🚀 部署建议

### 反向代理（Nginx）

```nginx
server {
    listen 443 ssl http2;
    server_name idp.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持（如果使用 server 模式）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Docker 部署

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### 推荐的 Onebot 实现

- [Lagrange.Core](https://github.com/KonataDev/Lagrange.Core) - 推荐
- [NapCatQQ](https://github.com/NapNeko/NapCatQQ)
- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)
- [Chronocat](https://github.com/chrononeko/chronocat)

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
