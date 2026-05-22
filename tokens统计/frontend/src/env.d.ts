/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'element-plus/dist/locale/en.mjs'
declare module 'element-plus/dist/locale/zh-cn.mjs'
declare module 'element-plus/dist/locale/ja.mjs'
declare module 'element-plus/dist/locale/ko.mjs'
declare module 'element-plus/dist/locale/ru.mjs'
declare module 'element-plus/dist/locale/fr.mjs'
declare module 'element-plus/dist/locale/es.mjs'
