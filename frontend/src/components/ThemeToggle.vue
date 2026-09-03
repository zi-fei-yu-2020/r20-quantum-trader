<script setup lang="ts">
import { Moon, Sun } from 'lucide-vue-next'
import { useTheme } from '../composables/useTheme'

const { isDark, toggleTheme } = useTheme()
</script>

<template>
  <button
    type="button"
    class="r20-theme-toggle"
    :aria-label="isDark ? '切换到亮色主题' : '切换到暗色主题'"
    :title="isDark ? '切换到亮色主题' : '切换到暗色主题'"
    :aria-pressed="!isDark"
    @click="toggleTheme"
  >
    <Sun v-if="isDark" class="h-3.5 w-3.5" aria-hidden="true" />
    <Moon v-else class="h-3.5 w-3.5" aria-hidden="true" />
    <span class="hidden sm:inline">{{ isDark ? '亮色' : '暗色' }}</span>
  </button>
</template>
