<script setupt lang="ts"></script>

<template>
   <div class="text-xs p-2 space-y-6">

      <div class="space-y-2">
         <h2 class="font-semibold uppercase tracking-wider text-slate-500">
            RAGAS BENCHMARK
         </h2>

         <div class="font-mono text-slate-500 pt-4">
            <div class="flex justify-between items-center pb-2">
               <span>context precision</span>
               <span class="font-bold">...</span>
            </div>

            <div class="flex justify-between items-center pb-2">
               <span>context recall</span>
               <span class="font-bold">...</span>
            </div>

            <div class="flex justify-between items-center pb-2">
               <span>faithfulness</span>
               <span class="font-bold">...</span>
            </div>

            <div class="flex justify-between items-center pb-2">
               <span>answer relevancy</span>
               <span class="font-bold">...</span>
            </div>
         </div>
      </div>

      <div class="space-y-1.5">
         <h2 class="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Usage Metrics
         </h2>

         <div class="font-mono text-slate-500 pt-4">
            <div class="flex justify-between items-center pb-2">
               <span>total tokens</span>
               <span class="font-bold">...</span>
            </div>
         </div>
      </div>

   </div>
</template>

<style scoped></style>