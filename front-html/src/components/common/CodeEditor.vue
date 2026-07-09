<script setup lang="ts">
import { Codemirror } from 'vue-codemirror'
import { python } from '@codemirror/lang-python'
import { oneDark } from '@codemirror/theme-one-dark'

const model = defineModel<string>({ default: '' })

const props = withDefaults(defineProps<{
  readonly?: boolean
}>(), {
  readonly: false,
})

const extensions = [python(), oneDark]
</script>

<template>
  <div class="code-editor-wrap">
    <Codemirror
      v-model="model"
      :extensions="extensions"
      :disabled="readonly"
      :indent-with-tab="true"
      :tab-size="4"
      :style="{ height: '100%' }"
    />
  </div>
</template>

<style scoped>
.code-editor-wrap {
  height: 100%;
  overflow: hidden;
  border-radius: var(--radius-md);
}
.code-editor-wrap :deep(.cm-editor) {
  height: 100%;
}
.code-editor-wrap :deep(.cm-scroller) {
  font-family: var(--font-mono);
  font-size: 0.82rem;
}
.code-editor-wrap :deep(.cm-content) {
  padding: 12px;
}
</style>
