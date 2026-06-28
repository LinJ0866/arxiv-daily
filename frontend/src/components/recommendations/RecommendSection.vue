<template>
  <section class="recommend-section">
    <div class="section-header">
      <h2 class="section-title">
        <span class="icon">⭐</span>
        猜你喜欢
      </h2>
      <span class="count">共 {{ totalCount }} 篇</span>
    </div>

    <div v-if="loading && recommendations.length === 0" class="loading">
      <div class="spinner"></div>
    </div>

    <div v-else-if="recommendations.length > 0">
      <ArticleCard
        v-for="(rec, index) in recommendations"
        :key="rec.article_id"
        :article="rec"
        :index="(currentPage - 1) * pageSize + index + 1"
        :search-query="searchQuery"
        @show-detail="$emit('show-detail', $event)"
        @like-changed="onLikeChanged($event)"
      />

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="pagination">
        <button
          class="page-btn"
          :disabled="currentPage <= 1"
          @click="goToPage(currentPage - 1)"
        >
          上一页
        </button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button
          class="page-btn"
          :disabled="currentPage >= totalPages"
          @click="goToPage(currentPage + 1)"
        >
          下一页
        </button>
      </div>
    </div>

    <div v-else class="empty">
      <p>暂无推荐</p>
      <p class="hint">喜欢一些文章后，系统会为你生成个性化推荐</p>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { recommendationApi } from '@/api'
import ArticleCard from '@/components/articles/ArticleCard.vue'

const props = defineProps({
  dateFilter: {
    type: String,
    default: null
  },
  searchQuery: {
    type: String,
    default: ''
  }
})

const authStore = useAuthStore()

defineEmits(['show-detail'])

const allRecommendations = ref([])  // 所有推荐
const recommendations = ref([])     // 当前页的推荐
const loading = ref(false)

// 分页状态
const currentPage = ref(1)
const pageSize = ref(50)
const totalCount = ref(0)

// 总页数
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

async function waitForAuth() {
  if (authStore.initialized) return
  return new Promise(resolve => {
    const check = setInterval(() => {
      if (authStore.initialized) {
        clearInterval(check)
        resolve()
      }
    }, 50)
  })
}

async function fetchRecommendations() {
  await waitForAuth()
  if (!authStore.isAuthenticated) return

  loading.value = true
  try {
    // 获取所有推荐（不分页，因为推荐数量通常不会太多）
    const { data } = await recommendationApi.getList(props.dateFilter, 200)
    // API 已返回 id 字段，直接使用
    allRecommendations.value = data.recommendations || []
    totalCount.value = allRecommendations.value.length
    // 应用分页
    applyPagination()
  } catch (error) {
    console.error('Failed to fetch recommendations:', error)
  } finally {
    loading.value = false
  }
}

// 翻页（客户端分页）
function goToPage(page) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  // 重新应用分页
  applyPagination()
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 应用分页
function applyPagination() {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  recommendations.value = allRecommendations.value.slice(start, end)
}

// 处理喜欢状态变化（内部更新）
function onLikeChanged({ id, liked }) {
  // 更新 allRecommendations
  const allIndex = allRecommendations.value.findIndex(r => r.article_id === id)
  if (allIndex !== -1) {
    allRecommendations.value[allIndex] = { ...allRecommendations.value[allIndex], is_liked: liked }
  }
  // 更新当前页的 recommendations
  const pageIndex = recommendations.value.findIndex(r => r.article_id === id)
  if (pageIndex !== -1) {
    recommendations.value[pageIndex] = { ...recommendations.value[pageIndex], is_liked: liked }
  }
}

// 监听日期变化
watch(() => props.dateFilter, () => {
  currentPage.value = 1
  fetchRecommendations()
})

onMounted(fetchRecommendations)
</script>

<style scoped>
.recommend-section {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color);
}

.icon {
  font-size: 20px;
}

.count {
  font-size: 14px;
  color: var(--text-tertiary);
}

.empty {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.empty p {
  margin-bottom: 8px;
}

.hint {
  font-size: 14px;
  color: var(--text-tertiary);
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

/* 分页 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-white);
  color: var(--text-color);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: var(--text-secondary);
}
</style>
