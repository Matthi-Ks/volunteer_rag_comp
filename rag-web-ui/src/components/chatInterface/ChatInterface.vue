<script setup lang="ts">
import { ref, computed } from 'vue';
import { Send, Loader2, MapPin, Calendar, FileText } from 'lucide-vue-next';
import QueryWheelPicker from './QueryWheelPicker.vue'; // Import der neuen Komponente
import { QueryManager } from '@/ts/query_store.ts';
import predefQueries from '../../resources/query.json'
import { search_and_evaluate } from '@/ts/rest.ts';
import ContextModal from './ContextModal.vue';
import ChatMessageBubble from './ChatMessageBubble.vue';
import type { PickerItem, ChatMessage, RawQueryJson } from '@/types/webAppTypes.ts';
import { type QueryOptions, type Profile, type EvaluationResult, QuestionVariant, type Query } from '@/types/backendTypes.ts';
import { Region, TimeFrame } from '@/types/backendTypes.ts';

const props = defineProps<{
   queryOptions: QueryOptions;
   selectedProfile: Profile
}>();

const emit = defineEmits<{
   (e: 'received', value: EvaluationResult[]): void;
}>();

const qm: QueryManager = new QueryManager();
qm.loadFromJson(predefQueries)

const rawQueries: RawQueryJson[] = qm.getAllQueries();

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

const activeQueryIndex = ref(0);
const chatHistory = ref<ChatMessage[]>([]);
const isSending = ref(false);

const isContextModalOpen = ref(false);
const usedContexts = ref<string[]>([]);

const variantOrder: QuestionVariant[] = [
   QuestionVariant.NORMAL,
   QuestionVariant.ABSTRACT,
   QuestionVariant.DETAILED
];

const formattedQueries = computed(() => {
   const loc = selectedRegion.value || '[location]';
   const tf = selectedTimeframe.value || '[timeframe]';

   return rawQueries.map(q => {
      const formattedVariants: Record<QuestionVariant, string> = {} as Record<QuestionVariant, string>;

      Object.entries(q.text_variants).forEach(([variantKey, textValue]) => {
         formattedVariants[variantKey as QuestionVariant] = textValue
            .replace(/\[location\]/gi, loc)
            .replace(/\[timeframe\]/gi, tf);
      });

      return {
         id: q.id,
         normalDisplayText: formattedVariants[QuestionVariant.NORMAL] || '',
         formattedVariants,
         rawQuery: q
      };
   })
});

const wheelPickerTexts = computed(() => formattedQueries.value.map(q => q.normalDisplayText));
const selectedQueryObj = computed(() => formattedQueries.value[activeQueryIndex.value]);
const selectedQueryText = computed(() => formattedQueries.value[activeQueryIndex.value]?.normalDisplayText);

const cycleMessageVariant = (msg: ChatMessage, direction: 'prev' | 'next') => {
   const maxIndex = variantOrder.length - 1;
   let currentIndex = msg.activeVariantIndex ?? 0;

   if (direction === 'next') {
      currentIndex = currentIndex >= maxIndex ? 0 : currentIndex + 1;
   } else {
      currentIndex = currentIndex <= 0 ? maxIndex : currentIndex - 1;
   }

   msg.activeVariantIndex = currentIndex;
   const activeVariant = variantOrder[currentIndex];

   if (msg.sender === 'user' && msg.textVariants) {
      msg.text = msg.textVariants[activeVariant!] || msg.text;
   } else if (msg.sender === 'system' && msg.results) {
      const match = msg.results.find(r => r.question_variant === activeVariant) || msg.results[0];
      msg.matchingResult = match;
      msg.text = match ? `${match.answer}` : "No matching response for this variant.";
   }
};

const sendQuery = async () => {
   const selected = selectedQueryObj.value;
   if (!isSelectionComplete.value || !selected || isSending.value) return;

   console.log(selectedRegion.value, selectedTimeframe.value)

   const queryPayload: Query = {
      profile: props.selectedProfile,
      query_id: selected.id,
      text_variants: selected.formattedVariants,
      options: props.queryOptions,
      filter_values: {
         region: selectedRegion.value,
         timeFrame: selectedTimeframe.value
      }
   };

   chatHistory.value.push({
      id: Date.now(),
      sender: 'user',
      text: selected.normalDisplayText,
      textVariants: selected.formattedVariants,
      activeVariantIndex: 0
   });

   isSending.value = true;

   try {
      const response: EvaluationResult[] = await search_and_evaluate(queryPayload);
      const matchingResult = response.find(res => res.question_variant === QuestionVariant.NORMAL) || response[0];

      chatHistory.value.push({
         id: Date.now() + 1,
         sender: 'system',
         text: matchingResult ? `${matchingResult.answer}` : "No matching response for this variant.",
         results: response,
         matchingResult: matchingResult,
         activeVariantIndex: 0
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

      <!-- Chat Stream -->
      <div class="flex-1 overflow-y-auto p-6 space-y-4 max-w-4xl mx-auto w-full">
         <ChatMessageBubble v-for="msg in chatHistory" :key="msg.id" :message="msg" :variant-order="variantOrder"
            @cycle-variant="(direction) => cycleMessageVariant(msg, direction)" @open-context="openContextModal" />
      </div>

      <!-- Controls Panel -->
      <div class="p-6 space-y-4">
         <div class="max-w-4xl mx-auto w-full space-y-4">

            <QueryWheelPicker :queries="wheelPickerTexts" v-model="activeQueryIndex" />

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
               <input type="text" :value="selectedQueryText" readonly :class="['flex-1 bg-transparent border-none outline-none text-sm font-medium select-none pr-12 truncate py-1',
                  isSelectionComplete ? 'text-slate-800' : 'text-slate-400 italic']" />

               <button @click="sendQuery" :disabled="!isSelectionComplete || isSending"
                  class="absolute right-3 bg-blue-600 hover:bg-blue-500 text-white p-2 rounded-lg transition disabled:bg-slate-400 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer">
                  <Loader2 v-if="isSending" class="w-4 h-4 animate-spin" />
                  <Send v-else class="w-4 h-4" />
               </button>
            </div>

         </div>
      </div>

      <ContextModal :is-open="isContextModalOpen" :contexts="usedContexts" @close="closeContextModal" />

   </div>
</template>