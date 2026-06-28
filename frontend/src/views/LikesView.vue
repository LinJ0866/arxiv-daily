<template>
  <div class="likes-view container">
    <h1 class="page-title">我的喜欢</h1>

    <div class="toolbar">
      <span class="likes-count">共 {{ likedCount }} 篇喜欢的论文</span>
      <label class="btn btn-secondary btn-sm import-btn">
        📥 导入 Zotero
        <input type="file" accept=".rdf" @change="importZotero" hidden />
      </label>
    </div>

    <!-- 导入状态 -->
    <div v-if="importing" class="import-status">
      <div class="spinner-sm"></div>
      <span>正在导入...</span>
    </div>
    <div v-if="importResult" class="import-result" :class="importResult.success ? 'success' : 'error'">
      {{ importResult.message }}
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>

    <div v-else-if="likes.length > 0">
      <div class="likes-list">
        <ArticleCard
          v-for="like in likes"
          :key="like.id"
          :article="like"
          @show-detail="showDetail"
          @like-changed="handleLikeChanged"
        />
      </div>
    </div>

    <div v-else class="empty">
      <p>暂无喜欢的论文</p>
      <p class="hint">在首页点击 ❤️ 按钮收藏你喜欢的论文</p>
      <router-link to="/" class="btn btn-primary">去首页看看</router-link>
    </div>

    <!-- 文章详情模态框 -->
    <ArticleDetail
      v-if="selectedArticle"
      :article="selectedArticle"
      @close="selectedArticle = null"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { likeApi, zoteroApi } from '@/api'
import ArticleCard from '@/components/articles/ArticleCard.vue'
import ArticleDetail from '@/components/articles/ArticleDetail.vue'

const likes = ref([])
const loading = ref(false)
const selectedArticle = ref(null)
const importing = ref(false)
const importResult = ref(null)

// 实时计算喜欢数量
const likedCount = computed(() => {
  return likes.value.filter(item => item.is_liked).length
})

// 导入 Zotero RDF
async function importZotero(event) {
  const file = event.target.files[0]
  if (!file) return

  importing.value = true
  importResult.value = null

  try {
    const { data } = await zoteroApi.import(file)
    importResult.value = {
      success: true,
      message: `✅ 导入成功！共 ${data.total} 篇文章，新增 ${data.new_articles} 篇，已标记喜欢 ${data.liked} 篇`
    }
    // 刷新列表
    await fetchLikes()
  } catch (error) {
    importResult.value = {
      success: false,
      message: `❌ 导入失败：${error.response?.data?.detail || error.message}`
    }
  } finally {
    importing.value = false
    // 清空文件输入
    event.target.value = ''
  }
}

async function fetchLikes() {
  loading.value = true
  try {
    const { data } = await likeApi.getList()
    // API 已返回完整文章信息，直接使用
    likes.value = (data.likes || []).map(like => ({
      ...like,
      is_liked: true
    }))
  } catch (error) {
    console.error('Failed to fetch likes:', error)
  } finally {
    loading.value = false
  }
}

// 处理喜欢状态变化
function handleLikeChanged({ id, liked }) {
  const index = likes.value.findIndex(a => a.id === id)
  if (index !== -1) {
    likes.value[index] = { ...likes.value[index], is_liked: liked }
  }
  // 更新详情页
  if (selectedArticle.value && selectedArticle.value.id === id) {
    selectedArticle.value = { ...selectedArticle.value, is_liked: liked }
  }
}

function showDetail(article) {
  selectedArticle.value = article
}

onMounted(fetchLikes)
</script>

<style scoped>
.likes-view {
  padding-top: 20px;
  padding-bottom: 40px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-color);
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.likes-count {
  font-size: 14px;
  color: var(--text-secondary);
}

.import-btn {
  cursor: pointer;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.import-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--bg-color);
  border-radius: var(--radius-sm);
  margin-bottom: 16px;
  font-size: 14px;
  color: var(--text-secondary);
}

.import-result {
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  margin-bottom: 16px;
  font-size: 14px;
}

.import-result.success {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  color: #52c41a;
}

.import-result.error {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: #ff4d4f;
}

.spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.likes-list {
  display: grid;
  gap: 16px;
}

.empty {
  text-align: center;
  padding: 60px 20px;
  background: var(--bg-white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.empty p {
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.hint {
  font-size: 14px;
  color: var(--text-tertiary);
  margin-bottom: 20px;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 60px;
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
</style>
