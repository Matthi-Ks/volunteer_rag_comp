<script setup lang="ts">
import { RagPipeline } from '@/types/backendTypes';
import { ref, computed } from 'vue';

const activeTab = ref<RagPipeline>(RagPipeline.HYBRID);

const mockOverallMetrics = {
   hybrid: {
      precision: 0.76,
      recall: 0.81,
      faithfulness: 0.79,
      relevancy: 0.84,
      tokens: 425100
   },
   fusion: {
      precision: 0.88,
      recall: 0.89,
      faithfulness: 0.91,
      relevancy: 0.87,
      tokens: 894000
   },
   graph: {
      precision: 0.82,
      recall: 0.93,
      faithfulness: 0.71,
      relevancy: 0.80,
      tokens: 1542000
   }
};

const activeMetrics = computed(() => mockOverallMetrics[activeTab.value]);

const formatScore = (val: number) => val.toFixed(2);

const getScoreColorClass = (score: number) => {
   if (score >= 0.8) return 'bg-emerald-500';
   if (score >= 0.5) return 'bg-amber-500';
   return 'bg-rose-500';
};

const determineBarWidth = (score: number) => {
    if (score >= 0) return `${score*100}%`;
    return '0%';
};
</script>

<template>
   <div class="space-y-3">
      <div class="flex items-center justify-between">
         <h2 class="font-semibold uppercase tracking-wider text-slate-500 text-xs">
            Overall Metrics
         </h2>
         <span class="text-[9px] text-slate-400 font-mono italic">
            Aggregated Runs
         </span>
      </div>

      <div class="grid grid-cols-3 gap-1 bg-slate-200/60 p-1 rounded-lg">
         <button 
            v-for="pipeline in ([RagPipeline.HYBRID, RagPipeline.GRAPH, RagPipeline.FUSION] as const)" 
            :key="pipeline"
            @click="activeTab = pipeline"
            :class="[
               'py-1 text-[10px] font-medium capitalize rounded transition duration-200',
               activeTab === pipeline
                  ? 'bg-white text-blue-600 shadow-sm font-semibold' 
                  : 'text-slate-600 hover:text-slate-900'
            ]"
         >
            {{ pipeline }}
         </button>
      </div>

      <div class="font-mono text-slate-600 space-y-4 pt-1">
         <div class="space-y-3">
            <div class="space-y-1">
               <div class="flex justify-between items-center text-[11px]">
                  <span>avg. precision</span>
                  <span class="font-bold text-slate-800">{{ formatScore(activeMetrics.precision) }}</span>
               </div>
               <div class="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                  <div 
                     class="h-full transition-all duration-500 ease-out"
                     :class="getScoreColorClass(activeMetrics.precision)"
                     :style="{ width: determineBarWidth(activeMetrics.precision) }"
                  ></div>
               </div>
            </div>

            <div class="space-y-1">
               <div class="flex justify-between items-center text-[11px]">
                  <span>avg. recall</span>
                  <span class="font-bold text-slate-800">{{ formatScore(activeMetrics.recall) }}</span>
               </div>
               <div class="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                  <div 
                     class="h-full transition-all duration-500 ease-out"
                     :class="getScoreColorClass(activeMetrics.recall)"
                     :style="{ width: determineBarWidth(activeMetrics.recall) }"
                  ></div>
               </div>
            </div>

            <div class="space-y-1">
               <div class="flex justify-between items-center text-[11px]">
                  <span>avg. faithfulness</span>
                  <span class="font-bold text-slate-800">{{ formatScore(activeMetrics.faithfulness) }}</span>
               </div>
               <div class="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                  <div 
                     class="h-full transition-all duration-500 ease-out"
                     :class="getScoreColorClass(activeMetrics.faithfulness)"
                     :style="{ width: determineBarWidth(activeMetrics.faithfulness) }"
                  ></div>
               </div>
            </div>

            <div class="space-y-1">
               <div class="flex justify-between items-center text-[11px]">
                  <span>avg. relevancy</span>
                  <span class="font-bold text-slate-800">{{ formatScore(activeMetrics.relevancy) }}</span>
               </div>
               <div class="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                  <div 
                     class="h-full transition-all duration-500 ease-out"
                     :class="getScoreColorClass(activeMetrics.relevancy)"
                     :style="{ width: determineBarWidth(activeMetrics.relevancy) }"
                  ></div>
               </div>
            </div>
         </div>

         <div class="pt-3 border-t border-slate-200/60 flex justify-between items-center text-[11px]">
            <span>accumulated tokens</span>
            <span class="font-bold text-slate-800">{{ activeMetrics.tokens.toLocaleString() }}</span>
         </div>
      </div>
   </div>
</template>