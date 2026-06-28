<template>
  <div class="article-card card" :class="{ 'matched-paper': isMatched }" @click="$emit('show-detail', article)">
    <!-- 序号 -->
    <div v-if="index" class="article-index">{{ index }}</div>
    <div class="article-main">
      <div class="card-header">
        <div class="card-main">
          <h3 class="title" v-html="highlightedTitle"></h3>
          <div class="authors" v-html="highlightedAuthors"></div>
          <div class="categories">
            <span v-for="cat in article.categories" :key="cat" class="tag tag-primary">
              {{ cat }}
            </span>
          </div>
        </div>
        <LikeButton
          :article-id="article.id"
          :model-value="article.is_liked"
          @update:model-value="$emit('like-changed', { id: article.id, liked: $event })"
        />
      </div>

      <div class="card-body">
        <p v-if="article.ai?.tldr" class="tldr">
          <span class="tldr-label">TL;DR:</span>
          <span v-html="highlightedTldr"></span>
        </p>
        <p v-else class="summary" v-html="highlightedSummary"></p>
      </div>

      <div class="card-footer">
        <span class="date">{{ formatDate(article.crawled_at) }}</span>
        <div class="actions">
          <a :href="article.abs_url" target="_blank" rel="noopener" class="action-link" @click.stop>
            arXiv
          </a>
          <a v-if="article.pdf_url" :href="article.pdf_url" target="_blank" rel="noopener" class="action-link" @click.stop>
            PDF
          </a>
        </div>
      </div>

      <!-- 匹配标记 -->
      <div v-if="isMatched" class="match-badge" :title="matchReason"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import LikeButton from '@/components/common/LikeButton.vue'

const props = defineProps({
  article: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    default: null
  },
  searchQuery: {
    type: String,
    default: ''
  }
})

defineEmits(['show-detail', 'like-changed'])

// 检查是否匹配搜索
const isMatched = computed(() => {
  if (!props.searchQuery?.trim()) return false
  const q = props.searchQuery.toLowerCase()
  const hay = [
    props.article.title || '',
    (props.article.authors || []).join(' '),
    props.article.summary || '',
    (props.article.categories || []).join(' '),
    props.article.ai?.tldr || '',
    props.article.ai?.motivation || '',
    props.article.ai?.method || '',
    props.article.ai?.result || '',
    props.article.ai?.conclusion || ''
  ].join(' ').toLowerCase()
  return hay.includes(q)
})

// 匹配原因
const matchReason = computed(() => {
  if (!isMatched.value) return ''
  return `匹配: ${props.searchQuery}`
})

// 高亮文本
function highlightText(text, query) {
  if (!query?.trim() || !text) return text
  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex = new RegExp(`(${escaped})`, 'gi')
  return text.replace(regex, '<mark class="highlight-match">$1</mark>')
}

// 高亮标题
const highlightedTitle = computed(() => {
  return highlightText(props.article.title, props.searchQuery)
})

// 高亮作者
const highlightedAuthors = computed(() => {
  const authors = props.article.authors || []
  if (authors.length === 0) return 'Unknown authors'
  const display = authors.length <= 4
    ? authors.join(', ')
    : `${authors.slice(0, 2).join(', ')}, ..., ${authors.slice(-2).join(', ')}`
  return highlightText(display, props.searchQuery)
})

// 高亮 TL;DR
const highlightedTldr = computed(() => {
  return highlightText(props.article.ai?.tldr, props.searchQuery)
})

// 高亮摘要
const highlightedSummary = computed(() => {
  const summary = props.article.summary || ''
  const truncated = summary.length <= 200 ? summary : summary.substring(0, 200) + '...'
  return highlightText(truncated, props.searchQuery)
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}
</script>

<style scoped>
.article-card {
  cursor: pointer;
  margin-bottom: 16px;
  position: relative;
  display: flex;
  gap: 16px;
}

.article-card.matched-paper {
  border-left: 3px solid var(--primary-color);
  background: rgba(102, 126, 234, 0.02);
}

.article-index {
  font-weight: 600;
  color: white;
  background: var(--gradient-primary);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
  margin-top: 4px;
}

.match-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 8px;
  height: 8px;
  background: var(--primary-color);
  border-radius: 50%;
}

.article-main {
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.card-main {
  flex: 1;
  min-width: 0;
}

.title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 8px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.authors {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.categories {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.card-body {
  margin-top: 12px;
}

.tldr {
  font-size: 14px;
  color: var(--text-color);
  line-height: 1.6;
}

.tldr-label {
  font-weight: 600;
  color: var(--primary-color);
}

.summary {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.date {
  font-size: 12px;
  color: var(--text-tertiary);
}

.actions {
  display: flex;
  gap: 12px;
}

.action-link {
  font-size: 12px;
  color: var(--primary-color);
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.action-link:hover {
  background: rgba(102, 126, 234, 0.1);
  text-decoration: none;
}

/* 高亮样式 */
:deep(.highlight-match) {
  background: rgba(255, 214, 0, 0.3);
  padding: 1px 2px;
  border-radius: 2px;
}

:deep(.author-highlight) {
  color: var(--primary-color);
  font-weight: 500;
}
</style>
