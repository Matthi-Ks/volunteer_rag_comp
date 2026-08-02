<script setup lang="ts">
import { PanelLeft, ChevronUp } from 'lucide-vue-next';
import profilesData from '../resources/profile.json';
import { onMounted, ref } from 'vue';
import type Profile from '@/types/profile';

const profiles = ref<Profile[]>(profilesData);

const selectedProfileId = ref<number | null>(profiles.value[0]?.id ?? null);
const expandedProfileId = ref<number | null>(null);

const emit = defineEmits<{
   (e: 'selectProfile', profile: Profile): void
}>();

onMounted(() => {
   if (profiles.value.length > 0){
      emit('selectProfile', profiles.value[0] as Profile)
   }
});

const handleSelectProfile = (profile: Profile) => {
   selectedProfileId.value = profile.id;
   emit('selectProfile', profile);
};

const toggleDetails = (id: number, event: Event) => {
   event.stopPropagation();
   expandedProfileId.value = expandedProfileId.value === id ? null : id;
};

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
         <li v-for="profile in profiles" :key="profile.id" @click="handleSelectProfile(profile)"
            class="flex flex-col p-3 rounded-lg cursor-pointer transition-all duration-150 border-l-4" :class="[
               selectedProfileId === profile.id
                  ? 'bg-slate-200 border-blue-500 text-slate-700 shadow-sm'
                  : 'border-transparent text-slate-400 hover:bg-slate-200 hover:text-slate-500'
            ]">

            <div class="flex justify-between items-center w-full">
               <span class="text-sm font-semibold">
                  Profile {{ profile.id }}
               </span>
               
               <button
                  type="button"
                  @click="toggleDetails(profile.id, $event)"
                  class="p-1 rounded hover:bg-slate-300/60 transition-colors"
                  :aria-label="`Toggle Profile ${profile.id} details`"
               >
                  <ChevronUp
                     class="w-4 h-4 transition-transform duration-200"
                     :class="{ 'rotate-180': expandedProfileId === profile.id }"
                  />
               </button>
            </div>

            <div
               v-if="expandedProfileId === profile.id"
               class="mt-3 pt-3 border-t border-slate-300/60 text-xs text-slate-600 space-y-3 cursor-default"
               @click.stopPropagation
            >
               <div>
                  <h4 class="font-semibold text-slate-700 mb-1">Biography</h4>
                  <p class="leading-relaxed text-[11px]">
                     {{ profile.biography }}
                  </p>
               </div>

               <div>
                  <h4 class="font-semibold text-slate-700 mb-1.5">Skills</h4>
                  <div class="flex flex-wrap gap-1">
                     <span
                        v-for="(skill, index) in profile.esco_skills"
                        :key="index"
                        class="px-2 py-0.5 rounded-md bg-slate-300/70 text-slate-700 text-[10px] font-medium"
                     >
                        {{ skill }}
                     </span>
                  </div>
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