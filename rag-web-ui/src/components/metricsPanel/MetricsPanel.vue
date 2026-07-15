<script setup lang="ts">
import type { EvaluationResult } from '@/types/evaluationResult';
import QueryMetricsPanel from './QueryMetricsPanel.vue';
import PipelineMetricsPanel from './PipelineMetricsPanel.vue';


defineProps<{
   results: EvaluationResult[] | null
}>();
</script>

<template>
   <div class="text-xs p-2 space-y-8">
      <QueryMetricsPanel :results="results" />

      <hr class="border-slate-200/80" />

      <PipelineMetricsPanel />
   </div>
</template>