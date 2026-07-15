<script setup lang="ts">
import { InformationTier, RagPipeline } from '@/types/enums';
import type { QueryOptions } from '@/types/query';
import { computed, ref, watch } from 'vue';


const emit = defineEmits<{
   (e: 'update', value: QueryOptions): void;
}>();

const selectedPipeline = ref<RagPipeline>(RagPipeline.HYBRID);
const useESCOData = ref<boolean>(false);
const useTitleOnly = ref<boolean>(false);
const useHardFilter = ref<boolean>(true);

const queryOptions = computed<QueryOptions>(() => ({
   pipeline: selectedPipeline.value,
   informationTier: useTitleOnly.value 
      ? (useESCOData.value ? InformationTier.TITLE_ONLY: InformationTier.TITLE_SOFTSKILL) 
      : (useESCOData.value ? InformationTier.TITLE_SOFTSKILL: InformationTier.TITLE_DESC_SOFTSKILL),
   useMetadataFilter: useHardFilter.value
}));

watch(queryOptions, (newVal) => {
   emit('update', newVal);
}, { deep: true });

</script>
<template>
   <div class="text-xs p-2 space-y-6">

      <div class="space-y-2">
         <h2 class="font-semibold uppercase tracking-wider text-slate-500">
            Pipeline Config
         </h2>

         <div class="font-mono text-slate-500 pt-4">
            <div class="flex flex-col space-y-1.5">
               <label for="rag-strategy">rag strategy</label>

               <select
                  id="rag-strategy"
                  v-model="selectedPipeline"
                  class="w-full bg-slate-200 border border-slate-100 rounded px-2.5 py-1.5 outline-none focus:border-blue-500 cursor-pointer transition">
                  <option :value='RagPipeline.FUSION'>Fusion RAG</option>
                  <option :value='RagPipeline.GRAPH'>GraphRAG</option>
                  <option :value='RagPipeline.HYBRID'>Hybrid Keyword/Vector</option>
               </select>
            </div>

            <div class="flex items-center justify-between pt-2">
               <div class="flex flex-col pr-4">
                  <span>use ESCO labeled data</span>
               </div>

               <label class="relative inline-flex items-center cursor-pointer select-none">
                  <input type="checkbox" v-model="useESCOData" class="sr-only peer" />
                  <div
                     class="w-7 h-4 bg-slate-300 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-blue-600 dark:peer-checked:bg-blue-500 border border-slate-200">
                  </div>
               </label>
            </div>

            <div class="flex items-center justify-between pt-2">
               <div class="flex flex-col pr-4">
                  <span>use activity title only</span>
               </div>

               <label class="relative inline-flex items-center cursor-pointer select-none">
                  <input type="checkbox" v-model="useTitleOnly" class="sr-only peer" />
                  <div
                     class="w-7 h-4 bg-slate-300 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-blue-600 dark:peer-checked:bg-blue-500 border border-slate-200">
                  </div>
               </label>
            </div>

            <div class="flex items-center justify-between pt-2">
            <div class="flex flex-col pr-4">
               <span>use hard metadata filter</span>
            </div>

            <label class="relative inline-flex items-center cursor-pointer select-none">
               <input type="checkbox" v-model="useHardFilter" class="sr-only peer" checked />
               <div
                  class="w-7 h-4 bg-slate-300 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-blue-600 dark:peer-checked:bg-blue-500 border border-slate-200">
               </div>
            </label>
         </div>

         </div>
      </div>

   </div>
</template>

<style scoped></style>