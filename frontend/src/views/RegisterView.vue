<template>
  <div class="auth-view">
    <div class="auth-card card">
      <h1 class="auth-title">注册</h1>

      <div v-if="error" class="error-message">{{ error }}</div>

      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <input
            v-model="username"
            type="text"
            class="form-input"
            placeholder="请输入用户名（3-50字符）"
            required
            minlength="3"
            maxlength="50"
          />
        </div>

        <div class="form-group">
          <label class="form-label">密码</label>
          <input
            v-model="password"
            type="password"
            class="form-input"
            placeholder="请输入密码（至少6位）"
            required
            minlength="6"
          />
        </div>

        <div class="form-group">
          <label class="form-label">确认密码</label>
          <input
            v-model="confirmPassword"
            type="password"
            class="form-input"
            placeholder="请再次输入密码"
            required
          />
        </div>

        <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <div class="auth-footer">
        已有账号？
        <router-link to="/login">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  error.value = ''

  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }

  loading.value = true

  try {
    await authStore.register(username.value, password.value)
    // 注册成功后自动登录
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (err) {
    error.value = err.message || '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-view {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - var(--header-height) - 100px);
  padding: 20px;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  padding: 32px;
}

.auth-title {
  font-size: 24px;
  font-weight: 600;
  text-align: center;
  margin-bottom: 24px;
  color: var(--text-color);
}

.error-message {
  padding: 12px 16px;
  margin-bottom: 20px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: var(--radius-sm);
  color: #ff4d4f;
  font-size: 14px;
}

.btn-block {
  width: 100%;
  margin-top: 8px;
}

.auth-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: var(--text-secondary);
}

.auth-footer a {
  color: var(--primary-color);
  font-weight: 500;
}
</style>
