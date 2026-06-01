<script setup lang="ts">
import { PanelLeft, ChevronUp } from 'lucide-vue-next';
</script>

<template>
   <div class="flex flex-col h-full">
      <div class="p-5 flex items-start justify-between space-x-4">

         <div class="flex-1">
            <h2 class="text-xs font-semibold uppercase tracking-wider text-slate-500">
               Volunteer Profiles
            </h2>
            <p class="text-[11px] text-slate-550 mt-1">
               Select a profile to inject metadata and skills into the RAG context.
            </p>
         </div>

         <PanelLeft class="w-5 h-5 shrink-0" />

      </div>

      <ul class="flex-1 overflow-y-auto p-3 space-y-1">
         <li
            class="flex flex-col p-3 rounded-lg bg-slate-200 border-l-4 border-blue-500 text-slate-500 cursor-pointer transition-all duration-150">
            <div class="flex justify-between items-center w-full">
               <span class="text-sm font-semibold">Profile 1</span>
               <div class="rounded hover:bg-slate-300">
                  <ChevronUp class=""></ChevronUp>
               </div>
            </div>
         </li>

         <li
            class="flex flex-col p-3 rounded-lg text-slate-400 hover:bg-slate-200 hover:text-slate-500 cursor-pointer transition-all duration-150 border-l-4 border-transparent">
            <div class="flex justify-between items-center w-full">
               <span class="text-sm font-medium">Profile 2</span>
               <div class="rounded hover:bg-slate-300">
                  <ChevronUp class=""></ChevronUp>
               </div>
            </div>
         </li>

         <li
            class="flex flex-col p-3 rounded-lg text-slate-400 hover:bg-slate-200 hover:text-slate-500 cursor-pointer transition-all duration-150 border-l-4 border-transparent">
            <div class="flex justify-between items-center w-full">
               <span class="text-sm font-medium">Profile 3</span>
               <div class="rounded hover:bg-slate-300">
                  <ChevronUp class=""></ChevronUp>
               </div>
            </div>
         </li>
      </ul>

      <div class="p-4 text-center">
         <div class="flex items-center justify-center space-x-2 text-xs text-slate-500">
            <span>Backend: Ministral 3 8B</span>
         </div>
      </div>
   </div>

</template>

<style scoped></style>