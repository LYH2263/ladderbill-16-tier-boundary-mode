<script setup>
import { computed, onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import TierLadder from '../components/TierLadder.vue'
import SegmentTable from '../components/SegmentTable.vue'
const kwh = ref(220)
const peak = ref(false)
const result = ref(null)
const bc = ref(null)
const tierUps = ref([])
const modeLabel = (m) => (m === 'left' ? '含左端' : '含右端')
const isBoundary = computed(() => tierUps.value.some((u) => Math.abs(u - kwh.value) < 1e-9))
const run = async () => {
  bc.value = null
  result.value = await postJSON('/api/bill', { kwh: kwh.value, peak: peak.value, persist: true })
}
const compareModes = async () => {
  bc.value = await postJSON('/api/boundary_compare', { kwh: kwh.value })
}
onMounted(async () => {
  const t = await getJSON('/api/tiers')
  tierUps.value = t.items.map((x) => x.up_to).filter((u) => u != null)
})
</script>
<template>
  <div class="page work">
    <h1>测算工作台</h1>
    <div class="panel form-row">
      <label>电量(kWh) <input type="number" v-model.number="kwh" min="0" step="1" /></label>
      <label><input type="checkbox" v-model="peak" /> 尖峰系数</label>
      <button @click="run">计算并入库</button>
      <button class="ghost" @click="compareModes">双模式对比</button>
    </div>
    <p v-if="isBoundary" class="boundary-hint">⚡ 探针电量 {{ kwh }} kWh 恰好落在档界上，含端模式决定边界电量归属</p>
    <div v-if="result" class="panel">
      <p>
        合计 ¥{{ result.total }}
        <span class="mode-tag">{{ modeLabel(result.boundary_mode) }}</span>
        <span class="muted">记录#{{ result.run_id }}</span>
      </p>
      <TierLadder :segments="result.segments" />
      <SegmentTable :rows="result.segments" />
    </div>
    <div v-if="bc" class="compare-grid">
      <div class="panel">
        <h3>含左端</h3>
        <div class="hero-num">¥{{ bc.left.total }}</div>
        <SegmentTable :rows="bc.left.segments" />
      </div>
      <div class="panel">
        <h3>含右端</h3>
        <div class="hero-num">¥{{ bc.right.total }}</div>
        <SegmentTable :rows="bc.right.segments" />
      </div>
      <div class="panel">
        <h3>差额(左−右)</h3>
        <div class="hero-num">¥{{ bc.delta }}</div>
        <p class="muted">只读对比，未写入运行记录</p>
      </div>
    </div>
  </div>
</template>
<style scoped>
.form-row { display: flex; flex-wrap: wrap; gap: 1rem; align-items: end; }
input[type=number] { width: 6rem; margin-left: 0.35rem; }
.compare-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; margin-top: 0.75rem; }
.mode-tag { margin: 0 0.5rem; padding: 0.1rem 0.5rem; border-radius: 6px; background: color-mix(in srgb, var(--accent) 25%, var(--panel)); font-size: 0.85rem; }
.boundary-hint { color: var(--accent); margin: 0.5rem 0 0; }
.ghost { background: transparent; border: 1px solid var(--muted); }
</style>
