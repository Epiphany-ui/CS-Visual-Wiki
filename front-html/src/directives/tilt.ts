import type { Directive } from 'vue'

/**
 * 3D 卡片倾斜效果指令
 * 使用方式：v-tilt 或 v-tilt="{ max: 15, glare: true }"
 */
interface TiltOptions {
  max?: number    // 最大倾斜角度
  glare?: boolean // 是否开启反光效果
  scale?: number  // 悬停缩放
}

export const vTilt: Directive<HTMLElement, TiltOptions | undefined> = {
  mounted(el, binding) {
    const options = binding.value || {}
    const maxTilt = options.max ?? 20
    const enableGlare = options.glare ?? true
    const scale = options.scale ?? 1.05

    // 减少动效模式不启用
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    // 触摸设备不启用
    if (window.matchMedia('(pointer: coarse)').matches) return

    el.style.transformStyle = 'preserve-3d'
    el.style.transition = 'transform 0.15s ease-out'
    el.style.perspective = '1000px'

    // 创建反光层
    let glareEl: HTMLDivElement | null = null
    if (enableGlare) {
      glareEl = document.createElement('div')
      glareEl.className = 'tilt-glare'
      glareEl.style.cssText = `
        position: absolute;
        inset: 0;
        border-radius: inherit;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: 10;
        background: linear-gradient(
          135deg,
          rgba(255, 255, 255, 0.15) 0%,
          transparent 60%
        );
      `
      el.style.position = el.style.position || 'relative'
      el.style.overflow = 'hidden'
      el.appendChild(glareEl)
    }

    function handleMove(e: MouseEvent) {
      const rect = el.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      const centerX = rect.width / 2
      const centerY = rect.height / 2

      const rotateX = ((y - centerY) / centerY) * -maxTilt
      const rotateY = ((x - centerX) / centerX) * maxTilt

      el.style.transform = `
        perspective(1000px)
        rotateX(${rotateX}deg)
        rotateY(${rotateY}deg)
        scale(${scale})
      `

      // 更新反光位置
      if (glareEl) {
        const glareX = (x / rect.width) * 100
        const glareY = (y / rect.height) * 100
        glareEl.style.background = `
          radial-gradient(
            circle at ${glareX}% ${glareY}%,
            rgba(255, 255, 255, 0.18) 0%,
            transparent 55%
          )
        `
      }
    }

    function handleEnter() {
      if (glareEl) glareEl.style.opacity = '1'
    }

    function handleLeave() {
      el.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)'
      if (glareEl) glareEl.style.opacity = '0'
    }

    el.addEventListener('mousemove', handleMove)
    el.addEventListener('mouseenter', handleEnter)
    el.addEventListener('mouseleave', handleLeave)

    // 保存引用以便卸载
    ;(el as any)._tiltCleanup = () => {
      el.removeEventListener('mousemove', handleMove)
      el.removeEventListener('mouseenter', handleEnter)
      el.removeEventListener('mouseleave', handleLeave)
      if (glareEl) glareEl.remove()
    }
  },

  unmounted(el) {
    if ((el as any)._tiltCleanup) {
      (el as any)._tiltCleanup()
    }
  },
}
