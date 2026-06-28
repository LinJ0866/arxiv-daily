<template>
  <footer class="footer">
    <div class="footer-content container">
      <p class="copyright">
        © {{ currentYear }} arXiv Daily AI Enhanced. Built with Vue 3 + FastAPI
      </p>
      <div class="links">
        <a href="https://arxiv.org" target="_blank" rel="noopener">arXiv</a>
        <a href="https://github.com/dw-dengwei/daily-arXiv-ai-enhanced" target="_blank" rel="noopener">GitHub</a>
      </div>
    </div>
  </footer>
</template>

<script setup>
const currentYear = new Date().getFullYear()
</script>

<style scoped>
.footer {
  background: var(--bg-white);
  border-top: 1px solid var(--border-color);
  padding: 20px 0;
  margin-top: auto;
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.copyright {
  font-size: 14px;
  color: var(--text-tertiary);
}

.links {
  display: flex;
  gap: 16px;
}

.links a {
  font-size: 14px;
  color: var(--text-secondary);
}

.links a:hover {
  color: var(--primary-color);
}

@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
}
</style>
