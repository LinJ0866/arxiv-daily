<template>
  <header class="header">
    <div class="header-content container">
      <div class="header-left">
        <router-link to="/" class="logo">
          <img src="/favicon.png" alt="Logo" class="logo-img" />
          <span class="logo-text">Daily arXiv AI Enhanced</span>
        </router-link>
      </div>

      <div class="header-right">
        <!-- 所有用户可见 -->
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link to="/system" class="nav-link">系统</router-link>

        <!-- 登录用户可见 -->
        <template v-if="authStore.isAuthenticated">
          <router-link to="/likes" class="nav-link">我的喜欢</router-link>
          <router-link to="/settings" class="nav-link">设置</router-link>
          <div class="user-info">
            <span class="username">{{ authStore.user?.username }}</span>
            <button class="btn btn-secondary btn-sm" @click="handleLogout">退出</button>
          </div>
        </template>
        <template v-else>
          <router-link to="/login" class="btn btn-secondary">登录</router-link>
          <router-link to="/register" class="btn btn-primary">注册</router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--header-height);
  background: var(--bg-white);
  box-shadow: var(--shadow-sm);
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: var(--text-color);
}

.logo-img {
  height: 36px;
  width: auto;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.nav-link:hover {
  color: var(--primary-color);
  background: rgba(102, 126, 234, 0.1);
}

.nav-link.router-link-active {
  color: var(--primary-color);
  font-weight: 500;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  font-size: 14px;
  color: var(--text-secondary);
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .logo-text {
    display: none;
  }

  .nav-link {
    padding: 6px 8px;
    font-size: 12px;
  }
}
</style>
