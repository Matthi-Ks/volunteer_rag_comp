<script setup lang="ts">
import { ref, watch, onMounted, nextTick, onBeforeUpdate } from 'vue';
import { ChevronUp, ChevronDown } from 'lucide-vue-next';

const props = defineProps<{
   queries: string[];
   modelValue: number;
}>();

const emit = defineEmits<{
   (e: 'update:modelValue', index: number): void;
   (e: 'change', queryText: string): void;
}>();

const itemRefs = ref<HTMLElement[]>([]);
const translateY = ref(0);

onBeforeUpdate(() => {
   itemRefs.value = [];
});

const updateSelection = (newIndex: number) => {
   if (newIndex >= 0 && newIndex < props.queries.length) {
      emit('update:modelValue', newIndex);
      emit('change', props.queries[newIndex]);
   }
};

const calculateOffset = () => {
   nextTick(() => {
      const activeElement = itemRefs.value[props.modelValue];
      if (!activeElement) return;

      const itemOffsetTop = activeElement.offsetTop;
      const itemHalfHeight = activeElement.clientHeight / 2;
      const containerHalfHeight = 176 / 2; // Matching the h-44 container

      translateY.value = containerHalfHeight - (itemOffsetTop + itemHalfHeight);
   });
};

// Calculate 3D styles based on distance from selected index
const get3DStyles = (idx: number) => {
   const diff = idx - props.modelValue;
   
   // We limit the visible calculation to immediate neighbors for natural roll-off
   if (Math.abs(diff) > 2) {
      return {
         opacity: 0,
         transform: `rotateX(${diff > 0 ? 90 : -90}deg) translateZ(-40px) scale(0.85)`,
         pointerEvents: 'none' as const
      };
   }

   // 1. Rotation: Curving around the cylinder (e.g., 25 degrees per step)
   const angle = diff * 25; 
   
   // 2. Depth: Pushing non-selected items back along the Z-axis
   const zTranslation = Math.abs(diff) * -15; 

   // 3. Scale: Slight reduction in size as it rolls back
   const scale = 1 - (Math.abs(diff) * 0.05);

   // 4. Opacity fade
   const opacity = Math.max(0, 1 - (Math.abs(diff) * 0.55));

   return {
      opacity: opacity,
      transform: `rotateX(${angle}deg) translateZ(${zTranslation}px) scale(${scale})`,
      zIndex: 10 - Math.abs(diff)
   };
};

watch(() => props.modelValue, calculateOffset);
watch(() => props.queries, () => nextTick(calculateOffset), { deep: true });

onMounted(() => {
   calculateOffset();
   window.addEventListener('resize', calculateOffset);
});
</script>

<template>
   <div class="relative flex items-center justify-center p-2 h-44 overflow-hidden rounded-2xl border border-slate-200 bg-slate-100/50 shadow-inner w-full custom-perspective">
      
      <!-- Arrow Controls -->
      <div class="absolute left-4 flex flex-col space-y-2 z-20">
         <button @click="updateSelection(props.modelValue - 1)" :disabled="props.modelValue === 0"
            class="p-1.5 rounded bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-20 disabled:cursor-not-allowed transition duration-200">
            <ChevronUp class="w-4 h-4" />
         </button>
         <button @click="updateSelection(props.modelValue + 1)" :disabled="props.modelValue === queries.length - 1"
            class="p-1.5 rounded bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-20 disabled:cursor-not-allowed transition duration-200">
            <ChevronDown class="w-4 h-4" />
         </button>
      </div>

      <!-- Masked Container Window -->
      <div class="w-full h-full relative overflow-hidden select-none px-16 custom-perspective">
         <!-- Scroll Track -->
         <div 
            class="absolute left-0 right-0 transition-transform duration-500 cubic-bezier will-change-transform 3D-container"
            :style="{ transform: `translateY(${translateY}px)` }"
         >
            <div 
               v-for="(query, idx) in queries" 
               :key="idx" 
               :ref="(el) => { if (el) itemRefs[idx] = el as HTMLElement }"
               @click="updateSelection(idx)" 
               :class="[
                  'text-xs py-2 px-4 flex items-center justify-center cursor-pointer transition-all duration-500 ease-out leading-relaxed text-center absolute left-0 right-0',
                  idx === props.modelValue 
                     ? 'text-blue-600 font-semibold' 
                     : 'text-slate-400 font-normal'
               ]"
               :style="{
                  ...get3DStyles(idx),
                  top: `${idx * 40}px` /* Fixed layout positioning anchor to stack them neatly */
               }"
            >
               <!-- Custom text wrapper using data-text attribute to prevent bold width jumping -->
               <span 
                  class="max-w-xl inline-flex flex-col items-center justify-center text-center select-none dynamic-text"
                  :data-text="query"
               >
                  {{ query }}
               </span>
            </div>
         </div>
      </div>
   </div>
</template>

<style scoped>
.cubic-bezier {
   transition-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
}

/* 3D Context Setup */
.custom-perspective {
   perspective: 1000px;
}

.container-3d {
   transform-style: preserve-3d;
   height: 100%;
}

/* 
  Creates a hidden bold pseudo-element. 
  This forces the layout engine to calculate block width and height based on the 
  bold version, preventing wrapping differences when changing states!
*/
.dynamic-text::after {
   content: attr(data-text);
   content: attr(data-text) / "";
   font-weight: 600; /* Matches 'font-semibold' */
   height: 0;
   visibility: hidden;
   overflow: hidden;
   user-select: none;
   pointer-events: none;
   display: block;
}
</style>