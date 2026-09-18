<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const s = ref({})
const mode = ref('right')
const saved = ref(false)
const busy = ref(false)

const MODES = [
  { value: 'right', label: '含右端', hint: '档区间 (下界, 上界]：电量恰好等于档界时，该度电留在本档（低档）' },
  { value: 'left', label: '含左端', hint: '档区间 [下界, 上界)：电量恰好等于档界时，临界 1 度升入下一档（高档）' },
]

const load = async () => {
  s.value = await getJSON('/api/settings')
  mode.value = s.value.boundary_mode || 'right'
}
onMounted(load)

const save = async () => {
  busy.value = true
  saved.value = false
  try {
    await putJSON('/api/settings/boundary-mode', { boundary_mode: mode.value })
    s.value = await getJSON('/api/settings')
    saved.value = true
  } finally {
    busy.value = false
  }
}
</script>
<template>
  <div class="page">
    <h1>参数</h1>
    <div class="panel">
      <h3>档界含端模式</h3>
      <p class="muted">仅决定电量恰好等于某档上界时临界度电的归属，不修改档价表数值。</p>
      <div class="mode-opts">
        <label v-for="m in MODES" :key="m.value" class="mode-opt" :class="{ active: mode === m.value }">
          <input type="radio" name="boundary_mode" :value="m.value" v-model="mode" @change="saved = false" />
          <span><strong>{{ m.label }}</strong><em>{{ m.hint }}</em></span>
        </label>
      </div>
      <div class="actions">
        <button :disabled="busy" @click="save">保存模式</button>
        <span v-if="saved" class="ok">已保存，下次测算即时生效</span>
        <span class="muted">当前库内模式：{{ s.boundary_mode }}</span>
      </div>
    </div>
    <ul class="panel kv">
      <li v-for="(v, k) in s" :key="k"><span class="muted">{{ k }}</span> {{ v }}</li>
    </ul>
  </div>
</template>
<style scoped>
.kv { list-style: none; padding: 1rem; margin: 0; }
.kv li { padding: 0.35rem 0; border-bottom: 1px solid color-mix(in srgb, var(--muted) 25%, transparent); }
.mode-opts { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin: 0.75rem 0; }
.mode-opt { display: flex; gap: 0.6rem; align-items: start; padding: 0.75rem; border: 1px solid color-mix(in srgb, var(--muted) 40%, transparent); border-radius: 10px; cursor: pointer; }
.mode-opt.active { border-color: var(--accent); background: color-mix(in srgb, var(--accent) 10%, transparent); }
.mode-opt strong { display: block; margin-bottom: 0.25rem; }
.mode-opt em { font-style: normal; color: var(--muted); font-size: 0.85rem; }
.actions { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
.ok { color: var(--accent); font-weight: 600; }
</style>
