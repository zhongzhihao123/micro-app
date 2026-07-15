<template>
  <Transition name="login-fade">
    <div v-if="visible" class="login-overlay">
      <div class="login-card">
        <div class="login-header">
          <div class="login-logo">
            <svg width="40" height="40" viewBox="0 0 40 40">
              <rect width="40" height="40" rx="10" fill="url(#lg)" />
              <text x="20" y="27" text-anchor="middle" fill="#fff" font-size="20" font-weight="700">AI</text>
              <defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#3b82f6" /><stop offset="100%" stop-color="#8b5cf6" /></linearGradient></defs>
            </svg>
          </div>
          <h1 class="login-title">AI 系统平台</h1>
          <p class="login-subtitle">AI Systems Platform</p>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          class="login-form"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="用户名"
              :prefix-icon="User"
              size="large"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码"
              :prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              {{ loading ? '登录中…' : '登 录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <p v-if="error" class="login-error">{{ error }}</p>

        <div class="login-footer">
          <span>演示账号：admin / admin123</span>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { User, Lock } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import axios from 'axios'

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{ login: [token: string] }>()

const formRef = ref<FormInstance>()
const loading = ref(false)
const error = ref('')

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  error.value = ''

  try {
    // 调用 Java Gateway 登录
    const res = await axios.post('http://localhost:8100/api/users/login', {
      username: form.username,
      password: form.password,
    })
    const data = res.data
    if (data.code === 200 && data.data?.accessToken) {
      emit('login', data.data.accessToken)
    } else {
      error.value = data.message || '登录失败'
    }
  } catch (e: any) {
    error.value = e.response?.data?.message || '无法连接到认证服务'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e8ecf1 0%, #dde1e8 50%, #e0e4ec 100%);
}

.login-card {
  width: 400px;
  padding: 40px 36px 32px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(24px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.login-header {
  margin-bottom: 32px;
}

.login-logo {
  margin-bottom: 12px;
}

.login-title {
  font-size: 22px;
  font-weight: 700;
  color: #1a1d28;
  margin: 0;
}

.login-subtitle {
  font-size: 13px;
  color: #9ca3af;
  margin: 4px 0 0;
}

.login-form {
  text-align: left;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  border-radius: 10px;
}

.login-error {
  color: #ef4444;
  font-size: 13px;
  margin: 12px 0 0;
}

.login-footer {
  margin-top: 24px;
  font-size: 12px;
  color: #adb5bd;
}

.login-fade-enter-active,
.login-fade-leave-active {
  transition: all 0.4s ease;
}
.login-fade-enter-from,
.login-fade-leave-to {
  opacity: 0;
  backdrop-filter: blur(0);
}
</style>
