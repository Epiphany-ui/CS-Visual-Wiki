import type { Directive } from 'vue'

/**
 * 点击波纹效果指令
 * 使用方式：v-ripple 或 v-ripple="'rgba(124, 58, 237, 0.3)'"
 */
export const vRipple: Directive<HTMLElement, string | undefined> = {
  mounted(el, binding) {
    el.style.position = el.style.position || 'relative'
    el.style.overflow = el.style.overflow || 'hidden'

    el.addEventListener('mousedown', (e: MouseEvent) => {
      const rect = el.getBoundingClientRect()
      const size = Math.max(rect.width, rect.height) * 2
      const x = e.clientX - rect.left - size / 2
      const y = e.clientY - rect.top - size / 2

      const ripple = document.createElement('span')
      ripple.className = 'ripple-effect'
      ripple.style.width = ripple.style.height = `${size}px`
      ripple.style.left = `${x}px`
      ripple.style.top = `${y}px`
      ripple.style.background = binding.value || 'rgba(255, 255, 255, 0.25)'

      el.appendChild(ripple)

      const cleanup = () => {
        ripple.remove()
        ripple.removeEventListener('animationend', cleanup)
      }
      ripple.addEventListener('animationend', cleanup)

      // 兜底：600ms 后强制移除
      setTimeout(cleanup, 600)
    })
  },
}

// 波纹动画样式（注入一次）
const styleId = 'ripple-directive-style'
if (!document.getElementById(styleId)) {
  const style = document.createElement('style')
  style.id = styleId
  style.textContent = `
    .ripple-effect {
      position: absolute;
      border-radius: 50%;
      transform: scale(0);
      animation: ripple-expand 0.6s ease-out forwards;
      pointer-events: none;
      opacity: 0.6;
    }
    @keyframes ripple-expand {
      to {
        transform: scale(1);
        opacity: 0;
      }
    }
    @media (prefers-reduced-motion: reduce) {
      .ripple-effect {
        animation: none;
        display: none;
      }
    }
  `
  document.head.appendChild(style)
}
