<script setup lang="ts">
import { ref, computed } from 'vue';
import { Send } from 'lucide-vue-next';
import QueryWheelPicker from './QueryWheelPicker.vue'; // Import der neuen Komponente

const predefinedQueries = [
   "Test query 1",
   "Test query 2",
   "Test query 3",
   "Test query 4",
   "Test query 5",
];

const activeQueryIndex = ref(2); // Steuert die Auswahl (Zwei-Wege-Binding)
const chatHistory = ref<{ id: number; sender: string; text: string }[]>([]);

// Berechnet den Text für das Read-Only Inputfeld
const currentQueryText = computed(() => predefinedQueries[activeQueryIndex.value]);

const sendQuery = () => {
   if (!currentQueryText.value) return;

   chatHistory.value.push({
      id: Date.now(),
      sender: 'user',
      text: currentQueryText.value
   });

   // Backend-Anbindung (FastAPI) würde hier triggern
};
</script>

<template>
   <div class="flex flex-col h-full justify-between">
      <h1 class="text-slate-800 text-center text-2xl font-semibold pt-3">Chat</h1>
      <div class="flex-1 overflow-y-auto p-6 space-y-4 max-w-3xl mx-auto w-full">
         <div v-for="msg in chatHistory" :key="msg.id"
            :class="['flex flex-col', msg.sender === 'user' ? 'items-end' : 'items-start']">
            <span class="text-[10px] text-slate-500 mb-1 px-1 capitalize">{{ msg.sender }}</span>
            <div
               :class="['p-4 rounded-xl text-sm max-w-xl shadow-md', msg.sender === 'user' ? 'bg-slate-200 text-slate-800' : 'bg-slate-800 text-slate-200']">
               {{ msg.text }}
            </div>
         </div>
      </div>

      <div class="p-6 space-y-4">
         <div class="max-w-3xl mx-auto w-full space-y-4">

            <QueryWheelPicker :queries="predefinedQueries" v-model="activeQueryIndex" />

            <div class="relative flex items-center bg-slate-300 border border-slate-200 rounded-xl px-4 py-3 shadow-xl">
               <input type="text" :value="currentQueryText" readonly
                  class="flex-1 bg-transparent border-none outline-none text-sm text-slate-500 font-medium select-none pr-12 truncate py-1" />
               <button @click="sendQuery"
                  class="absolute right-3 bg-blue-600 hover:bg-blue-500 text-white p-2 rounded-lg transition">
                  <Send class="w-4 h-4" />
               </button>
            </div>

         </div>
      </div>
   </div>
</template>