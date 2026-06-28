<template>
  <div class="settings-view container">
    <h1 class="page-title">设置</h1>

    <!-- 用户信息 -->
    <section class="settings-section card">
      <h2 class="section-title">个人信息</h2>
      <div class="form-group">
        <label class="form-label">用户名</label>
        <div class="input-row">
          <input v-model="profile.username" type="text" class="form-input" placeholder="用户名" />
          <button class="btn btn-primary btn-sm" @click="updateProfile" :disabled="savingProfile">
            {{ savingProfile ? '保存中...' : '修改' }}
          </button>
        </div>
      </div>
    </section>

    <!-- 修改密码 -->
    <section class="settings-section card">
      <h2 class="section-title">修改密码</h2>
      <div class="form-group">
        <label class="form-label">旧密码</label>
        <input v-model="passwordForm.oldPassword" type="password" class="form-input" placeholder="请输入旧密码" />
      </div>
      <div class="form-group">
        <label class="form-label">新密码</label>
        <input v-model="passwordForm.newPassword" type="password" class="form-input" placeholder="请输入新密码（至少6位）" />
      </div>
      <button class="btn btn-primary" @click="updatePassword" :disabled="savingPassword">
        {{ savingPassword ? '修改中...' : '修改密码' }}
      </button>
      <p v-if="passwordResult" class="result-msg" :class="passwordResult.success ? 'success' : 'error'">
        {{ passwordResult.message }}
      </p>
    </section>

    <!-- 偏好设置 -->
    <section class="settings-section card">
      <h2 class="section-title">偏好设置</h2>

      <div class="form-group">
        <label class="form-label">偏好关键词</label>
        <div class="tags-input">
          <div class="tags-list">
            <span v-for="(kw, index) in preferences.keywords" :key="index" class="tag">
              {{ kw }}
              <button class="tag-remove" @click="removeKeyword(index)">×</button>
            </span>
          </div>
          <div class="tag-input-row">
            <input
              v-model="newKeyword"
              type="text"
              class="form-input"
              placeholder="输入关键词，按回车添加"
              @keydown.enter.prevent="addKeyword"
            />
            <button class="btn btn-secondary" @click="addKeyword">添加</button>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">偏好作者</label>
        <div class="tags-input">
          <div class="tags-list">
            <span v-for="(author, index) in preferences.authors" :key="index" class="tag">
              {{ author }}
              <button class="tag-remove" @click="removeAuthor(index)">×</button>
            </span>
          </div>
          <div class="tag-input-row">
            <input
              v-model="newAuthor"
              type="text"
              class="form-input"
              placeholder="输入作者名，按回车添加"
              @keydown.enter.prevent="addAuthor"
            />
            <button class="btn btn-secondary" @click="addAuthor">添加</button>
          </div>
        </div>
      </div>

      <button class="btn btn-primary" @click="savePreferences" :disabled="saving">
        {{ saving ? '保存中...' : '保存偏好' }}
      </button>
    </section>

    <!-- 推荐权重设置 -->
    <section class="settings-section card">
      <h2 class="section-title">推荐权重</h2>
      <p class="section-desc">调整推荐算法中各因素的权重</p>

      <div class="weight-settings">
        <div class="weight-item">
          <label class="weight-label">
            <span>向量相似度</span>
            <span class="weight-value">{{ weights.weight_vector.toFixed(2) }}</span>
          </label>
          <input v-model.number="weights.weight_vector" type="range" min="0" max="1" step="0.1" class="weight-slider" />
        </div>

        <div class="weight-item">
          <label class="weight-label">
            <span>关键词匹配</span>
            <span class="weight-value">{{ weights.weight_keyword.toFixed(2) }}</span>
          </label>
          <input v-model.number="weights.weight_keyword" type="range" min="0" max="1" step="0.1" class="weight-slider" />
        </div>

        <div class="weight-item">
          <label class="weight-label">
            <span>作者匹配加分</span>
            <span class="weight-value">{{ weights.author_bonus.toFixed(2) }}</span>
          </label>
          <input v-model.number="weights.author_bonus" type="range" min="0" max="2" step="0.1" class="weight-slider" />
        </div>
      </div>

      <button class="btn btn-primary" @click="saveWeights" :disabled="savingWeights">
        {{ savingWeights ? '保存中...' : '保存权重' }}
      </button>
    </section>

    <!-- 推荐操作 -->
    <section class="settings-section card">
      <h2 class="section-title">推荐管理</h2>
      <p class="section-desc">手动刷新推荐列表，基于你当前的喜欢记录重新计算推荐</p>
      <button class="btn btn-primary" @click="refreshRecommendations" :disabled="refreshing">
        {{ refreshing ? '计算中...' : '🔄 刷新推荐' }}
      </button>
      <p v-if="refreshResult" class="result-msg" :class="refreshResult.success ? 'success' : 'error'">
        {{ refreshResult.message }}
      </p>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { preferenceApi, recommendationApi, userApi } from '@/api'

const authStore = useAuthStore()

// 用户信息
const profile = ref({ username: '' })
const savingProfile = ref(false)

// 密码修改
const passwordForm = ref({ oldPassword: '', newPassword: '' })
const savingPassword = ref(false)
const passwordResult = ref(null)

// 偏好设置
const preferences = ref({ keywords: [], authors: [] })
const weights = ref({ weight_vector: 0.7, weight_keyword: 0.3, author_bonus: 0.5 })
const newKeyword = ref('')
const newAuthor = ref('')
const saving = ref(false)
const savingWeights = ref(false)

// 推荐管理
const refreshing = ref(false)
const refreshResult = ref('')

// 获取用户信息
function fetchProfile() {
  if (authStore.user) {
    profile.value.username = authStore.user.username
  }
}

// 修改用户名
async function updateProfile() {
  savingProfile.value = true
  try {
    await userApi.updateProfile({ username: profile.value.username })
    await authStore.fetchUser()
    alert('用户名已修改')
  } catch (error) {
    alert(error.response?.data?.detail || '修改失败')
  } finally {
    savingProfile.value = false
  }
}

// 修改密码
async function updatePassword() {
  if (!passwordForm.value.oldPassword || !passwordForm.value.newPassword) {
    passwordResult.value = { success: false, message: '请填写完整' }
    return
  }
  savingPassword.value = true
  try {
    await userApi.updatePassword({
      old_password: passwordForm.value.oldPassword,
      new_password: passwordForm.value.newPassword
    })
    passwordResult.value = { success: true, message: '✅ 密码修改成功' }
    passwordForm.value = { oldPassword: '', newPassword: '' }
  } catch (error) {
    passwordResult.value = { success: false, message: `❌ ${error.response?.data?.detail || '修改失败'}` }
  } finally {
    savingPassword.value = false
  }
}

// 偏好设置
async function fetchPreferences() {
  try {
    const { data } = await preferenceApi.get()
    preferences.value = data
  } catch (error) {
    console.error('Failed to fetch preferences:', error)
  }
}

async function fetchWeights() {
  try {
    const { data } = await preferenceApi.getWeights()
    weights.value = data
  } catch (error) {
    console.error('Failed to fetch weights:', error)
  }
}

function addKeyword() {
  const kw = newKeyword.value.trim()
  if (kw && !preferences.value.keywords.includes(kw)) {
    preferences.value.keywords.push(kw)
    newKeyword.value = ''
  }
}

function removeKeyword(index) {
  preferences.value.keywords.splice(index, 1)
}

function addAuthor() {
  const author = newAuthor.value.trim()
  if (author && !preferences.value.authors.includes(author)) {
    preferences.value.authors.push(author)
    newAuthor.value = ''
  }
}

function removeAuthor(index) {
  preferences.value.authors.splice(index, 1)
}

async function savePreferences() {
  saving.value = true
  try {
    await preferenceApi.update(preferences.value)
    alert('偏好设置已保存')
  } catch (error) {
    alert('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

async function saveWeights() {
  savingWeights.value = true
  try {
    await preferenceApi.updateWeights(weights.value)
    alert('推荐权重已保存')
  } catch (error) {
    alert('保存失败，请重试')
  } finally {
    savingWeights.value = false
  }
}

// 推荐管理
async function refreshRecommendations() {
  refreshing.value = true
  refreshResult.value = null
  try {
    const { data } = await recommendationApi.recompute()
    refreshResult.value = { success: true, message: `✅ 成功生成 ${data.new_recommendations} 条新推荐` }
  } catch (error) {
    refreshResult.value = { success: false, message: '❌ 刷新失败，请重试' }
  } finally {
    refreshing.value = false
  }
}

onMounted(() => {
  fetchProfile()
  fetchPreferences()
  fetchWeights()
})
</script>

<style scoped>
.settings-view {
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

.settings-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 16px;
}

.section-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color);
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
}

.form-input:focus {
  border-color: var(--primary-color);
  outline: none;
}

.input-row {
  display: flex;
  gap: 8px;
}

.input-row .form-input {
  flex: 1;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 13px;
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

.tags-input {
  margin-bottom: 12px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: rgba(102, 126, 234, 0.1);
  color: var(--primary-color);
  border-radius: 20px;
  font-size: 13px;
}

.tag-remove {
  background: transparent;
  color: var(--primary-color);
  font-size: 16px;
  padding: 0 4px;
  cursor: pointer;
  opacity: 0.7;
}

.tag-remove:hover {
  opacity: 1;
}

.tag-input-row {
  display: flex;
  gap: 8px;
}

.tag-input-row .form-input {
  flex: 1;
}

.weight-settings {
  margin-bottom: 20px;
}

.weight-item {
  margin-bottom: 16px;
}

.weight-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  color: var(--text-color);
}

.weight-value {
  font-weight: 600;
  color: var(--primary-color);
}

.weight-slider {
  width: 100%;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: var(--border-color);
  border-radius: 3px;
  outline: none;
}

.weight-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  background: var(--primary-color);
  border-radius: 50%;
  cursor: pointer;
}

.weight-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  background: var(--primary-color);
  border-radius: 50%;
  cursor: pointer;
  border: none;
}

.system-info {
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
}

.info-label {
  color: var(--text-secondary);
}

.info-value {
  color: var(--text-color);
  font-weight: 500;
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

.admin-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed var(--border-color);
}
</style>
