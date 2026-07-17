import type { Directive } from 'vue'

/**
 * 磁吸按钮效果指令
 * 鼠标靠近时按钮被"吸引"过去
 * 使用方式：v-magnet 或 v-magnet="20"（磁吸强度）
 */
export const vMagnet: Directive<HTMLElement, number | undefined> = {
  mounted(el, binding) {
    const strength = binding.value ?? 15 // 磁吸强度（像素）

    // 减少动效模式不启用
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    // 触摸设备不启用
    if (window.matchMedia('(pointer: coarse)').matches) return

    el.style.transition = 'transform 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94)'

    let parentEl: HTMLElement | null = el.parentElement

    function handleMove(e: MouseEvent) {
      if (!parentEl) parentEl = el.parentElement
      if (!parentEl) return

      const rect = el.getBoundingClientRect()
      const parentRect = parentEl.getBoundingClientRect()

      const centerX = rect.left + rect.width / 2
      const centerY = rect.top + rect.height / 2

      const deltaX = e.clientX - centerX
      const deltaY = e.clientY - centerY

      const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)
      const maxDistance = Math.max(parentRect.width, parentRect.height) * 0.5

      if (distance < maxDistance) {
        const force = 1 - distance / maxDistance
        const moveX = deltaX * force * (strength / 100)
        const moveY = deltaY * force * (strength / 100)
        el.style.transform = `translate(${moveX}px, ${moveY}px)`
      } else {
        el.style.transform = 'translate(0, 0)'
      }
    }

    function handleLeave() {
      el.style.transform = 'translate(0, 0)'
    }

    // 监听父元素的鼠标移动
    const target = parentEl || el
    target.addEventListener('mousemove', handleMove)
    target.addEventListener('mouseleave', handleLeave)

    ;(el as any)._magnetCleanup = () => {
      target.removeEventListener('mousemove', handleMove)
      target.removeEventListener('mouseleave', handleLeave)
    }
  },

  unmounted(el) {
    if ((el as any)._magnetCleanup) {
      (el as any)._magnetCleanup()
    }
  },
}
