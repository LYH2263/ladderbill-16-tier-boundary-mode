<script setup>
import { computed, onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import TierLadder from '../components/TierLadder.vue'
import SegmentTable from '../components/SegmentTable.vue'

const kwh = ref(180)
const peak = ref(false)
const result = ref(null)
const boundaries = ref([])
const compare = ref(null)
const busy = ref(false)

const MODE_LABEL = { right: '含右端', left: '含左端' }
const MODE_HINT = {
  right: '档界度电留在本档（低档）',
  left: '临界 1 度升入下一档（高档）',
}

onMounted(async () => {
  const t = await getJSON('/api/tiers')
  boundaries.value = t.items.map((x) => x.up_to).filter((x) => x != null).map(Number)
})

const isCritical = computed(() =>
  boundaries.value.some((b) => Math.abs(Number(kwh.value) - b) < 1e-9),
)

const run = async () => {
  busy.value = true
  try {
    result.value = await postJSON('/api/bill', { kwh: Number(kwh.value), peak: peak.value, persist: true })
    compare.value = null
  } finally {
    busy.value = false
  }
}

const runCompare = async () => {
  busy.value = true
  try {
    compare.value = await postJSON('/api/boundary-compare', { kwh: Number(kwh.value), peak: peak.value })
  } finally {
    busy.value = false
  }
}
</script>
<template>
  <div class="page work">
    <h1>测算工作台</h1>
    <div class="panel form-row">
      <label>电量(kWh) <input type="number" v-model.number="kwh" min="0" step="1" /></label>
      <label><input type="checkbox" v-model="peak" /> 尖峰系数</label>
      <button @click="run" :disabled="busy">计算并入库</button>
      <button class="ghost" @click="runCompare" :disabled="busy">双模式并列对比（只读）</button>
    </div>

    <p v-if="isCritical" class="critical">
      探针电量 {{ kwh }} kWh 恰好落在档界上：两种含端模式的归属不同，可点右侧按钮对比。
    </p>

    <div v-if="result" class="panel">
      <div class="result-head">
        <p class="total">合计 ¥{{ result.total }} <span class="muted">记录#{{ result.run_id }}</span></p>
        <span class="badge" :class="result.boundary_mode">
          当前模式：{{ MODE_LABEL[result.boundary_mode] }} · {{ MODE_HINT[result.boundary_mode] }}
        </span>
      </div>
      <p v-if="isCritical" class="muted small">
        本明细按当前模式{{ MODE_LABEL[result.boundary_mode] }}归属；改模式后重新测算，此处徽标与分段即时切换。
      </p>
      <TierLadder :segments="result.segments" />
      <SegmentTable :rows="result.segments" />
    </div>

    <div v-if="compare" class="panel">
      <h3>双模式只读对比 <span class="muted small">（不写运行记录）· 当前库内模式：{{ MODE_LABEL[compare.current_mode] }}</span></h3>
      <div class="cmp-grid">
        <div v-for="m in ['right', 'left']" :key="m" class="cmp-col" :class="{ current: compare.current_mode === m }">
          <h4>
            {{ MODE_LABEL[m] }}
            <span v-if="compare.current_mode === m" class="tag">当前</span>
          </h4>
          <div class="hero-num" style="font-size:1.8rem">¥{{ compare.modes[m].total }}</div>
          <p class="muted small">{{ MODE_HINT[m] }}</p>
          <SegmentTable :rows="compare.modes[m].segments" />
        </div>
      </div>
    </div>
  </div>
</template>
<style scoped>
.form-row { display: flex; flex-wrap: wrap; gap: 1rem; align-items: end; }
input[type=number] { width: 6rem; margin-left: 0.35rem; }
button.ghost { background: transparent; color: var(--accent); border: 1px solid var(--accent); }
.result-head { display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; }
.total { margin: 0.25rem 0; font-size: 1.2rem; }
.badge { font-size: 0.8rem; padding: 0.3rem 0.6rem; border-radius: 999px; border: 1px solid var(--muted); }
.badge.right { color: var(--accent); border-color: var(--accent); }
.badge.left { color: #e8b94d; border-color: #e8b94d; }
.critical { background: color-mix(in srgb, #e8b94d 15%, transparent); border: 1px solid #e8b94d; padding: 0.6rem 0.8rem; border-radius: 8px; }
.small { font-size: 0.82rem; }
.cmp-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.cmp-col { padding: 0.75rem; border: 1px solid color-mix(in srgb, var(--muted) 35%, transparent); border-radius: 10px; }
.cmp-col.current { border-color: var(--accent); }
.cmp-col h4 { margin: 0 0 0.5rem; }
.tag { font-size: 0.7rem; background: var(--accent); color: #111; padding: 0.1rem 0.45rem; border-radius: 999px; margin-left: 0.4rem; }
</style>
