<template>
  <div class="authorize-page">
    <el-container>
      <el-main>
        <div class="authorize-container">
          <el-card class="authorize-card" shadow="always">
            <div class="logo-section">
              <el-icon :size="60" color="#409EFF">
                <Lock />
              </el-icon>
            </div>

            <h1>QQ 账号登录验证</h1>

            <template v-if="!expired && !authorized">
              <p class="instructions">请在 QQ 群聊或私聊中发送以下命令完成登录：</p>

              <div class="command-box">
                <el-tag size="large" type="info">{{ loginCommand }} {{ loginCode }}</el-tag>
              </div>

              <div class="code-display">
                <div class="code-box">{{ loginCode }}</div>
              </div>

              <div class="countdown-section">
                <el-progress
                  :percentage="countdownPercentage"
                  :color="countdownColor"
                  :stroke-width="10"
                />
                <p class="expire-text">
                  验证码将在 <strong>{{ remainingSeconds }}</strong> 秒后过期
                </p>
              </div>

              <div class="waiting-status">
                <el-icon class="is-loading" :size="24" color="#409EFF">
                  <Loading />
                </el-icon>
                <span>等待验证中...</span>
              </div>
            </template>

            <template v-else-if="expired">
              <el-result icon="error" title="验证码已过期">
                <template #sub-title>
                  <p>验证码已过期，请刷新页面重新获取</p>
                </template>
                <template #extra>
                  <el-button type="primary" @click="refreshPage">刷新页面</el-button>
                </template>
              </el-result>
            </template>

            <template v-else-if="authorized">
              <el-result icon="success" title="授权成功">
                <template #sub-title>
                  <p>正在跳转...</p>
                </template>
              </el-result>
            </template>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { Lock, Loading } from '@element-plus/icons-vue'
import { apiService } from '../api'
import { ElMessage } from 'element-plus'

const route = useRoute()

// Get login code from URL or generate from authorize flow
const loginCode = ref('')
const loginCommand = ref('/login')
const expireSeconds = ref(180)
const remainingSeconds = ref(180)
const expired = ref(false)
const authorized = ref(false)

let countdownInterval = null
let checkInterval = null

// Computed properties
const countdownPercentage = computed(() => {
  return (remainingSeconds.value / expireSeconds.value) * 100
})

const countdownColor = computed(() => {
  const percentage = countdownPercentage.value
  if (percentage > 50) return '#67C23A'
  if (percentage > 25) return '#E6A23C'
  return '#F56C6C'
})

// Functions
const startCountdown = () => {
  countdownInterval = setInterval(() => {
    remainingSeconds.value--
    if (remainingSeconds.value <= 0) {
      clearInterval(countdownInterval)
      showExpired()
    }
  }, 1000)
}

const showExpired = () => {
  expired.value = true
  if (checkInterval) {
    clearInterval(checkInterval)
  }
}

const checkAuthStatus = async () => {
  if (expired.value || !loginCode.value) return

  try {
    const data = await apiService.checkAuthStatus(loginCode.value)
    
    if (data.authorized) {
      authorized.value = true
      clearInterval(checkInterval)
      clearInterval(countdownInterval)
      
      // Redirect to the callback URL
      if (data.redirect_url) {
        setTimeout(() => {
          window.location.href = data.redirect_url
        }, 1000)
      }
    } else if (data.status === 'expired') {
      showExpired()
    }
  } catch (err) {
    console.error('检查状态失败:', err)
  }
}

const startPolling = () => {
  checkInterval = setInterval(checkAuthStatus, 2000)
}

const refreshPage = () => {
  window.location.reload()
}

const initializeAuth = async () => {
  // Check if this is coming from OAuth authorize endpoint
  // In real scenario, the backend would handle the authorize flow
  // and this page would receive the login_code
  
  // For now, we'll redirect to the actual backend authorize endpoint
  // which will show its own HTML page
  const params = route.query
  if (params.client_id) {
    // Build the authorize URL and redirect
    const authorizeUrl = apiService.buildAuthorizeUrl(params)
    window.location.href = authorizeUrl
  } else {
    // If no params, show error
    ElMessage.error('缺少必要的授权参数')
  }
}

onMounted(() => {
  // Check if we have the necessary query parameters
  const params = route.query
  
  if (params.client_id) {
    // This means we need to redirect to the actual backend authorize endpoint
    initializeAuth()
  } else {
    // This shouldn't happen in normal flow, but handle gracefully
    ElMessage.warning('请通过正确的授权流程访问此页面')
  }
})

onUnmounted(() => {
  if (countdownInterval) clearInterval(countdownInterval)
  if (checkInterval) clearInterval(checkInterval)
})
</script>

<style scoped>
.authorize-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.authorize-container {
  max-width: 550px;
  width: 100%;
}

.authorize-card {
  border-radius: 16px;
  text-align: center;
  padding: 40px 20px;
}

.logo-section {
  margin-bottom: 20px;
}

h1 {
  color: #333;
  margin-bottom: 20px;
  font-size: 28px;
}

.instructions {
  color: #666;
  line-height: 1.8;
  margin-bottom: 20px;
}

.command-box {
  margin: 20px 0;
}

.code-display {
  margin: 30px 0;
}

.code-box {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 48px;
  font-weight: bold;
  letter-spacing: 12px;
  padding: 30px;
  border-radius: 12px;
  font-family: 'Courier New', monospace;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.countdown-section {
  margin: 30px 0;
}

.expire-text {
  color: #666;
  margin-top: 15px;
  font-size: 14px;
}

.expire-text strong {
  color: #409EFF;
  font-size: 18px;
}

.waiting-status {
  margin-top: 30px;
  padding: 20px;
  background: #ecf5ff;
  border-radius: 8px;
  color: #409EFF;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  h1 {
    font-size: 24px;
  }

  .code-box {
    font-size: 36px;
    letter-spacing: 8px;
    padding: 20px;
  }
}
</style>
