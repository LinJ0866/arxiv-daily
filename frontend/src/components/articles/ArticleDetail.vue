<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2 class="modal-title">{{ article.title }}</h2>
        <button class="close-btn" @click="$emit('close')">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" fill="currentColor"/>
          </svg>
        </button>
      </div>

      <div class="modal-body">
        <div class="meta">
          <div class="authors">
            <span class="label">Authors:</span>
            {{ article.authors?.join(', ') || 'Unknown' }}
          </div>
          <div class="categories">
            <span class="label">Categories:</span>
            <span v-for="cat in article.categories" :key="cat" class="tag tag-primary">
              {{ cat }}
            </span>
          </div>
          <div class="date">
            <span class="label">Date:</span>
            {{ article.crawled_at }}
          </div>
        </div>

        <div class="actions">
          <LikeButton
            :article-id="article.id"
            :model-value="article.is_liked"
            @update:model-value="article.is_liked = $event"
          />
          <a v-if="article.abs_url" :href="article.abs_url" target="_blank" rel="noopener" class="btn btn-secondary">
            arXiv
          </a>
          <a v-if="article.pdf_url" :href="article.pdf_url" target="_blank" rel="noopener" class="btn btn-secondary">
            PDF
          </a>
          <a v-if="article.ai?.code_url" :href="article.ai.code_url" target="_blank" rel="noopener" class="btn btn-secondary">
            Code
            <span v-if="article.ai.code_stars" class="stars">⭐ {{ article.ai.code_stars }}</span>
          </a>
        </div>

        <div v-if="article.ai" class="ai-section">
          <div v-if="article.ai.tldr" class="section">
            <h3 class="section-title">TL;DR</h3>
            <p class="section-content">{{ article.ai.tldr }}</p>
          </div>

          <div v-if="article.ai.motivation" class="section">
            <h3 class="section-title">Motivation</h3>
            <p class="section-content">{{ article.ai.motivation }}</p>
          </div>

          <div v-if="article.ai.method" class="section">
            <h3 class="section-title">Method</h3>
            <p class="section-content">{{ article.ai.method }}</p>
          </div>

          <div v-if="article.ai.result" class="section">
            <h3 class="section-title">Result</h3>
            <p class="section-content">{{ article.ai.result }}</p>
          </div>

          <div v-if="article.ai.conclusion" class="section">
            <h3 class="section-title">Conclusion</h3>
            <p class="section-content">{{ article.ai.conclusion }}</p>
          </div>
        </div>

        <div class="section">
          <h3 class="section-title">Abstract</h3>
          <p class="section-content abstract">{{ article.summary }}</p>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="$emit('close')">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import LikeButton from '@/components/common/LikeButton.vue'

defineProps({
  article: {
    type: Object,
    required: true
  }
})

defineEmits(['close'])
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: var(--bg-white);
  border-radius: var(--radius-lg);
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 24px 24px 0;
  gap: 16px;
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color);
  line-height: 1.4;
}

.close-btn {
  background: transparent;
  color: var(--text-tertiary);
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.close-btn:hover {
  background: var(--bg-color);
  color: var(--text-color);
}

.modal-body {
  padding: 24px;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 20px;
  font-size: 14px;
  color: var(--text-secondary);
}

.label {
  font-weight: 500;
  color: var(--text-color);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

.stars {
  margin-left: 4px;
  font-size: 12px;
}

.ai-section {
  margin-bottom: 24px;
}

.section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 8px;
}

.section-content {
  font-size: 14px;
  color: var(--text-color);
  line-height: 1.8;
}

.abstract {
  color: var(--text-secondary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .modal-content {
    max-height: 95vh;
  }

  .modal-header {
    padding: 16px 16px 0;
  }

  .modal-body {
    padding: 16px;
  }

  .modal-footer {
    padding: 12px 16px;
  }
}
</style>
