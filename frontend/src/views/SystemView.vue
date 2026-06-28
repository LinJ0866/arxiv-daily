<template>
  <div class="system-view container">
    <h1 class="page-title">系统状态</h1>

    <!-- 定时任务状态 -->
    <section class="status-section card">
      <h2 class="section-title">定时任务</h2>
      <div class="status-grid">
        <div class="status-item">
          <span class="status-label">状态</span>
          <span class="status-value" :class="schedulerStatusClass">{{ schedulerStatus }}</span>
        </div>
        <div class="status-item">
          <span class="status-label">下次执行</span>
          <span class="status-value">{{ nextRun || '未知' }}</span>
        </div>
        <div class="status-item">
          <span class="status-label">任务数量</span>
          <span class="status-value">{{ jobCount }}</span>
        </div>
      </div>

      <!-- 仅 admin 可见的抓取按钮 -->
      <div v-if="isAdmin" class="admin-actions">
        <button class="btn btn-danger" @click="runPipeline" :disabled="runningPipeline">
          {{ runningPipeline ? '执行中...' : '🚀 立即抓取 arXiv' }}
        </button>
        <p class="action-hint">手动触发每日爬取任务（通常由定时任务自动执行）</p>
      </div>

      <p v-if="pipelineResult" class="result-msg" :class="pipelineResult.success ? 'success' : 'error'">
        {{ pipelineResult.message }}
      </p>
    </section>

    <!-- 管理员操作 -->
    <section v-if="isAdmin" class="status-section card">
      <h2 class="section-title">管理员操作</h2>
      <div class="admin-grid">
        <div class="admin-item">
          <h3>重建 Embedding</h3>
          <p>使用当前配置的模型重新计算所有文章和用户兴趣向量的 embedding</p>
          <button class="btn btn-warning" @click="rebuildEmbeddings" :disabled="rebuilding">
            {{ rebuilding ? '重建中...' : '🔄 重建 Embedding' }}
          </button>
        </div>
      </div>
      <p v-if="rebuildResult" class="result-msg" :class="rebuildResult.success ? 'success' : 'error'">
        {{ rebuildResult.message }}
      </p>
    </section>

    <!-- 任务列表 -->
    <section v-if="jobs.length > 0" class="status-section card">
      <h2 class="section-title">任务列表</h2>
      <div class="jobs-table">
        <div class="job-header">
          <span class="job-col">ID</span>
          <span class="job-col">名称</span>
          <span class="job-col">下次执行时间</span>
        </div>
        <div v-for="job in jobs" :key="job.id" class="job-row">
          <span class="job-col">{{ job.id }}</span>
          <span class="job-col">{{ job.name }}</span>
          <span class="job-col">{{ job.next_run || '未调度' }}</span>
        </div>
      </div>
    </section>

    <!-- 运行历史 -->
    <section class="status-section card">
      <h2 class="section-title">运行历史</h2>
      <div v-if="loadingHistory" class="loading">
        <div class="spinner"></div>
      </div>
      <div v-else-if="history.length > 0" class="history-list">
        <div v-for="record in history" :key="record.id" class="history-item" :class="'status-' + record.status">
          <div class="history-header">
            <div class="history-status">
              <span class="status-badge" :class="'badge-' + record.status">
                {{ statusText(record.status) }}
              </span>
              <span class="history-date">{{ record.run_date }}</span>
            </div>
            <span class="history-time">{{ formatTime(record.started_at) }}</span>
          </div>
          <div class="history-stats">
            <span class="stat">爬取: {{ record.crawled_count }}</span>
            <span class="stat">新增: {{ record.saved_count }}</span>
            <span class="stat">Embedding: {{ record.embedded_count }}</span>
            <span class="stat">推荐: {{ record.recommended_count }}</span>
          </div>
          <div v-if="record.error_message" class="history-error">
            {{ record.error_message }}
          </div>
        </div>
      </div>
      <div v-else class="empty">
        <p>暂无运行记录</p>
      </div>
    </section>

    <!-- 刷新按钮 -->
    <div class="actions">
      <button class="btn btn-secondary" @click="fetchAll" :disabled="loading">
        {{ loading ? '刷新中...' : '🔄 刷新状态' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { systemApi } from '@/api'

const authStore = useAuthStore()

const isAdmin = computed(() => authStore.user?.is_admin === true)

const loading = ref(false)
const jobs = ref([])
const history = ref([])
const loadingHistory = ref(false)
const runningPipeline = ref(false)
const pipelineResult = ref(null)
const rebuilding = ref(false)
const rebuildResult = ref(null)

const schedulerStatus = computed(() => {
  if (jobs.value.length > 0) return '运行中'
  return '未配置'
})

const schedulerStatusClass = computed(() => {
  if (jobs.value.length > 0) return 'status-active'
  return 'status-inactive'
})

const nextRun = computed(() => {
  if (jobs.value.length > 0) {
    return jobs.value[0].next_run || '未知'
  }
  return null
})

const jobCount = computed(() => jobs.value.length)

function statusText(status) {
  const map = {
    'running': '运行中',
    'success': '成功',
    'failed': '失败'
  }
  return map[status] || status
}

function formatTime(isoString) {
  if (!isoString) return ''
  const date = new Date(isoString)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

async function fetchStatus() {
  try {
    const { data } = await systemApi.getSchedulerStatus()
    jobs.value = data.jobs || []
  } catch (error) {
    console.error('Failed to fetch scheduler status:', error)
    jobs.value = []
  }
}

async function fetchHistory() {
  loadingHistory.value = true
  try {
    const { data } = await systemApi.getHistory(10)
    history.value = data.history || []
  } catch (error) {
    console.error('Failed to fetch history:', error)
    history.value = []
  } finally {
    loadingHistory.value = false
  }
}

async function fetchAll() {
  loading.value = true
  await Promise.all([fetchStatus(), fetchHistory()])
  loading.value = false
}

async function runPipeline() {
  runningPipeline.value = true
  pipelineResult.value = null
  try {
    await systemApi.runPipeline()
    pipelineResult.value = { success: true, message: '✅ Pipeline 已触发，正在后台执行' }
    // 延迟刷新历史
    setTimeout(fetchHistory, 3000)
  } catch (error) {
    pipelineResult.value = { success: false, message: `❌ 触发失败：${error.response?.data?.detail || error.message}` }
  } finally {
    runningPipeline.value = false
  }
}

async function rebuildEmbeddings() {
  rebuilding.value = true
  rebuildResult.value = null
  try {
    await systemApi.rebuildEmbeddings()
    rebuildResult.value = { success: true, message: '✅ Embedding 重建已启动，正在后台执行。这可能需要几分钟时间。' }
  } catch (error) {
    rebuildResult.value = { success: false, message: `❌ 启动失败：${error.response?.data?.detail || error.message}` }
  } finally {
    rebuilding.value = false
  }
}

onMounted(fetchAll)
</script>

<style scoped>
.system-view {
  padding-top: 20px;
  padding-bottom: 40px;
  max-width: 800px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
  color: var(--text-color);
}

.status-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 16px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.status-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.status-label {
  font-size: 12px;
  color: var(--text-tertiary);
  text-transform: uppercase;
}

.status-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
}

.status-active {
  color: #52c41a;
}

.status-inactive {
  color: var(--text-tertiary);
}

.admin-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed var(--border-color);
}

.action-hint {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.result-msg {
  margin-top: 12px;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
}

.result-msg.success {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  color: #52c41a;
}

.result-msg.error {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: #ff4d4f;
}

.jobs-table {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

.job-header {
  display: grid;
  grid-template-columns: 1fr 2fr 2fr;
  padding: 12px 16px;
  background: var(--bg-color);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.job-row {
  display: grid;
  grid-template-columns: 1fr 2fr 2fr;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
  font-size: 14px;
}

.job-row:first-child {
  border-top: none;
}

.job-col {
  display: flex;
  align-items: center;
}

/* 历史记录样式 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  padding: 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  transition: border-color 0.2s;
}

.history-item:hover {
  border-color: var(--primary-color);
}

.history-item.status-success {
  border-left: 3px solid #52c41a;
}

.history-item.status-failed {
  border-left: 3px solid #ff4d4f;
}

.history-item.status-running {
  border-left: 3px solid #1890ff;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.history-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.badge-success {
  background: #f6ffed;
  color: #52c41a;
}

.badge-failed {
  background: #fff2f0;
  color: #ff4d4f;
}

.badge-running {
  background: #e6f7ff;
  color: #1890ff;
}

.history-date {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color);
}

.history-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.history-stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-secondary);
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
}

.history-error {
  margin-top: 8px;
  padding: 8px 12px;
  background: #fff2f0;
  border-radius: 4px;
  font-size: 12px;
  color: #ff4d4f;
}

.empty {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.loading {
  display: flex;
  justify-content: center;
  padding: 40px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.actions {
  display: flex;
  justify-content: center;
}

.btn-danger {
  background: #ff4d4f;
  color: white;
}

.btn-danger:hover {
  background: #ff7875;
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-warning {
  background: #faad14;
  color: white;
}

.btn-warning:hover {
  background: #ffc53d;
}

.btn-warning:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.admin-grid {
  display: grid;
  gap: 16px;
}

.admin-item {
  padding: 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.admin-item h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-color);
}

.admin-item p {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}
</style>
