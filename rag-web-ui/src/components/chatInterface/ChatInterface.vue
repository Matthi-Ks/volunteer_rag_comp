<script setup lang="ts">
import { ref, computed } from 'vue';
import { Send, Loader2, MapPin, Calendar, FileText } from 'lucide-vue-next';
import QueryWheelPicker from '../QueryWheelPicker.vue'; // Import der neuen Komponente
import { QueryManager } from '@/ts/query_store.ts';
import predefQueries from '../../resources/query.json'
import type { EvaluationResult } from '@/types/evaluationResult.ts';
import type { Query, QueryOptions, RawQueryJson } from '@/types/query.ts';
import { search_and_evaluate } from '@/ts/rest.ts';
import { QuestionVariant, Region, TimeFrame } from '@/types/enums.ts';
import type Profile from '@/types/profile.ts';
import ContextModal from './ContextModal.vue';

interface PickerItem {
   rawTextTemplate: string
   displayText: string;
   variantType: QuestionVariant;
   parentQuery: RawQueryJson;
}

interface ChatMessage { 
   id: number;
   sender: string;
   text: string; 
   results?: EvaluationResult[]; 
   matchingResult?: EvaluationResult 
}

const props = defineProps<{
   queryOptions: QueryOptions;
   selectedProfile: Profile
}>();

const emit = defineEmits<{
   (e: 'received', value: EvaluationResult[]): void;
}>();

const qm: QueryManager = new QueryManager();
qm.loadFromJson(predefQueries)

const rawQueries = qm.getAllQueries();

const regionOptions = Object.entries(Region).map(([key, label]) => ({
   enumKey: key as keyof typeof Region,
   enumValue: label as Region,
}));

const timeframeOptions = Object.entries(TimeFrame).map(([key, label]) => ({
   enumKey: key as keyof typeof TimeFrame,
   enumValue: label as TimeFrame,
}));

const selectedRegion = ref<Region>(Region.REMOTE);
const selectedTimeframe = ref<TimeFrame>(TimeFrame.ASAP);

const isSelectionComplete = computed(() => selectedRegion.value !== null);

const formatQueryText = (text: string): string => {
   if (!text) return '';
   const loc = selectedRegion.value || '[location]';
   const tf = selectedTimeframe.value || '[timeframe]';

   return text
      .replace(/\[location\]/gi, loc)
      .replace(/\[timeframe\]/gi, tf);
};

const wheelPickerItems = computed<PickerItem[]>(() => {
   const items: PickerItem[] = [];
   rawQueries.forEach(q => {
      Object.entries(q.text_variants).forEach(([variantKey, textValue]) => {
         items.push({
            rawTextTemplate: textValue,
            displayText: formatQueryText(textValue),
            variantType: variantKey as QuestionVariant,
            parentQuery: q
         });
      });
   });
   return items;
});

const predefinedQueriesTextOnly = computed(() => wheelPickerItems.value.map(item => item.displayText));

const activeQueryIndex = ref(0);
const chatHistory = ref<ChatMessage[]>([]);
const isSending = ref(false);

const currentSelectedItem = computed<PickerItem | undefined>(() => wheelPickerItems.value[activeQueryIndex.value]);
const currentQueryText = computed(() => currentSelectedItem.value?.displayText || '');

const sendQuery = async () => {
   console.log(props.selectedProfile)
   const selectedItem = currentSelectedItem.value;
   if (!isSelectionComplete.value || !selectedItem || isSending.value) return;

   const activeRawQuery = selectedItem.parentQuery;

   const formattedTextVariants: Record<QuestionVariant, string> = {} as Record<QuestionVariant, string>;
   Object.entries(activeRawQuery.text_variants).forEach(([key, val]) => {
      formattedTextVariants[key as QuestionVariant] = formatQueryText(val);
   });

   const queryPayload: Query = {
      profile: props.selectedProfile,
      text_variants: formattedTextVariants,
      options: props.queryOptions,
      filter_values: {
         region: selectedRegion.value,
         timeFrame: selectedTimeframe.value
      }
   };

   chatHistory.value.push({
      id: Date.now(),
      sender: 'user',
      text: currentQueryText.value
   });

   isSending.value = true;

   try {
      const response: EvaluationResult[] = await search_and_evaluate(queryPayload);

      const matchingResult = response.find(res => res.question_variant === selectedItem.variantType) || response[0];
      console.log(matchingResult)

      chatHistory.value.push({
         id: Date.now() + 1,
         sender: 'system',
         text: matchingResult ? `${matchingResult.answer}` : "No matching response for this variant.",
         results: response,
         matchingResult: matchingResult
      });

      emit("received", response);

   } catch (error: any) {
      chatHistory.value.push({
         id: Date.now() + 1,
         sender: 'system',
         text: `Error processing query: ${error.message || 'Server connection failed.'}`
      });
   } finally {
      isSending.value = false;
   }
};

const isContextModalOpen = ref(false);
const usedContexts = ref<string[]>([]);

const openContextModal = (contexts: string[]) => {
   usedContexts.value = contexts;
   isContextModalOpen.value = true;
};

const closeContextModal = () => {
   isContextModalOpen.value = false;
   usedContexts.value = [];
};
</script>

<template>
   <div class="flex flex-col h-full justify-between">
      <h1 class="text-slate-800 text-center text-2xl font-semibold pt-3">Chat</h1>

      <div class="flex-1 overflow-y-auto p-6 space-y-4 max-w-4xl mx-auto w-full">
         <div v-for="msg in chatHistory" :key="msg.id"
            :class="['flex flex-col', msg.sender === 'user' ? 'items-end' : 'items-start']">
            <span class="text-[10px] text-slate-500 mb-1 px-1 capitalize">{{ msg.sender }}</span>
            <div
               :class="['p-4 rounded-xl text-sm max-w-xl shadow-md', msg.sender === 'user' ? 'bg-slate-200 text-slate-800' : 'bg-slate-800 text-slate-200']">

               <div>{{ msg.text }}</div>

               <div v-if="msg.sender === 'system' && msg.matchingResult"
                  class="pt-2 border-t border-slate-700/60 space-y-2.5">
                  <div v-if="msg.matchingResult.matching_skills?.length" class="flex flex-wrap gap-1.5 items-center">
                     <span v-for="(skill, idx) in msg.matchingResult.matching_skills" :key="idx"
                        class="px-2 py-0.5 text-[10px] font-medium rounded-full bg-blue-900/80 text-blue-200 border border-blue-700/50">
                        {{ skill }}
                     </span>
                  </div>

                  <div v-if="msg.matchingResult.context?.length" class="flex justify-end pt-1">
                     <button @click="openContextModal(msg.matchingResult.context)"
                        class="inline-flex items-center gap-1.5 text-[11px] font-medium text-slate-400 hover:text-white transition duration-150 bg-slate-700/50 hover:bg-slate-700 px-2.5 py-1 rounded-md border border-slate-600/40">
                        <FileText class="w-3.5 h-3.5" />
                        <span>View Context ({{ msg.matchingResult.context.length }})</span>
                     </button>
                  </div>
               </div>


            </div>
         </div>
      </div>

      <div class="p-6 space-y-4">
         <div class="max-w-4xl mx-auto w-full space-y-4">

            <QueryWheelPicker :queries="predefinedQueriesTextOnly" v-model="activeQueryIndex" />

            <div class="grid grid-cols-2 gap-4">

               <div
                  class="relative flex items-center bg-slate-100 border border-slate-200 rounded-xl px-3 py-2 shadow-md">
                  <MapPin class="w-4 h-4 text-slate-400 mr-2 shrink-0" />
                  <select v-model="selectedRegion"
                     class="w-full bg-transparent border-none outline-none text-xs text-slate-600 font-medium cursor-pointer">
                     <option value="" disabled selected>Select Location...</option>
                     <option v-for="loc in regionOptions" :key="loc.enumKey" :value="loc.enumValue">{{ loc.enumValue }}
                     </option>
                  </select>
               </div>

               <div
                  class="relative flex items-center bg-slate-100 border border-slate-200 rounded-xl px-3 py-2 shadow-md">
                  <Calendar class="w-4 h-4 text-slate-400 mr-2 shrink-0" />
                  <select v-model="selectedTimeframe"
                     class="w-full bg-transparent border-none outline-none text-xs text-slate-600 font-medium cursor-pointer">
                     <option :value="null" disabled selected>Select Timeframe...</option>
                     <option v-for="tf in timeframeOptions" :key="tf.enumKey" :value="tf.enumValue">{{ tf.enumValue }}
                     </option>
                  </select>
               </div>
            </div>

            <div class="relative flex items-center bg-slate-300 border border-slate-200 rounded-xl px-4 py-3 shadow-xl">
               <input type="text" :value="currentQueryText" readonly :class="['flex-1 bg-transparent border-none outline-none text-sm font-medium select-none pr-12 truncate py-1',
                  isSelectionComplete ? 'text-slate-800' : 'text-slate-400 italic']" />

               <button @click="sendQuery" :disabled="!isSelectionComplete || isSending"
                  class="absolute right-3 bg-blue-600 hover:bg-blue-500 text-white p-2 rounded-lg transition disabled:bg-slate-400 disabled:opacity-50 disabled:cursor-not-allowed">
                  <Loader2 v-if="isSending" class="w-4 h-4 animate-spin" />
                  <Send v-else class="w-4 h-4" />
               </button>
            </div>

         </div>
      </div>

      <ContextModal :is-open="isContextModalOpen" :contexts="usedContexts" @close="closeContextModal" />

   </div>
</template>