<script setup lang="ts">
/**
 * Typewriter — syntax-highlighted brush-stroke code reveal.
 *
 * Tokenizes Python code into colored segments (One Dark palette),
 * then renders each character individually with staggered CSS animations.
 * Syntax colors are visible during the entire animation → seamless
 * transition to CodeMirror.
 */
import { ref, computed, onMounted } from 'vue'

const props = defineProps<{ code: string }>()
const emit = defineEmits<{ (e: 'done'): void }>()

// ── Python tokenizer (One Dark palette) ──────────
interface Token { text: string; cls: string }

const KW = /^(def|class|return|if|elif|else|for|while|import|from|as|try|except|finally|with|yield|and|or|not|in|is|None|True|False|pass|break|continue|raise|lambda|global|nonlocal|assert|del|async|await)\b/
const NUM = /^\d+\.?\d*/
const DECO = /^@\w+/
const SELF = /^self\b/

function tokenizeLine(line: string): Token[] {
  const tokens: Token[] = []
  let i = 0
  while (i < line.length) {
    // Comment — rest of line
    if (line[i] === '#') {
      tokens.push({ text: line.slice(i), cls: 'cmt' })
      break
    }
    // String (single/double quote)
    if (line[i] === '"' || line[i] === "'") {
      const q = line[i]
      // Triple-quoted
      if (line.slice(i, i + 3) === q + q + q) {
        const end = line.indexOf(q + q + q, i + 3)
        const t = end === -1 ? line.slice(i) : line.slice(i, end + 3)
        tokens.push({ text: t, cls: 'str' })
        i += t.length; continue
      }
      let j = i + 1
      while (j < line.length) {
        if (line[j] === '\\') { j += 2; continue }
        if (line[j] === q) { j++; break }
        j++
      }
      tokens.push({ text: line.slice(i, j), cls: 'str' })
      i = j; continue
    }
    // Whitespace
    if (line[i] === ' ' || line[i] === '\t') {
      let j = i
      while (j < line.length && (line[j] === ' ' || line[j] === '\t')) j++
      tokens.push({ text: line.slice(i, j), cls: '' })
      i = j; continue
    }
    // Decimal number
    const rest = line.slice(i)
    if (/^\d/.test(rest)) {
      const m = rest.match(NUM)
      if (m) { tokens.push({ text: m[0], cls: 'num' }); i += m[0].length; continue }
    }
    // Decorator
    if (rest[0] === '@') {
      const m = rest.match(DECO)
      if (m) { tokens.push({ text: m[0], cls: 'deco' }); i += m[0].length; continue }
    }
    // Keyword / self / identifier
    const w = rest.match(/^[a-zA-Z_]\w*/)
    if (w) {
      const word = w[0]
      if (SELF.test(word)) tokens.push({ text: word, cls: 'self' })
      else if (KW.test(word)) tokens.push({ text: word, cls: 'kw' })
      else tokens.push({ text: word, cls: '' })
      i += word.length; continue
    }
    // Punctuation / operators
    tokens.push({ text: line[i], cls: '' })
    i++
  }
  return tokens
}

// ── Characters with syntax class ──────────────────
interface CharData {
  char: string
  delay: number
  dur: number
  ink: string // ink-dry / ink-bleed / ink-wet
  cls: string // syntax highlight class
}

function hash(i: number, j: number): number {
  let h = (i * 31 + j * 7) ^ 0x5e5ab
  h = Math.imul(h ^ (h >>> 13), 0x7feb352d)
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296
}

const chars = computed<CharData[]>(() => {
  const raw = props.code || ''
  const lines = raw.split('\n')
  const result: CharData[] = []
  const lineDelay = 0.03
  const charSpeed = 0.01
  let globalIdx = 0

  for (let li = 0; li < lines.length; li++) {
    const tokens = tokenizeLine(lines[li])
    for (const tok of tokens) {
      for (let ci = 0; ci < tok.text.length; ci++) {
        const r = hash(li, globalIdx++)
        result.push({
          char: tok.text[ci] === ' ' ? ' ' : tok.text[ci],
          delay: li * lineDelay + globalIdx * charSpeed * 0.5 + r * 0.018,
          dur: 0.18 + r * 0.12,
          ink: r > 0.65 ? 'wet' : r > 0.3 ? 'bleed' : 'dry',
          cls: tok.cls,
        })
      }
    }
    if (li < lines.length - 1) {
      result.push({ char: '\n', delay: 0, dur: 0, ink: 'dry', cls: '' })
    }
  }
  return result
})

const totalDuration = computed(() => {
  if (chars.value.length === 0) return 1
  const last = chars.value[chars.value.length - 1]
  return last.delay + last.dur + 0.3
})

const started = ref(false)
onMounted(() => {
  requestAnimationFrame(() => { started.value = true })
  setTimeout(() => emit('done'), (totalDuration.value || 2) * 1000 + 300)
})
</script>

<template>
  <div class="ct" :class="{ 'ct-on': started }">
    <pre class="ct-pre"><span
      v-for="(c, idx) in chars"
      :key="idx"
      :class="['ct-c', 'ink-' + c.ink, c.cls ? 'sy-' + c.cls : '']"
      :style="{ animationDelay: c.delay + 's', animationDuration: c.dur + 's' }"
    >{{ c.char }}</span></pre>
  </div>
</template>

<style scoped>
.ct {
  position: absolute; inset: 0; z-index: 5; overflow: auto;
  background: #0d1117;
}
.ct-pre {
  margin: 0; padding: 12px;
  font-family: 'JetBrains Mono','Fira Code',Consolas,monospace;
  font-size: 0.82rem; line-height: 1.55; tab-size: 4;
  color: #c9d1d9; white-space: pre-wrap; word-break: break-all;
}

/* ── Characters ────────────────────────────────── */
.ct-c {
  display: inline;
  opacity: 0;
  animation: ink-on 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  animation-play-state: paused;
}
.ct-on .ct-c { animation-play-state: running; }

.ink-dry   { animation-name: ink-dry; }
.ink-bleed { animation-name: ink-bleed; }
.ink-wet   { animation-name: ink-wet; }

@keyframes ink-dry   { 0% { opacity: 0; } 100% { opacity: 1; } }
@keyframes ink-bleed { 0% { opacity: 0; filter: blur(1px); } 60% { opacity: 0.8; filter: blur(0.5px); } 100% { opacity: 1; filter: blur(0); } }
@keyframes ink-wet   { 0% { opacity: 0; filter: blur(1.8px); } 100% { opacity: 1; filter: blur(0); } }

/* ── Syntax colors (One Dark) ──────────────────── */
.sy-kw   { color: #c678dd; }  /* keywords */
.sy-str  { color: #98c379; }  /* strings */
.sy-cmt  { color: #5c6370; font-style: italic; }  /* comments */
.sy-num  { color: #d19a66; }  /* numbers */
.sy-deco { color: #61afef; }  /* decorators */
.sy-self { color: #e06c75; }  /* self */
</style>
