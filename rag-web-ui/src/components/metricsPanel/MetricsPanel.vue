<script setup lang="ts">
import type { EvaluationResult, PipelineSummary } from '@/types/backendTypes.ts';
import QueryMetricsPanel from './QueryMetricsPanel.vue';
import PipelineMetricsPanel from './PipelineMetricsPanel.vue';
import { ref, watch } from 'vue';
import { get_pipeline_summaries } from '@/ts/rest.ts';


const props = defineProps<{
   results: EvaluationResult[] | null
}>();

const metrics = ref<PipelineSummary[]>([]);

watch(
   () => props.results,
   async () => {
      metrics.value = await get_pipeline_summaries();
   },
   { immediate: true }
);
</script>

<template>
   <div class="text-xs p-2 space-y-8">
      <QueryMetricsPanel :results="results" />

      <hr class="border-slate-200/80" />

      <PipelineMetricsPanel :metrics="metrics" />
   </div>
</template>