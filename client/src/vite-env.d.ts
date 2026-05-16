/// <reference types="vite/client" />

// Поддержка импорта CSS/SCSS файлов
declare module '*.css' {
    const content: string
    export default content
  }
  
  declare module '*.scss' {
    const content: string
    export default content
  }
  
  declare module '*.sass' {
    const content: string
    export default content
  }
  
  declare module '*.less' {
    const content: string
    export default content
  }