<template>
  <div class="management-page">
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
        <el-card class="management-card">
          <template #header>
            <div class="card-header">
              <div class="title-section">
                <el-icon :size="24" color="#409EFF">
                  <User />
                </el-icon>
                <span class="title">绑定管理</span>
              </div>
              <el-button type="primary" :icon="Refresh" @click="fetchBindings" :loading="loading">
                刷新
              </el-button>
            </div>
          </template>

          <div class="search-section">
            <el-input
              v-model="searchQuery"
              placeholder="搜索 QQ号 或 用户名"
              :prefix-icon="Search"
              clearable
              @clear="fetchBindings"
            />
          </div>

          <el-divider />

          <div class="stats-section">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-statistic title="总绑定数" :value="totalBindings">
                  <template #prefix>
                    <el-icon color="#409EFF">
                      <User />
                    </el-icon>
                  </template>
                </el-statistic>
              </el-col>
              <el-col :span="8">
                <el-statistic title="显示数量" :value="filteredBindings.length">
                  <template #prefix>
                    <el-icon color="#67C23A">
                      <View />
                    </el-icon>
                  </template>
                </el-statistic>
              </el-col>
              <el-col :span="8">
                <el-statistic title="最近更新" :value="lastUpdateTime">
                  <template #prefix>
                    <el-icon color="#E6A23C">
                      <Clock />
                    </el-icon>
                  </template>
                </el-statistic>
              </el-col>
            </el-row>
          </div>

          <el-divider />

          <el-table
            v-loading="loading"
            :data="filteredBindings"
            style="width: 100%"
            stripe
            :default-sort="{ prop: 'bound_at', order: 'descending' }"
          >
            <el-table-column prop="uin" label="QQ号" width="150" sortable />
            <el-table-column prop="username" label="用户名" sortable>
              <template #default="{ row }">
                <el-tag>{{ row.username }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="bound_at" label="绑定时间" width="200" sortable>
              <template #default="{ row }">
                <el-tooltip :content="formatFullDate(row.bound_at)" placement="top">
                  <span>
                    <el-icon><Clock /></el-icon>
                    {{ formatDate(row.bound_at) }}
                  </span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  :icon="View"
                  @click="viewDetails(row)"
                >
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="!loading && filteredBindings.length === 0" description="暂无绑定记录" />
        </el-card>
      </el-main>
    </el-container>

    <!-- Detail Dialog -->
    <el-dialog
      v-model="detailDialogVisible"
      title="绑定详情"
      width="500px"
    >
      <el-descriptions v-if="selectedBinding" :column="1" border>
        <el-descriptions-item label="QQ号">
          {{ selectedBinding.uin }}
        </el-descriptions-item>
        <el-descriptions-item label="用户名">
          <el-tag>{{ selectedBinding.username }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="绑定时间">
          {{ formatFullDate(selectedBinding.bound_at) }}
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiService } from '../api'
import {
  Connection,
  User,
  Refresh,
  Search,
  View,
  Clock
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const bindings = ref({})
const searchQuery = ref('')
const detailDialogVisible = ref(false)
const selectedBinding = ref(null)
const lastUpdateTime = ref('--')

// Computed properties
const totalBindings = computed(() => {
  return Object.keys(bindings.value).length
})

const bindingsList = computed(() => {
  return Object.entries(bindings.value).map(([uin, binding]) => ({
    uin,
    ...binding
  }))
})

const filteredBindings = computed(() => {
  if (!searchQuery.value) {
    return bindingsList.value
  }
  
  const query = searchQuery.value.toLowerCase()
  return bindingsList.value.filter(binding => {
    return (
      binding.uin.includes(query) ||
      binding.username.toLowerCase().includes(query)
    )
  })
})

// Methods
const fetchBindings = async () => {
  loading.value = true
  try {
    const data = await apiService.getAllBindings()
    bindings.value = data
    lastUpdateTime.value = new Date().toLocaleTimeString('zh-CN')
    ElMessage.success('数据已更新')
  } catch (err) {
    ElMessage.error('获取绑定列表失败: ' + (err.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const viewDetails = (binding) => {
  selectedBinding.value = binding
  detailDialogVisible.value = true
}

const formatDate = (timestamp) => {
  if (!timestamp) return '--'
  const date = new Date(timestamp * 1000)
  const now = new Date()
  const diff = now - date
  
  // Less than 1 minute
  if (diff < 60000) {
    return '刚刚'
  }
  // Less than 1 hour
  if (diff < 3600000) {
    return Math.floor(diff / 60000) + ' 分钟前'
  }
  // Less than 1 day
  if (diff < 86400000) {
    return Math.floor(diff / 3600000) + ' 小时前'
  }
  // Less than 7 days
  if (diff < 604800000) {
    return Math.floor(diff / 86400000) + ' 天前'
  }
  
  return date.toLocaleDateString('zh-CN')
}

const formatFullDate = (timestamp) => {
  if (!timestamp) return '--'
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  fetchBindings()
})
</script>

<style scoped>
.management-page {
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

.management-card {
  border-radius: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.search-section {
  margin: 20px 0;
}

.stats-section {
  margin: 20px 0;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 10px;
  }

  .card-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>
