<template>
  <button
    class="like-btn"
    :class="{ liked: modelValue, loading: isLoading }"
    @click.stop="toggleLike"
    :disabled="isLoading"
    :title="modelValue ? '取消喜欢' : '喜欢'"
  >
    <svg viewBox="0 0 24 24" width="20" height="20">
      <path
        v-if="modelValue"
        d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
        fill="currentColor"
      />
      <path
        v-else
        d="M16.5 3c-1.74 0-3.41.81-4.5 2.09C10.91 3.81 9.24 3 7.5 3 4.42 3 2 5.42 2 8.5c0 3.78 3.4 6.86 8.55 11.54L12 21.35l1.45-1.32C18.6 15.36 22 12.28 22 8.5 22 5.42 19.58 3 16.5 3zm-4.4 15.55l-.1.1-.1-.1C7.14 14.24 4 11.39 4 8.5 4 6.5 5.5 5 7.5 5c1.54 0 3.04.99 3.57 2.36h1.87C13.46 5.99 14.96 5 16.5 5c2 0 3.5 1.5 3.5 3.5 0 2.89-3.14 5.74-7.9 10.05z"
        fill="currentColor"
      />
    </svg>
  </button>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { likeApi } from '@/api'
import { useRouter } from 'vue-router'

const props = defineProps({
  articleId: {
    type: String,
    required: true
  },
  // 使用 v-model 双向绑定
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const authStore = useAuthStore()
const router = useRouter()
const isLoading = ref(false)

async function toggleLike() {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'Login', query: { redirect: router.currentRoute.value.fullPath } })
    return
  }

  isLoading.value = true
  try {
    if (props.modelValue) {
      await likeApi.unlike(props.articleId)
      emit('update:modelValue', false)
    } else {
      await likeApi.like(props.articleId)
      emit('update:modelValue', true)
    }
  } catch (error) {
    console.error('Like operation failed:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.like-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: transparent;
  color: var(--text-tertiary);
  transition: all 0.2s ease;
}

.like-btn:hover {
  background: rgba(255, 77, 79, 0.1);
  color: #ff4d4f;
}

.like-btn.liked {
  color: #ff4d4f;
}

.like-btn.liked:hover {
  background: rgba(255, 77, 79, 0.15);
}

.like-btn.loading {
  opacity: 0.5;
  cursor: not-allowed;
}

.like-btn:disabled {
  cursor: not-allowed;
}
</style>
