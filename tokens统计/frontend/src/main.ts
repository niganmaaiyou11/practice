import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/global.css'

// ECharts tree-shaking
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart, ScatterChart } from 'echarts/charts'
import {
  TooltipComponent,
  GridComponent,
  LegendComponent,
  DataZoomComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, BarChart, LineChart, PieChart, ScatterChart, TooltipComponent, GridComponent, LegendComponent, DataZoomComponent])

const app = createApp(App)
app.use(ElementPlus)
app.use(createPinia())
app.use(router)
app.component('v-chart', VChart)
app.mount('#app')
