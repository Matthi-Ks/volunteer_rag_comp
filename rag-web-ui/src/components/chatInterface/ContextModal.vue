<script setup lang="ts">
import { FileText, X } from 'lucide-vue-next';

defineProps<{
   isOpen: boolean;
   contexts: string[];
}>();

const emit = defineEmits<{
   (e: 'close'): void;
}>();
</script>

<template>
   <Teleport to="body">
      <div 
         v-if="isOpen" 
         class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4"
         @click.self="emit('close')"
      >
         <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] flex flex-col overflow-hidden">
            <!-- Modal Header -->
            <div class="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center">
               <div class="flex items-center gap-2">
                  <FileText class="w-4 h-4 text-blue-600" />
                  <h3 class="font-semibold text-slate-800 dark:text-slate-100 text-sm">
                     Retrieved Contexts ({{ contexts.length }})
                  </h3>
               </div>
               <button 
                  @click="emit('close')"
                  class="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg transition cursor-pointer"
               >
                  <X class="w-5 h-5" />
               </button>
            </div>

            <!-- Modal Body -->
            <div class="p-6 overflow-y-auto space-y-4 flex-1 font-mono text-xs text-slate-700 dark:text-slate-300">
               <div 
                  v-for="(ctx, idx) in contexts" 
                  :key="idx" 
                  class="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-lg border border-slate-200 dark:border-slate-700/50 space-y-1"
               >
                  <div class="text-[10px] text-blue-600 dark:text-blue-400 font-bold uppercase tracking-wider">
                     Document #{{ idx + 1 }}
                  </div>
                  <p class="whitespace-pre-wrap leading-relaxed">{{ ctx }}</p>
               </div>
            </div>
         </div>
      </div>
   </Teleport>
</template>