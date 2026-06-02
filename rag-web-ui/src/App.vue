<script setup lang="ts">
import ChatInterface from './components/ChatInterface.vue';
import ControlPanel from './components/ControlPanel.vue';
import MetricsPanel from './components/MetricsPanel.vue';
import ProfileSelector from './components/ProfileSelector.vue';

</script>

<template>
  <div class="flex h-screen w-screen overflow-hidden font-sans">
    <aside class="w-64 flex flex-col border-r border-slate-300">
      <ProfileSelector></ProfileSelector>
    </aside>
    <main class="flex-1 flex flex-col justify-between relative bg-slate-100">
      <ChatInterface></ChatInterface>
    </main>
    <section class="w-80 flex flex-col border-l border-slate-300 overflow-y-auto">

      <div class="flex-1 overflow-y-auto p-4 border-b border-slate-200 dark:border-slate-800">
        <MetricsPanel />
      </div>

      <div class="shrink-0 p-4">
        <ControlPanel />
      </div>
    </section>
  </div>

</template>

<style scoped></style>
