<template>
  <div class="bind-page">
    <el-container>
      <el-main>
        <div class="bind-container">
          <el-card class="bind-card" shadow="always">
            <template v-if="loading">
              <div class="loading-section">
                <el-icon class="is-loading" :size="60" color="#409EFF">
                  <Loading />
                </el-icon>
                <h2>正在验证绑定链接...</h2>
                <p>请稍候，即将跳转到授权页面</p>
              </div>
            </template>

            <template v-else-if="error">
              <div class="error-section">
                <el-icon :size="80" color="#F56C6C">
                  <CircleClose />
                </el-icon>
                <h2>绑定失败</h2>
                <el-alert
                  :title="error"
                  type="error"
                  :closable="false"
                  show-icon
                />
                <p class="help-text">请返回 QQ 重新发起绑定请求</p>
                <el-button type="primary" @click="goHome">返回首页</el-button>
              </div>
            </template>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Loading, CircleClose } from '@element-plus/icons-vue'
import { apiService } from '../api'

const props = defineProps({
  bindCode: {
    type: String,
    required: true
  }
})

const router = useRouter()
const loading = ref(true)
const error = ref(null)

const redirectToBind = async () => {
  try {
    // The backend will handle the redirect to OAuth2 authorize
    // We just need to navigate to the actual bind endpoint
    const bindUrl = apiService.buildBindUrl(props.bindCode)
    window.location.href = bindUrl
  } catch (err) {
    loading.value = false
    error.value = err.response?.data?.detail || '绑定链接无效或已过期，请重新发起绑定请求'
  }
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  // Automatically redirect after a short delay to show the loading state
  setTimeout(() => {
    redirectToBind()
  }, 1000)
})
</script>

<style scoped>
.bind-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.bind-container {
  max-width: 500px;
  width: 100%;
}

.bind-card {
  border-radius: 16px;
  text-align: center;
  padding: 20px;
}

.loading-section,
.error-section {
  padding: 40px 20px;
}

.loading-section h2,
.error-section h2 {
  margin: 20px 0;
  color: #333;
}

.loading-section p {
  color: #666;
  margin-bottom: 20px;
}

.error-section .el-alert {
  margin: 20px 0;
}

.help-text {
  color: #666;
  margin: 20px 0;
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
</style>
