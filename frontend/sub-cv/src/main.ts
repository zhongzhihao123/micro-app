import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { renderWithQiankun, qiankunWindow } from 'vite-plugin-qiankun/dist/helper'
import App from './App.vue'
import routes from './router'

let app: any = null, router: any = null

function render(props: any = {}) {
  const { container } = props
  router = createRouter({
    history: createWebHistory(qiankunWindow.__POWERED_BY_QIANKUN__ ? (props.baseRoute || '/cv') : '/'),
    routes,
  })
  app = createApp(App)
  app.use(router)
  app.use(ElementPlus)
  app.mount(container ? container.querySelector('#app') : '#app')
}

renderWithQiankun({
  bootstrap() {},
  mount(props) { render(props) },
  unmount() { app?.unmount(); app = null; router = null },
  update() {},
})

if (!qiankunWindow.__POWERED_BY_QIANKUN__) { render() }
