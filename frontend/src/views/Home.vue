<template>
  <div class="home-container">
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <div class="logo-section">
            <el-icon :size="40" color="#409EFF">
              <Connection />
            </el-icon>
            <h1>Onebot-IDP</h1>
          </div>
          <el-menu mode="horizontal" :ellipsis="false" router>
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/admin/bindings">绑定管理</el-menu-item>
          </el-menu>
        </div>
      </el-header>

      <el-main class="main-content">
        <div class="hero-section">
          <el-card class="hero-card" shadow="hover">
            <div class="hero-content">
              <el-icon :size="80" color="#409EFF">
                <Lock />
              </el-icon>
              <h1 class="hero-title">QQ 账号绑定与身份认证服务</h1>
              <p class="hero-subtitle">基于 Onebot-V11、FastAPI 和 OAuth2</p>
              
              <el-divider />

              <div class="status-section">
                <el-alert
                  v-if="serviceStatus"
                  :title="'服务状态: ' + serviceStatus.status"
                  type="success"
                  :closable="false"
                  show-icon
                />
                <el-alert
                  v-else-if="error"
                  :title="'错误: ' + error"
                  type="error"
                  :closable="false"
                  show-icon
                />
                <el-skeleton v-else :rows="1" animated />
              </div>

              <div class="info-cards">
                <el-row :gutter="20">
                  <el-col :xs="24" :sm="12" :md="8">
                    <el-card shadow="hover" class="feature-card">
                      <template #header>
                        <div class="card-header">
                          <el-icon :size="30" color="#67C23A">
                            <UserFilled />
                          </el-icon>
                          <span>账号绑定</span>
                        </div>
                      </template>
                      <p>通过 QQ 机器人发送命令，快速完成账号绑定</p>
                    </el-card>
                  </el-col>
                  <el-col :xs="24" :sm="12" :md="8">
                    <el-card shadow="hover" class="feature-card">
                      <template #header>
                        <div class="card-header">
                          <el-icon :size="30" color="#E6A23C">
                            <Key />
                          </el-icon>
                          <span>OAuth2 认证</span>
                        </div>
                      </template>
                      <p>作为身份提供者，支持第三方应用接入</p>
                    </el-card>
                  </el-col>
                  <el-col :xs="24" :sm="12" :md="8">
                    <el-card shadow="hover" class="feature-card">
                      <template #header>
                        <div class="card-header">
                          <el-icon :size="30" color="#409EFF">
                            <Connection />
                          </el-icon>
                          <span>Onebot V11</span>
                        </div>
                      </template>
                      <p>支持多种 QQ 机器人框架</p>
                    </el-card>
                  </el-col>
                </el-row>
              </div>

              <el-divider />

              <div class="commands-section">
                <h3>可用命令</h3>
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="/bind [用户名]">
                    发起绑定请求（私聊可省略用户名）
                  </el-descriptions-item>
                  <el-descriptions-item label="/bind_cancel">
                    取消当前进行中的绑定请求
                  </el-descriptions-item>
                  <el-descriptions-item label="/unbind">
                    解除当前绑定
                  </el-descriptions-item>
                  <el-descriptions-item label="/status">
                    查询绑定状态
                  </el-descriptions-item>
                  <el-descriptions-item label="/login <验证码>">
                    授权第三方应用登录（IDP 模式）
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
          </el-card>
        </div>
      </el-main>

      <el-footer class="footer">
        <p>Onebot-IDP © 2024 | MIT License</p>
        <p>
          <el-link href="https://github.com/Murasame-Dev/Onebot-IDP" target="_blank" type="primary">
            <el-icon><Link /></el-icon> GitHub
          </el-link>
        </p>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiService } from '../api'
import {
  Connection,
  Lock,
  UserFilled,
  Key,
  Link
} from '@element-plus/icons-vue'

const serviceStatus = ref(null)
const error = ref(null)

const fetchStatus = async () => {
  try {
    const data = await apiService.getStatus()
    serviceStatus.value = data
  } catch (err) {
    error.value = err.message || '无法连接到服务器'
  }
}

onMounted(() => {
  fetchStatus()
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  background: white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-section h1 {
  margin: 0;
  font-size: 24px;
  color: #409EFF;
}

.main-content {
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.hero-section {
  margin-bottom: 40px;
}

.hero-card {
  border-radius: 16px;
}

.hero-content {
  text-align: center;
  padding: 20px;
}

.hero-title {
  margin: 20px 0 10px;
  font-size: 32px;
  color: #333;
}

.hero-subtitle {
  font-size: 18px;
  color: #666;
  margin-bottom: 20px;
}

.status-section {
  margin: 20px 0;
}

.info-cards {
  margin: 30px 0;
}

.feature-card {
  margin-bottom: 20px;
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: bold;
}

.commands-section {
  text-align: left;
  margin-top: 30px;
}

.commands-section h3 {
  margin-bottom: 20px;
  color: #333;
}

.footer {
  background: rgba(255, 255, 255, 0.95);
  text-align: center;
  padding: 20px;
  color: #666;
}

.footer p {
  margin: 5px 0;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 10px;
  }

  .hero-title {
    font-size: 24px;
  }

  .hero-subtitle {
    font-size: 16px;
  }
}
</style>
