<script setup lang="ts">
// Footer - no reactive logic needed
</script>

<template>
  <footer class="app-footer">
    <div class="footer-inner">
      <div class="footer-brand">
        <span class="footer-logo">◆ CS Visual Learn</span>
        <p class="footer-tagline">让每一个抽象概念都有对应的直观动画，让知识看得见。</p>
      </div>
      <div class="footer-links">
        <div class="link-group">
          <h4>学习</h4>
          <router-link to="/wiki">知识百科</router-link>
          <router-link to="/templates">模板库</router-link>
          <router-link to="/study">备考路径</router-link>
        </div>
        <div class="link-group">
          <h4>创作</h4>
          <router-link to="/sandbox">动画沙箱</router-link>
          <router-link to="/gallery">精选画廊</router-link>
          <router-link to="/community">社区</router-link>
        </div>
        <div class="link-group">
          <h4>关于</h4>
          <span class="dead-link">关于我们</span>
          <span class="dead-link">帮助文档</span>
          <span class="dead-link">反馈建议</span>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; 2026 CS Visual Learn. Powered by Manim + DeepSeek.</span>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  padding: var(--space-2xl) var(--space-xl) var(--space-lg);
  z-index: 1;
  position: relative;
}
.footer-inner {
  max-width: var(--max-content-width);
  margin: 0 auto;
  display: flex;
  gap: var(--space-3xl);
  flex-wrap: wrap;
}
.footer-brand {
  flex: 1;
  min-width: 250px;
}
.footer-logo {
  font-size: 1.1rem;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.footer-tagline {
  color: var(--text-tertiary);
  margin-top: var(--space-sm);
  font-size: 0.9rem;
}
.footer-links {
  display: flex;
  gap: var(--space-2xl);
}
.link-group h4 {
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: var(--space-md);
}
.link-group a {
  display: block;
  color: var(--text-tertiary);
  text-decoration: none;
  font-size: 0.85rem;
  padding: 4px 0;
  transition: color var(--transition-fast);
}
.link-group a:hover {
  color: var(--accent-purple-light);
}
.dead-link {
  display: block; color: var(--text-tertiary); font-size: 0.85rem; padding: 4px 0;
  text-decoration: line-through; cursor: not-allowed; opacity: 0.5;
}
.footer-bottom {
  max-width: var(--max-content-width);
  margin: var(--space-xl) auto 0;
  padding-top: var(--space-lg);
  border-top: 1px solid var(--border-color);
  text-align: center;
  color: var(--text-tertiary);
  font-size: 0.8rem;
}
</style>
