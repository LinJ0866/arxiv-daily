<template>
  <div class="home-view container">
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-row">
        <!-- 日期筛选 -->
        <div class="filter-group">
          <label class="filter-label">日期</label>
          <select v-model="selectedDate" class="filter-select" @change="onDateChange">
            <option v-for="date in availableDates" :key="date" :value="date">
              {{ formatDate(date) }}
            </option>
            <option value="all">All</option>
          </select>
        </div>

        <!-- 搜索框 -->
        <div class="filter-group search-group">
          <label class="filter-label">搜索</label>
          <div class="search-input-wrapper">
            <input
              v-model="searchQuery"
              type="text"
              class="search-input"
              placeholder="搜索论文标题、摘要、作者..."
              @input="onSearch"
            />
            <button v-if="searchQuery" class="clear-btn" @click="clearSearch">✕</button>
          </div>
        </div>
      </div>

      <!-- 标签栏 -->
      <div class="tabs-row">
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'recommend' }"
          @click="activeTab = 'recommend'"
        >
          ⭐ 猜我喜欢
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'papers' }"
          @click="switchTab('papers')"
        >
          📄 论文
        </button>
        <button
          v-for="cat in categories"
          :key="cat"
          class="tab-btn"
          :class="{ active: activeTab === cat }"
          @click="switchTab(cat)"
        >
          {{ cat }}
        </button>
      </div>
    </div>

    <!-- 推荐板块 -->
    <div v-if="activeTab === 'recommend'" class="content-section">
      <RecommendSection
        :date-filter="selectedDate === 'all' ? null : selectedDate"
        :search-query="searchQuery"
        @show-detail="showDetail"
      />
    </div>

    <!-- 论文列表 -->
    <div v-else class="content-section">
      <div class="section-header">
        <h2 class="section-title">
          {{ selectedDate === 'all' ? '全部论文' : formatDate(selectedDate) + '更新论文' }}
          <span v-if="activeTab !== 'papers'" class="category-tag">{{ activeTab }}</span>
        </h2>
        <span class="count">共 {{ totalCount }} 篇</span>
      </div>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>
      </div>

      <div v-else-if="filteredArticles.length > 0">
        <ArticleCard
          v-for="(article, index) in filteredArticles"
          :key="article.id"
          :article="article"
          :index="(currentPage - 1) * pageSize + index + 1"
          :search-query="searchQuery"
          @show-detail="showDetail"
          @like-changed="handleLikeChanged"
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
        <p>暂无文章</p>
      </div>
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
import { articleApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import RecommendSection from '@/components/recommendations/RecommendSection.vue'
import ArticleCard from '@/components/articles/ArticleCard.vue'
import ArticleDetail from '@/components/articles/ArticleDetail.vue'

const authStore = useAuthStore()

// 所有文章
const articles = ref([])
// 筛选后的文章
const filteredArticles = ref([])
const loading = ref(false)
const selectedArticle = ref(null)
const selectedDate = ref('all')
const searchQuery = ref('')
const activeTab = ref('papers')
const availableDates = ref([])

// 分页状态
const currentPage = ref(1)
const pageSize = ref(100)
const totalCount = ref(0)

// 总页数
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

// 分类列表
const categories = computed(() => {
  const cats = new Set()
  articles.value.forEach(a => {
    (a.categories || []).forEach(c => cats.add(c))
  })
  return Array.from(cats).sort()
})

// 格式化日期显示（带年份）
function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr + 'T00:00:00')
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
}

// 切换分类标签
function switchTab(tab) {
  activeTab.value = tab
  currentPage.value = 1
  fetchArticles()  // 重新获取文章（后端分类筛选）
}

// 日期变化时重新获取文章
function onDateChange() {
  currentPage.value = 1
  fetchArticles()
}

// 搜索输入
function onSearch() {
  // 搜索在前端处理（排序）
  applyFilters()
}

// 清除搜索
function clearSearch() {
  searchQuery.value = ''
  applyFilters()
}

// 翻页
function goToPage(page) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchArticles()
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 应用筛选（分类 + 搜索）
function applyFilters() {
  let result = [...articles.value]

  // 按分类过滤
  if (activeTab.value !== 'papers' && activeTab.value !== 'recommend') {
    result = result.filter(a =>
      (a.categories || []).includes(activeTab.value)
    )
  }

  // 搜索过滤 + 排序（隐藏不匹配）
  const query = searchQuery.value?.trim()

  if (query) {
    const q = query.toLowerCase()

    // 先过滤掉不匹配的
    result = result.filter(a => {
      const hay = [
        a.title || '',
        (a.authors || []).join(' '),
        a.summary || '',
        (a.categories || []).join(' '),
        a.ai?.tldr || '',
        a.ai?.motivation || '',
        a.ai?.method || '',
        a.ai?.result || '',
        a.ai?.conclusion || ''
      ].join(' ').toLowerCase()

      return hay.includes(q)
    })

    // 匹配结果排序
    result.sort((a, b) => {
      const titleA = (a.title || '').toLowerCase()
      const titleB = (b.title || '').toLowerCase()

      const titleMatchA = titleA.includes(q)
      const titleMatchB = titleB.includes(q)

      // 标题命中优先
      if (titleMatchA && !titleMatchB) return -1
      if (!titleMatchA && titleMatchB) return 1

      // 标题中匹配位置靠前优先
      const indexA = titleA.indexOf(q)
      const indexB = titleB.indexOf(q)

      if (indexA !== indexB) {
        return indexA - indexB
      }

      return 0
    })
  }

  filteredArticles.value = result
}

// 处理喜欢状态变化
function handleLikeChanged({ id, liked }) {
  // 更新 articles 中的状态
  const index = articles.value.findIndex(a => a.id === id)
  if (index !== -1) {
    articles.value[index] = { ...articles.value[index], is_liked: liked }
  }

  // 更新 filteredArticles 中的状态
  const filteredIndex = filteredArticles.value.findIndex(a => a.id === id)
  if (filteredIndex !== -1) {
    filteredArticles.value[filteredIndex] = { ...filteredArticles.value[filteredIndex], is_liked: liked }
  }

  // 更新详情页
  if (selectedArticle.value && selectedArticle.value.id === id) {
    selectedArticle.value = { ...selectedArticle.value, is_liked: liked }
  }
}

// 获取可用日期列表
async function fetchAvailableDates() {
  try {
    const { data } = await articleApi.getDates()
    availableDates.value = (data.dates || []).map(d => d.date)
    // 默认选择最新日期
    if (availableDates.value.length > 0) {
      selectedDate.value = availableDates.value[0]
    }
  } catch (error) {
    console.error('Failed to fetch dates:', error)
  }
}

// 获取文章列表
async function fetchArticles() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    // 日期筛选
    if (selectedDate.value !== 'all') {
      params.date_from = selectedDate.value
      params.date_to = selectedDate.value
    }
    // 分类筛选（由后端处理）
    if (activeTab.value !== 'papers' && activeTab.value !== 'recommend') {
      params.category = activeTab.value
    }
    const { data } = await articleApi.getList(params)
    articles.value = data.articles || []
    totalCount.value = data.total || 0
    filteredArticles.value = articles.value
  } catch (error) {
    console.error('Failed to fetch articles:', error)
  } finally {
    loading.value = false
  }
}

function showDetail(article) {
  selectedArticle.value = article
}

// 如果已登录，默认显示推荐标签
onMounted(() => {
  if (authStore.isAuthenticated) {
    activeTab.value = 'recommend'
  }
  fetchAvailableDates()
  fetchArticles()
})
</script>

<style scoped>
.home-view {
  padding-top: 20px;
  padding-bottom: 40px;
}

/* 筛选栏 */
.filter-bar {
  background: var(--bg-white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  padding: 16px;
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  white-space: nowrap;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: 14px;
  color: var(--text-color);
  background: var(--bg-white);
  cursor: pointer;
  min-width: 120px;
}

.filter-select:focus {
  border-color: var(--primary-color);
  outline: none;
}

.search-group {
  flex: 1;
}

.search-input-wrapper {
  position: relative;
  flex: 1;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  padding-right: 32px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: 14px;
  color: var(--text-color);
}

.search-input:focus {
  border-color: var(--primary-color);
  outline: none;
}

.clear-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  font-size: 14px;
  padding: 4px;
}

.clear-btn:hover {
  color: var(--text-color);
}

/* 标签栏 */
.tabs-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tab-btn {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  background: var(--bg-color);
  color: var(--text-secondary);
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
}

.tab-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  color: var(--primary-color);
}

.tab-btn.active {
  background: var(--gradient-primary);
  color: white;
}

/* 内容区域 */
.content-section {
  background: var(--bg-white);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color);
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-tag {
  font-size: 12px;
  padding: 4px 8px;
  background: rgba(102, 126, 234, 0.1);
  color: var(--primary-color);
  border-radius: 12px;
}

.count {
  font-size: 14px;
  color: var(--text-tertiary);
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
  border-radius: var(--radius-sm);
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

@media (max-width: 768px) {
  .home-view {
    padding-top: 16px;
  }

  .filter-row {
    flex-direction: column;
    gap: 12px;
  }

  .filter-group {
    width: 100%;
  }

  .filter-select {
    flex: 1;
  }

  .tabs-row {
    gap: 6px;
  }

  .tab-btn {
    padding: 6px 12px;
    font-size: 12px;
  }
}
</style>
