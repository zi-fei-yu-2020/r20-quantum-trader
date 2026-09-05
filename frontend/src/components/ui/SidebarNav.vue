<script setup lang="ts">
import { adminNavigation } from '../../config/navigation'
defineEmits<{ navigate: [] }>()
</script>
<template>
  <nav class="workspace-nav" aria-label="管理导航">
    <section v-for="group in adminNavigation" :key="group.label" class="workspace-nav__group">
      <h2>{{ group.label }}</h2>
      <RouterLink
        v-for="item in group.items"
        :key="item.id"
        :to="`/admin/${item.id}`"
        class="workspace-nav__item"
        active-class="is-active"
        @click="$emit('navigate')"
        ><component :is="item.icon" class="size-[18px] shrink-0" aria-hidden="true" /><span>{{
          item.label
        }}</span></RouterLink
      >
    </section>
  </nav>
</template>
