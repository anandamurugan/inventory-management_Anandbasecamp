<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div class="card">
      <div class="card-header">
        <h3 class="card-title">{{ t('restocking.budget') }}</h3>
        <span class="budget-value">{{ money(budget) }}</span>
      </div>
      <input
        v-model.number="budget"
        class="budget-slider"
        type="range"
        :min="MIN_BUDGET"
        :max="MAX_BUDGET"
        :step="STEP"
        :aria-label="t('restocking.budgetSlider')"
      />
      <div class="slider-scale">
        <span>{{ money(MIN_BUDGET) }}</span>
        <span>{{ money(MAX_BUDGET) }}</span>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card info">
        <div class="stat-label">{{ t('restocking.budget') }}</div>
        <div class="stat-value">{{ money(budget) }}</div>
      </div>
      <div class="stat-card warning">
        <div class="stat-label">{{ t('restocking.totalCost') }}</div>
        <div class="stat-value">{{ money(totalCost) }}</div>
      </div>
      <div class="stat-card success">
        <div class="stat-label">{{ t('restocking.remaining') }}</div>
        <div class="stat-value">{{ money(remaining) }}</div>
      </div>
    </div>

    <div v-if="orderResult" class="success-banner" role="status">
      <strong>{{ t('restocking.orderSuccess') }}</strong>
      <span>{{ t('restocking.orderId') }}: {{ orderResult.id }}</span>
      <span>{{ t('restocking.expectedDelivery') }}: {{ formatDate(orderResult.expected_delivery) }}</span>
    </div>
    <div v-if="orderError" class="error">{{ orderError }}</div>

    <div class="card">
      <div class="card-header">
        <h3 class="card-title">{{ t('restocking.recommendations') }} ({{ items.length }})</h3>
        <button
          class="place-order-btn"
          type="button"
          :disabled="items.length === 0 || submitting || loading"
          @click="placeOrder"
        >
          {{ submitting ? t('restocking.submitting') : t('restocking.placeOrder') }}
        </button>
      </div>

      <div v-if="loading && items.length === 0" class="loading">{{ t('common.loading') }}</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="items.length === 0" class="empty-state">{{ t('restocking.empty') }}</div>
      <div v-else class="table-container" :class="{ stale: loading }">
        <table>
          <thead>
            <tr>
              <th>{{ t('restocking.table.item') }}</th>
              <th>{{ t('restocking.table.supplier') }}</th>
              <th>{{ t('restocking.table.trend') }}</th>
              <th class="num">{{ t('restocking.table.demandGap') }}</th>
              <th class="num">{{ t('restocking.table.quantity') }}</th>
              <th class="num">{{ t('restocking.table.unitCost') }}</th>
              <th class="num">{{ t('restocking.table.lineTotal') }}</th>
              <th class="num">{{ t('restocking.table.leadTime') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.sku">
              <td>
                <strong>{{ translateProductName(item.name) }}</strong>
                <div class="sku">{{ item.sku }}</div>
              </td>
              <td>{{ item.supplier }}</td>
              <td>
                <span :class="['badge', item.trend]">{{ trendLabel(item.trend) }}</span>
              </td>
              <td class="num">{{ item.demand_gap }}</td>
              <td class="num">
                <strong>{{ item.quantity }}</strong>
                <span v-if="item.fully_covered === false" class="partial-note">{{ t('restocking.partial') }}</span>
              </td>
              <td class="num">{{ money(item.unit_cost) }}</td>
              <td class="num"><strong>{{ money(item.total_cost) }}</strong></td>
              <td class="num">{{ item.lead_time_days }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrency } from '../utils/currency'

const MIN_BUDGET = 0
const MAX_BUDGET = 100000
const STEP = 1000
const DEFAULT_BUDGET = 20000
const DEBOUNCE_MS = 200

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency, currentLocale, translateProductName } = useI18n()

    const budget = ref(DEFAULT_BUDGET)
    const items = ref([])
    const totalCost = ref(0)
    const remaining = ref(DEFAULT_BUDGET)
    const loading = ref(false)
    const error = ref(null)
    const submitting = ref(false)
    const orderError = ref(null)
    const orderResult = ref(null)

    // Monotonic id so a slow, older response can never overwrite a newer one
    let requestSeq = 0
    let debounceTimer = null

    const money = (amount) => formatCurrency(Number(amount) || 0, currentCurrency.value)

    const trendLabel = (trend) => {
      const key = `trends.${trend}`
      const label = t(key)
      return label === key ? trend : label
    }

    const formatDate = (dateString) => {
      const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
      return new Date(dateString).toLocaleDateString(locale, {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const loadRecommendations = async () => {
      const seq = ++requestSeq
      loading.value = true
      error.value = null
      try {
        const data = await api.getRestockingRecommendations(budget.value)
        if (seq !== requestSeq) return
        items.value = data.items || []
        totalCost.value = data.total_cost
        remaining.value = data.remaining
      } catch (err) {
        if (seq !== requestSeq) return
        items.value = []
        totalCost.value = 0
        remaining.value = budget.value
        error.value = t('restocking.loadError', { message: err.message })
      } finally {
        if (seq === requestSeq) loading.value = false
      }
    }

    // Debounce slider drags so we only fetch once the user pauses
    watch(budget, () => {
      clearTimeout(debounceTimer)
      debounceTimer = setTimeout(loadRecommendations, DEBOUNCE_MS)
    })

    const placeOrder = async () => {
      if (items.value.length === 0 || submitting.value) return
      submitting.value = true
      orderError.value = null
      orderResult.value = null
      try {
        orderResult.value = await api.createRestockingOrder({
          budget: budget.value,
          items: items.value.map(i => ({ sku: i.sku, quantity: i.quantity }))
        })
        await loadRecommendations()
      } catch (err) {
        orderError.value = t('restocking.orderError', { message: err.message })
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadRecommendations)
    onBeforeUnmount(() => clearTimeout(debounceTimer))

    return {
      t,
      MIN_BUDGET,
      MAX_BUDGET,
      STEP,
      budget,
      items,
      totalCost,
      remaining,
      loading,
      error,
      submitting,
      orderError,
      orderResult,
      money,
      trendLabel,
      formatDate,
      placeOrder,
      translateProductName
    }
  }
}
</script>

<style scoped>
.budget-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2563eb;
  letter-spacing: -0.025em;
}

.budget-slider {
  width: 100%;
  accent-color: #2563eb;
  cursor: pointer;
}

.slider-scale {
  display: flex;
  justify-content: space-between;
  font-size: 0.813rem;
  color: #64748b;
  margin-top: var(--space-1);
}

.num {
  text-align: right;
  white-space: nowrap;
}

.sku {
  font-size: 0.75rem;
  color: #64748b;
}

.partial-note {
  display: block;
  font-size: 0.688rem;
  color: #92400e;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.stale {
  opacity: 0.6;
  transition: opacity 0.15s ease;
}

.empty-state {
  text-align: center;
  padding: var(--space-10) var(--space-4);
  color: #64748b;
  font-size: 0.938rem;
}

.place-order-btn {
  background: #2563eb;
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  padding: var(--space-3) var(--space-5);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.place-order-btn:hover:not(:disabled) {
  background: #1d4ed8;
}

.place-order-btn:disabled {
  background: #cbd5e1;
  color: #64748b;
  cursor: not-allowed;
}

.success-banner {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-6);
  align-items: center;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #065f46;
  padding: var(--space-4);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-5);
  font-size: 0.938rem;
}
</style>
