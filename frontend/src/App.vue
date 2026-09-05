<script setup lang="ts">
import { onMounted } from 'vue'
import FeedbackHost from './components/ui/FeedbackHost.vue'
import { useTheme } from './composables/useTheme'

const { initTheme } = useTheme()
onMounted(() => {
  initTheme()
})
</script>

<template>
  <router-view />
  <FeedbackHost />
</template>
