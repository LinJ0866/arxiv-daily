import axios from 'axios'

// API 基础地址，可通过环境变量配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：添加 Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理 401 错误（仅在有 token 过期时重定向）
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && localStorage.getItem('auth_token')) {
      // Token 过期，清除并重定向到登录页
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// 文章 API
export const articleApi = {
  getList(params = {}) {
    return api.get('/articles', { params })
  },
  getDetail(id) {
    return api.get(`/articles/${id}`)
  },
  getDates() {
    return api.get('/articles/dates')
  }
}

// 喜欢 API
export const likeApi = {
  like(articleId) {
    return api.post(`/likes/${articleId}`)
  },
  unlike(articleId) {
    return api.delete(`/likes/${articleId}`)
  },
  getList() {
    return api.get('/likes')
  }
}

// 推荐 API
export const recommendationApi = {
  getList(date, limit = 50) {
    return api.get('/recommendations', { params: { target_date: date, limit } })
  },
  recompute() {
    return api.post('/recommendations/recompute')
  }
}

// 偏好设置 API
export const preferenceApi = {
  get() {
    return api.get('/preferences')
  },
  update(data) {
    return api.put('/preferences', data)
  },
  getWeights() {
    return api.get('/preferences/weights')
  },
  updateWeights(data) {
    return api.put('/preferences/weights', data)
  }
}

// Zotero 导入 API
export const zoteroApi = {
  import(file) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/zotero/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

// 用户 API
export const userApi = {
  updatePassword(data) {
    return api.put('/auth/password', data)
  },
  updateProfile(data) {
    return api.put('/auth/profile', data)
  }
}

// 系统 API
export const systemApi = {
  getSchedulerStatus() {
    return api.get('/scheduler/status')
  },
  runPipeline() {
    return api.post('/scheduler/run-now')
  },
  getHistory(limit = 10) {
    return api.get('/scheduler/history', { params: { limit } })
  },
  rebuildEmbeddings() {
    return api.post('/system/rebuild-embeddings')
  }
}
