<template>
  <Transition name="login-fade">
    <div v-if="visible" class="login-overlay">
      <div class="login-card">
        <div class="login-header">
          <div class="login-logo">
            <svg width="44" height="44" viewBox="0 0 40 40">
              <rect width="40" height="40" rx="10" fill="url(#lg)" />
              <text x="20" y="27" text-anchor="middle" fill="#fff" font-size="20" font-weight="700">AI</text>
              <defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#3b82f6" /><stop offset="100%" stop-color="#8b5cf6" /></linearGradient></defs>
            </svg>
          </div>
          <h1 class="login-title">AI 系统平台</h1>
          <p class="login-subtitle">{{ mode === 'login' ? 'AI Systems Platform' : mode === 'register' ? '创建新账号' : '重置密码' }}</p>
        </div>

        <!-- 模式切换 tabs -->
        <div class="mode-tabs" v-if="mode !== 'forgot'">
          <span :class="{ active: mode === 'login' }" @click="switchMode('login')">登录</span>
          <span :class="{ active: mode === 'register' }" @click="switchMode('register')">注册</span>
        </div>

        <!-- 登录表单 -->
        <el-form v-if="mode === 'login'" ref="formRef" :model="form" :rules="loginRules" class="login-form" @keyup.enter="handleLogin">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" size="large" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="密码" :prefix-icon="Lock" size="large" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="handleLogin">
              {{ loading ? '登录中…' : '登 录' }}
            </el-button>
          </el-form-item>
          <div class="login-links">
            <el-button link type="primary" size="small" @click="switchMode('forgot')">忘记密码？</el-button>
          </div>
        </el-form>

        <!-- 注册表单 -->
        <el-form v-if="mode === 'register'" ref="regFormRef" :model="regForm" :rules="regRules" class="login-form">
          <el-form-item prop="username">
            <el-input v-model="regForm.username" placeholder="用户名（英文）" :prefix-icon="User" size="large" />
          </el-form-item>
          <el-form-item prop="displayName">
            <el-input v-model="regForm.displayName" placeholder="显示名（中文姓名）" :prefix-icon="User" size="large" />
          </el-form-item>
          <el-form-item prop="email">
            <el-input v-model="regForm.email" placeholder="邮箱" :prefix-icon="Message" size="large" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="regForm.password" type="password" placeholder="密码（至少6位）" :prefix-icon="Lock" size="large" show-password />
          </el-form-item>
          <el-form-item prop="confirmPwd">
            <el-input v-model="regForm.confirmPwd" type="password" placeholder="确认密码" :prefix-icon="Lock" size="large" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="success" size="large" class="login-btn" :loading="regLoading" @click="handleRegister">
              {{ regLoading ? '注册中…' : '注 册' }}
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 忘记密码 -->
        <el-form v-if="mode === 'forgot'" ref="fpFormRef" :model="fpForm" :rules="fpRules" class="login-form">
          <p class="fp-hint">输入用户名和新密码，密码将被重置</p>
          <el-form-item prop="username">
            <el-input v-model="fpForm.username" placeholder="用户名" :prefix-icon="User" size="large" />
          </el-form-item>
          <el-form-item prop="email">
            <el-input v-model="fpForm.email" placeholder="注册邮箱" :prefix-icon="Message" size="large" />
          </el-form-item>
          <el-form-item prop="newPassword">
            <el-input v-model="fpForm.newPassword" type="password" placeholder="新密码（至少6位）" :prefix-icon="Lock" size="large" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="warning" size="large" class="login-btn" :loading="fpLoading" @click="handleForgotPwd">
              {{ fpLoading ? '重置中…' : '重置密码' }}
            </el-button>
          </el-form-item>
          <el-button link type="primary" size="small" style="width:100%" @click="switchMode('login')">← 返回登录</el-button>
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
import { User, Lock, Message } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import axios from 'axios'

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{ login: [data: { token: string; user: any }] }>()

const mode = ref<'login' | 'register' | 'forgot'>('login')

const formRef = ref<FormInstance>()
const regFormRef = ref<FormInstance>()
const fpFormRef = ref<FormInstance>()
const loading = ref(false)
const regLoading = ref(false)
const fpLoading = ref(false)
const error = ref('')

const form = reactive({ username: '', password: '' })
const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const regForm = reactive({ username: '', displayName: '', email: '', password: '', confirmPwd: '' })
const validateConfirm = (_rule: any, value: string, cb: any) => {
  if (value !== regForm.password) cb(new Error('两次密码不一致'))
  else cb()
}
const regRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPwd: [{ validator: validateConfirm, trigger: 'blur' }],
}

const fpForm = reactive({ username: '', email: '', newPassword: '' })
const fpRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入注册邮箱', trigger: 'blur' }],
  newPassword: [{ required: true, min: 6, message: '新密码至少6位', trigger: 'blur' }],
}

function switchMode(m: 'login' | 'register' | 'forgot') {
  mode.value = m
  error.value = ''
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true; error.value = ''
  try {
    const res = await axios.post('/api/users/login', { username: form.username, password: form.password })
    const data = res.data
    if (data.code === 200 && data.data?.accessToken) {
      emit('login', { token: data.data.accessToken, user: data.data.user })
    } else {
      error.value = data.message || '登录失败'
    }
  } catch (e: any) {
    error.value = e.response?.data?.message || '无法连接到认证服务'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  const valid = await regFormRef.value?.validate().catch(() => false)
  if (!valid) return
  regLoading.value = true; error.value = ''
  try {
    const res = await axios.post('/api/users/register', {
      username: regForm.username,
      email: regForm.email,
      password: regForm.password,
      displayName: regForm.displayName,
    })
    if (res.data.code === 200) {
      error.value = ''
      ElMessage.success('注册成功！请登录')
      switchMode('login')
      form.username = regForm.username
      form.password = ''
    } else {
      error.value = res.data.message || '注册失败'
    }
  } catch (e: any) {
    error.value = e.response?.data?.message || '注册失败'
  } finally {
    regLoading.value = false
  }
}

async function handleForgotPwd() {
  const valid = await fpFormRef.value?.validate().catch(() => false)
  if (!valid) return
  fpLoading.value = true; error.value = ''
  try {
    // 通过 admin 接口重置密码（需要先验证用户名和邮箱匹配）
    const res = await axios.put('/api/admin/users/forgot-password', {
      username: fpForm.username,
      email: fpForm.email,
      newPassword: fpForm.newPassword,
    })
    if (res.data.code === 200) {
      ElMessage.success('密码已重置，请登录')
      switchMode('login')
      form.username = fpForm.username
      form.password = ''
    } else {
      error.value = res.data.message || '重置失败'
    }
  } catch (e: any) {
    error.value = e.response?.data?.message || '用户名或邮箱不匹配'
  } finally {
    fpLoading.value = false
  }
}
</script>

<script lang="ts">
import { ElMessage } from 'element-plus'
export default { name: 'LoginDialog' }
</script>

<style scoped>
.login-overlay {
  position: fixed; inset: 0; z-index: 9999;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
}

.login-card {
  width: 420px; padding: 36px 32px 28px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(24px); border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); text-align: center;
}

.login-header { margin-bottom: 24px; }
.login-logo { margin-bottom: 12px; }
.login-title { font-size: 22px; font-weight: 700; color: #1a1d28; margin: 0; }
.login-subtitle { font-size: 13px; color: #9ca3af; margin: 4px 0 0; }

.mode-tabs {
  display: flex; border-bottom: 2px solid #f0f1f4; margin-bottom: 20px;
}
.mode-tabs span {
  flex: 1; padding: 10px 0; cursor: pointer; font-size: 14px; font-weight: 600;
  color: #9ca3af; transition: all 0.2s; border-bottom: 2px solid transparent; margin-bottom: -2px;
}
.mode-tabs span.active { color: #3b82f6; border-bottom-color: #3b82f6; }

.login-form { text-align: left; }
.login-btn { width: 100%; height: 44px; font-size: 15px; border-radius: 10px; }
.login-error { color: #ef4444; font-size: 13px; margin: 12px 0 0; }
.login-footer { margin-top: 20px; font-size: 12px; color: #adb5bd; }
.login-links { text-align: right; margin-top: -12px; }
.fp-hint { font-size: 13px; color: #6b7280; margin-bottom: 16px; text-align: center; }

.login-fade-enter-active, .login-fade-leave-active { transition: all 0.4s ease; }
.login-fade-enter-from, .login-fade-leave-to { opacity: 0; }
</style>
