import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('auth_token') || '')
  const user = ref(null)
  const initialized = ref(false)

  // 只要有 token 就认为已认证（用于路由守卫）
  const isAuthenticated = computed(() => !!token.value)
  // 用户信息是否已加载
  const isUserLoaded = computed(() => !!user.value)

  async function login(username, password) {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)

    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login failed')
    }

    const data = await response.json()
    token.value = data.access_token
    localStorage.setItem('auth_token', token.value)

    // 获取用户信息
    await fetchUser()

    return data
  }

  async function register(username, password) {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Registration failed')
    }

    return await response.json()
  }

  async function fetchUser() {
    if (!token.value) {
      user.value = null
      return
    }

    try {
      const response = await fetch('/api/auth/me', {
        headers: { 'Authorization': `Bearer ${token.value}` }
      })

      if (response.ok) {
        user.value = await response.json()
      } else {
        // Token 无效
        user.value = null
        token.value = ''
        localStorage.removeItem('auth_token')
      }
    } catch (error) {
      console.error('Failed to fetch user:', error)
      user.value = null
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('auth_token')
  }

  // 初始化时验证 token
  async function initialize() {
    if (token.value) {
      await fetchUser()
    }
    initialized.value = true
  }

  // 执行初始化
  initialize()

  return {
    token,
    user,
    initialized,
    isAuthenticated,
    isUserLoaded,
    login,
    register,
    fetchUser,
    logout
  }
})
