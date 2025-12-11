# Onebot-IDP Frontend

基于 Vue 3 + Vite + Element Plus 的现代化前端界面。

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Vue Router** - 官方路由管理器
- **Element Plus** - 基于 Vue 3 的组件库
- **Axios** - HTTP 客户端

## 功能特性

### 页面

1. **首页** (`/`)
   - 服务状态展示
   - 功能特性介绍
   - 可用命令列表

2. **绑定页面** (`/bind/:bindCode`)
   - QQ 账号绑定流程
   - 自动跳转到 OAuth2 授权

3. **授权页面** (`/oauth/authorize`)
   - OAuth2 登录验证
   - 验证码展示
   - 实时状态检查

4. **绑定管理** (`/admin/bindings`)
   - 查看所有绑定记录
   - 搜索过滤功能
   - 绑定详情查看

## 开发

### 安装依赖

```bash
npm install
```

### 开发服务器

```bash
npm run dev
```

开发服务器将在 `http://localhost:5173` 启动，并自动代理 API 请求到后端 (`http://localhost:8000`)。

### 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist` 目录。

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/
├── public/              # 静态资源
├── src/
│   ├── api/            # API 服务层
│   │   └── index.js    # API 接口定义
│   ├── components/     # 可复用组件
│   ├── router/         # 路由配置
│   │   └── index.js    # 路由定义
│   ├── views/          # 页面组件
│   │   ├── Home.vue              # 首页
│   │   ├── BindPage.vue          # 绑定页面
│   │   ├── AuthorizePage.vue     # 授权页面
│   │   └── BindingsManagement.vue # 绑定管理
│   ├── App.vue         # 根组件
│   ├── main.js         # 入口文件
│   └── style.css       # 全局样式
├── index.html          # HTML 模板
├── vite.config.js      # Vite 配置
└── package.json        # 项目配置
```

## 配置

### Vite 配置 (vite.config.js)

- **开发服务器代理**: 自动代理 `/api`, `/oauth`, `/bind`, `/callback` 到后端
- **构建输出**: `dist` 目录
- **端口**: 5173

### API 配置 (src/api/index.js)

API 基础路径配置为 `/`，在开发环境通过 Vite 代理到后端，生产环境由 FastAPI 直接提供服务。

## 部署

前端构建后的静态文件由 FastAPI 后端直接提供服务，无需单独部署。

1. 构建前端:
   ```bash
   cd frontend
   npm run build
   ```

2. 启动后端服务:
   ```bash
   cd ..
   python main.py
   ```

3. 访问服务:
   打开浏览器访问 `http://localhost:8000`

## 注意事项

- 开发时需要同时运行前端开发服务器和后端服务
- 生产环境只需运行后端服务，前端已集成
- 所有 API 路径都以 `/api` 或 `/oauth` 开头以区分前端路由
