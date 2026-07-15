import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import {
  renderWithQiankun,
  qiankunWindow,
} from 'vite-plugin-qiankun/dist/helper'
import App from './App.vue'
import routes from './router'

let app: any = null
let router: any = null

function render(props: any = {}) {
  const { container } = props
  const baseRoute = props.baseRoute || '/nlp'

  router = createRouter({
    history: createWebHistory(qiankunWindow.__POWERED_BY_QIANKUN__ ? baseRoute : '/'),
    routes,
  })

  app = createApp(App)
  app.use(router)
  app.use(ElementPlus)
  app.mount(container ? container.querySelector('#app') : '#app')
}

function storeTest(props: any) {
  props.setGlobalState?.({
    sub_nlp: { mounted: true },
  })
}

renderWithQiankun({
  bootstrap() {
    console.log('[sub-nlp] bootstrap')
  },
  mount(props) {
    console.log('[sub-nlp] mount', props)
    storeTest(props)
    render(props)
  },
  unmount(props) {
    console.log('[sub-nlp] unmount')
    app?.unmount()
    app = null
    router = null
  },
  update(props) {
    console.log('[sub-nlp] update', props)
  },
})

// 独立运行时
if (!qiankunWindow.__POWERED_BY_QIANKUN__) {
  render()
}
