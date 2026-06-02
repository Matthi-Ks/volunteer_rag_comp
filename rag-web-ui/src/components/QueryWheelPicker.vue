<script setup lang="ts">
import { ref, watch } from 'vue';
import { ChevronUp, ChevronDown } from 'lucide-vue-next';

// Props & Emits definieren (TypeScript-strikte Syntax)
const props = defineProps<{
   queries: string[];
   modelValue: number; // Ermöglicht v-model Anbindung für den Index
}>();

const emit = defineEmits<{
   (e: 'update:modelValue', index: number): void;
   (e: 'change', queryText: string): void;
}>();

// Lokaler Index, synchronisiert mit dem Prop
const localIndex = ref(props.modelValue);

// Überwache Änderungen von außen (falls das Elternteil den Index zurücksetzt)
watch(() => props.modelValue, (newVal) => {
   localIndex.value = newVal;
});

// Helfer zum Aktualisieren des States
const updateSelection = (newIndex: number) => {
   if (newIndex >= 0 && newIndex < props.queries.length) {
      localIndex.value = newIndex;
      emit('update:modelValue', newIndex);
      emit('change', props.queries[newIndex]);
   }
};

const scrollUp = () => updateSelection(localIndex.value - 1);
const scrollDown = () => updateSelection(localIndex.value + 1);
</script>

<template>
   <div
      class="relative flex items-center justify-center p-2 h-36 overflow-hidden shadow-inner w-full">

      <div class="absolute left-4 flex flex-col space-y-2 z-10">
         <button @click="scrollUp" :disabled="localIndex === 0"
            class="p-1.5 rounded bg-blue-600 hover:bg-blue-500 text-slate-300 disabled:opacity-20 disabled:cursor-not-allowed transition">
            <ChevronUp class="w-4 h-4" />
         </button>
         <button @click="scrollDown" :disabled="localIndex === queries.length - 1"
            class="p-1.5 rounded bg-blue-600 hover:bg-blue-500 text-slate-300 disabled:opacity-20 disabled:cursor-not-allowed transition">
            <ChevronDown class="w-4 h-4" />
         </button>
      </div>

      <div
         class="flex flex-col items-center space-y-1 transition-all duration-300 ease-out text-center w-full max-w-xl px-12"
         :style="{ transform: `translateY(${(localIndex * -28) + 58}px)` }">
         <div v-for="(query, idx) in queries" :key="idx" @click="updateSelection(idx)" :class="[
            'text-xs transition-all duration-200 h-6 truncate w-full flex items-center justify-center cursor-pointer select-none',
            idx === localIndex ? 'text-blue-400 font-bold scale-105' : 'text-slate-600 scale-95 opacity-40 blur-[0.3px]',
            Math.abs(idx - localIndex) === 1 ? 'opacity-60 text-slate-400' : '',
            Math.abs(idx - localIndex) > 1 ? 'opacity-10 text-slate-700 pointer-events-none' : ''
         ]">
            {{ query }}
         </div>
      </div>
   </div>
</template>