import axios from 'axios'

const api = axios.create({
  baseURL: '/',
  timeout: 10000
})

// API methods
export const apiService = {
  // Get service status
  async getStatus() {
    const response = await api.get('/')
    return response.data
  },

  // Get all bindings
  async getAllBindings() {
    const response = await api.get('/api/bindings')
    return response.data
  },

  // Get specific binding by UIN
  async getBinding(uin) {
    const response = await api.get(`/api/binding/${uin}`)
    return response.data
  },

  // Check OAuth authorization status
  async checkAuthStatus(loginCode) {
    const response = await api.get('/oauth/check_status', {
      params: { login_code: loginCode }
    })
    return response.data
  },

  // OAuth authorize - this redirects, so we handle it differently
  buildAuthorizeUrl(params) {
    const query = new URLSearchParams(params).toString()
    return `/oauth/authorize?${query}`
  },

  // Build bind URL
  buildBindUrl(bindCode) {
    return `/bind/${bindCode}`
  }
}

export default api
