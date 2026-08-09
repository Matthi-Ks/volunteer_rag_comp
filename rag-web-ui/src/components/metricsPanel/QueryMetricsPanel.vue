<script setup lang="ts">
import { ref, computed } from 'vue';
import type { EvaluationResult } from '@/types/backendTypes';
import { QuestionVariant } from '@/types/backendTypes';

const props = defineProps<{
   results: EvaluationResult[] | null
}>();

const tabs = [
   { label: 'Normal', variant: QuestionVariant.NORMAL },
   { label: 'Abstract', variant: QuestionVariant.ABSTRACT },
   { label: 'Detailed', variant: QuestionVariant.DETAILED }
];

const activeTab = ref<QuestionVariant>(QuestionVariant.NORMAL);

const activeResult = computed<EvaluationResult | null>(() => {
   if (!props.results) return null;
   return props.results.find(r => r.question_variant === activeTab.value) || null;
});

const formatScore = (val: number | undefined) => {
   if (val === undefined || isNaN(val)) return '—';
   return val.toFixed(2);
};

const getScoreColorClass = (score: number | undefined) => {
   if (score === undefined) return 'bg-slate-200';
   if (score >= 0.8) return 'bg-emerald-500';
   if (score >= 0.5) return 'bg-amber-500';
   return 'bg-rose-500';
};

const determineBarWidth = (score: number | undefined) => {
    if (score && score >= 0) return `${score*100}%`;
    return '0%';
};
</script>

<template>
   <div class="space-y-3">
      <div class="flex items-center justify-between">
         <h2 class="font-semibold uppercase tracking-wider text-slate-500 text-xs">
            Current Query
         </h2>
         <span v-if="!results" class="text-[10px] bg-slate-200 text-slate-600 px-1.5 py-0.5 rounded font-mono">
            No Run
         </span>
      </div>

      <div class="grid grid-cols-3 gap-1 bg-slate-200/60 p-1 rounded-lg">
         <button 
            v-for="tab in tabs" 
            :key="tab.variant"
            @click="activeTab = tab.variant"
            :disabled="!results"
            :class="[
               'py-1 text-[10px] font-medium rounded transition duration-200',
               !results ? 'opacity-40 cursor-not-allowed' : '',
               activeTab === tab.variant && results
                  ? 'bg-white text-blue-600 shadow-sm font-semibold' 
                  : 'text-slate-600 hover:text-slate-900'
            ]"
         >
            {{ tab.label }}
         </button>
      </div>

      <div class="font-mono text-slate-600 space-y-4 pt-1">
         <div class="space-y-3">
            <div class="space-y-1">
               <div class="flex justify-between items-center text-[11px]">
                  <span>context precision</span>
                  <span class="font-bold text-slate-800">
                     {{ formatScore(activeResult?.context_precision) }}
                  </span>
               </div>
               <div class="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                  <div 
                     class="h-full transition-all duration-500 ease-out"
                     :class="getScoreColorClass(activeResult?.context_precision)"
                     :style="{ width: determineBarWidth(activeResult?.context_precision) }"
                  ></div>
               </div>
            </div>

            <div class="space-y-1">
               <div class="flex justify-between items-center text-[11px]">
                  <span>context recall</span>
                  <span class="font-bold text-slate-800">
                     {{ formatScore(activeResult?.context_recall) }}
                  </span>
               </div>
               <div class="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                  <div 
                     class="h-full transition-all duration-500 ease-out"
                     :class="getScoreColorClass(activeResult?.context_recall)"
                     :style="{ width: determineBarWidth(activeResult?.context_recall) }"
                  ></div>
               </div>
            </div>

            <div class="space-y-1">
               <div class="flex justify-between items-center text-[11px]">
                  <span>faithfulness</span>
                  <span class="font-bold text-slate-800">
                     {{ formatScore(activeResult?.faithfulness) }}
                  </span>
               </div>
               <div class="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                  <div 
                     class="h-full transition-all duration-500 ease-out"
                     :class="getScoreColorClass(activeResult?.faithfulness)"
                     :style="{ width: determineBarWidth(activeResult?.faithfulness) }"
                  ></div>
               </div>
            </div>

            <div class="space-y-1">
               <div class="flex justify-between items-center text-[11px]">
                  <span>answer relevancy</span>
                  <span class="font-bold text-slate-800">
                     {{ formatScore(activeResult?.answer_relevance) }}
                  </span>
               </div>
               <div class="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                  <div 
                     class="h-full transition-all duration-500 ease-out"
                     :class="getScoreColorClass(activeResult?.answer_relevance)"
                     :style="{ width: determineBarWidth(activeResult?.answer_relevance) }"
                  ></div>
               </div>
            </div>
         </div>

         <div class="pt-3 border-t border-slate-200/60 flex justify-between items-center text-[11px]">
            <span>total tokens</span>
            <span class="font-bold text-slate-800">
               {{ activeResult?.token_count?.toLocaleString() ?? '—' }}
            </span>
         </div>
      </div>
   </div>
</template>