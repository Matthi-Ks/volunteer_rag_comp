<script setup lang="ts">
import { ref } from 'vue';
import ChatInterface from './components/chatInterface/ChatInterface.vue';
import ControlPanel from './components/ControlPanel.vue';
import MetricsPanel from './components/metricsPanel/MetricsPanel.vue';
import ProfileSelector from './components/ProfileSelector.vue';
import { InformationTier, RagPipeline, type EvaluationResult, type Profile, type QueryOptions } from './types/backendTypes.ts';
import profilesData from './resources/profile.json';

const activeOptions = ref<QueryOptions>({
    pipeline: RagPipeline.HYBRID,
    informationTier: InformationTier.MaT_TITLE_DESC,
    useMetadataFilter: true,
    useESCOSkills: false
});

const receivedResults = ref<EvaluationResult[] | null>(null)

const selectedProfile = ref<Profile>(profilesData[0] as Profile)

const handleOptionsUpdate = (options: QueryOptions) => {
   activeOptions.value = options;
};

const handleRecevedResults = (results: EvaluationResult[]) => {
    receivedResults.value = results;
}

const handleProfileSelection = (profile: Profile) => {
    selectedProfile.value = profile
};
</script>

<template>
  <div class="flex h-screen w-screen overflow-hidden font-sans">
    <aside class="w-64 flex flex-col border-r border-slate-300">
      <ProfileSelector @select-profile="handleProfileSelection"></ProfileSelector>
    </aside>
    <main class="flex-1 flex flex-col justify-between relative bg-slate-100">
      <ChatInterface :selected-profile="selectedProfile" :query-options="activeOptions" @received="handleRecevedResults" />
    </main>
    <section class="w-80 flex flex-col border-l border-slate-300 overflow-y-auto">

      <div class="flex-1 overflow-y-auto p-4 border-b border-slate-200 dark:border-slate-800">
        <MetricsPanel :results="receivedResults" />
      </div>

      <div class="shrink-0 p-4">
        <ControlPanel @update="handleOptionsUpdate"/>
      </div>
    </section>
  </div>

</template>

<style scoped></style>
