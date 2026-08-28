<script setup lang="ts">
import { RagPipeline, type PipelineSummary } from '@/types/backendTypes';
import { ref, computed } from 'vue';

const props = defineProps<{
   metrics: PipelineSummary[];
}>();

const activeTab = ref<RagPipeline>(RagPipeline.HYBRID);

const activeMetrics = computed(() => {
   const summary = props.metrics.find(m => m.pipeline_type === activeTab.value);

   return {
      precision: summary?.avg_context_precision ?? 0,
      recall: summary?.avg_context_recall ?? 0,
      faithfulness: summary?.avg_faithfulness ?? 0,
      relevancy: summary?.avg_answer_relevancy ?? 0,
      tokens: summary?.avg_token_count ?? 0,
   };
});

const formatScore = (val: number) => val.toFixed(2);

const getScoreColorClass = (score: number) => {
   if (score >= 0.8) return 'bg-emerald-500';
   if (score >= 0.5) return 'bg-amber-500';
   return 'bg-rose-500';
};

const determineBarWidth = (score: number) => {
   if (score >= 0) return `${score * 100}%`;
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
         <button v-for="pipeline in ([RagPipeline.HYBRID, RagPipeline.GRAPH, RagPipeline.FUSION] as const)"
            :key="pipeline" @click="activeTab = pipeline" :class="[
               'py-1 text-[10px] font-medium capitalize rounded transition duration-200',
               activeTab === pipeline
                  ? 'bg-white text-blue-600 shadow-sm font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
            ]">
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
                  <div class="h-full transition-all duration-500 ease-out"
                     :class="getScoreColorClass(activeMetrics.precision)"
                     :style="{ width: determineBarWidth(activeMetrics.precision) }"></div>
               </div>
            </div>

            <div class="space-y-1">
               <div class="flex justify-between items-center text-[11px]">
                  <span>avg. recall</span>
                  <span class="font-bold text-slate-800">{{ formatScore(activeMetrics.recall) }}</span>
               </div>
               <div class="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                  <div class="h-full transition-all duration-500 ease-out"
                     :class="getScoreColorClass(activeMetrics.recall)"
                     :style="{ width: determineBarWidth(activeMetrics.recall) }"></div>
               </div>
            </div>

            <div class="space-y-1">
               <div class="flex justify-between items-center text-[11px]">
                  <span>avg. faithfulness</span>
                  <span class="font-bold text-slate-800">{{ formatScore(activeMetrics.faithfulness) }}</span>
               </div>
               <div class="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                  <div class="h-full transition-all duration-500 ease-out"
                     :class="getScoreColorClass(activeMetrics.faithfulness)"
                     :style="{ width: determineBarWidth(activeMetrics.faithfulness) }"></div>
               </div>
            </div>

            <div class="space-y-1">
               <div class="flex justify-between items-center text-[11px]">
                  <span>avg. relevancy</span>
                  <span class="font-bold text-slate-800">{{ formatScore(activeMetrics.relevancy) }}</span>
               </div>
               <div class="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                  <div class="h-full transition-all duration-500 ease-out"
                     :class="getScoreColorClass(activeMetrics.relevancy)"
                     :style="{ width: determineBarWidth(activeMetrics.relevancy) }"></div>
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