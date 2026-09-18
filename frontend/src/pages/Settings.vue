<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const s = ref({})
const mode = ref('right')
const saving = ref(false)
const load = async () => {
  s.value = await getJSON('/api/settings')
  mode.value = s.value.boundary_mode || 'right'
}
const switchMode = async (m) => {
  if (saving.value || m === mode.value) return
  saving.value = true
  try {
    await putJSON('/api/settings/boundary_mode', { value: m })
    await load()
  } finally {
    saving.value = false
  }
}
onMounted(load)
</script>
<template>
  <div class="page">
    <h1>参数</h1>
    <div class="panel">
      <h3>档界含端模式</h3>
      <p class="muted">电量恰好等于某档上限时，边界电量的归属。切换不修改档价表数值。</p>
      <label class="mode-opt">
        <input type="radio" name="boundary_mode" value="right" :checked="mode === 'right'" @change="switchMode('right')" />
        含右端 <span class="muted">(prev, up]：边界电量归本档（默认）</span>
      </label>
      <label class="mode-opt">
        <input type="radio" name="boundary_mode" value="left" :checked="mode === 'left'" @change="switchMode('left')" />
        含左端 <span class="muted">[prev, up)：边界电量归下一档</span>
      </label>
      <p v-if="saving" class="muted">保存中…</p>
    </div>
    <ul class="panel kv">
      <li v-for="(v, k) in s" :key="k"><span class="muted">{{ k }}</span> {{ v }}</li>
    </ul>
  </div>
</template>
<style scoped>
.kv { list-style: none; padding: 1rem; margin: 0; }
.kv li { padding: 0.35rem 0; border-bottom: 1px solid color-mix(in srgb, var(--muted) 25%, transparent); }
.mode-opt { display: block; padding: 0.3rem 0; cursor: pointer; }
</style>
