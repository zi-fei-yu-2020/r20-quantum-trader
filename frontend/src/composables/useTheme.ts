import { computed, ref } from 'vue'

export type Theme = 'dark' | 'light'

const STORAGE_KEY = 'r20.ui.theme'
const DEFAULT_THEME: Theme = 'dark'
const theme = ref<Theme>(DEFAULT_THEME)
let initialized = false

function isTheme(value: string | null): value is Theme {
  return value === 'dark' || value === 'light'
}

function updateThemeColor(next: Theme) {
  if (typeof document === 'undefined') return
  const meta = document.querySelector<HTMLMetaElement>('meta[name="theme-color"]')
  if (meta) {
    meta.content = next === 'light' ? '#F5F7FA' : '#091117'
  }
}

function applyTheme(next: Theme) {
  theme.value = next
  if (typeof document !== 'undefined') {
    document.documentElement.dataset.theme = next
    document.documentElement.style.colorScheme = next
    updateThemeColor(next)
  }
}

function initializeTheme() {
  if (initialized) return
  initialized = true
  let saved: string | null = null
  if (typeof window !== 'undefined') {
    try {
      saved = window.localStorage.getItem(STORAGE_KEY)
    } catch {
      // Storage may be blocked by browser privacy settings.
    }
    window.addEventListener('storage', (event) => {
      if (event.key === STORAGE_KEY && isTheme(event.newValue)) {
        applyTheme(event.newValue)
      }
    })
  }
  applyTheme(isTheme(saved) ? saved : DEFAULT_THEME)
}

function setTheme(next: Theme) {
  applyTheme(next)
  if (typeof window !== 'undefined') {
    try {
      window.localStorage.setItem(STORAGE_KEY, next)
    } catch {
      // The active theme still applies for this session when storage is blocked.
    }
  }
}

function toggleTheme() {
  setTheme(theme.value === 'dark' ? 'light' : 'dark')
}

export function useTheme() {
  return {
    theme,
    isDark: computed(() => theme.value === 'dark'),
    isLight: computed(() => theme.value === 'light'),
    initializeTheme,
    setTheme,
    toggleTheme,
  }
}
