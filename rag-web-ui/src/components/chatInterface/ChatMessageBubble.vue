<script setup lang="ts">
import { ChevronLeft, ChevronRight, FileText } from 'lucide-vue-next';
import type { QuestionVariant } from '@/types/backendTypes';
import type { ChatMessage } from '@/types/webAppTypes';

const props = defineProps<{
    message: ChatMessage;
    variantOrder: QuestionVariant[];
}>();

const emit = defineEmits<{
    (e: 'cycleVariant', direction: 'prev' | 'next'): void;
    (e: 'openContext', contexts: string[]): void;
}>();

</script>
<template>
    <div :class="['flex flex-col', message.sender === 'user' ? 'items-end' : 'items-start']">
        <span class="text-[10px] text-slate-500 mb-1 px-1 capitalize">{{ message.sender }}</span>

        <div :class="[
            'p-4 rounded-xl text-sm max-w-xl shadow-md space-y-3 relative group',
            message.sender === 'user' ? 'bg-slate-200 text-slate-800' : 'bg-slate-800 text-slate-200'
        ]">
            <div v-if="(message.textVariants || message.results)"
                class="flex items-center justify-between pb-1">
                <span class="text-[10px] uppercase font-mono font-bold tracking-wider opacity-60">
                    {{ variantOrder[message.activeVariantIndex ?? 0] }}
                </span>

                <div class="flex items-center gap-1 bg-black/10 dark:bg-white/10 px-1.5 py-0.5 rounded-md">
                    <button @click="emit('cycleVariant', 'prev')"
                        class="p-0.5 hover:bg-black/10 dark:hover:bg-white/20 rounded transition cursor-pointer"
                        title="Previous variant">
                        <ChevronLeft class="w-3.5 h-3.5" />
                    </button>
                    <button @click="emit('cycleVariant', 'next')"
                        class="p-0.5 hover:bg-black/10 dark:hover:bg-white/20 rounded transition cursor-pointer"
                        title="Next variant">
                        <ChevronRight class="w-3.5 h-3.5" />
                    </button>
                </div>
            </div>

            <!-- Body Row: Message Text -->
            <div class="font-sans leading-relaxed">
                {{ message.text }}
            </div>
            <!-- Footer Metadata (System Messages Only) -->
            <div v-if="message.sender === 'system' && message.matchingResult"
                class="pt-2 border-t border-slate-700/60 space-y-2.5">
                <!-- Matching Skills -->
                <div v-if="message.matchingResult.matching_skills?.length" class="flex flex-wrap gap-1.5 items-center">
                    <span v-for="(skill, idx) in message.matchingResult.matching_skills" :key="idx"
                        class="px-2 py-0.5 text-[10px] font-medium rounded-full bg-blue-900/80 text-blue-200 border border-blue-700/50">
                        {{ skill }}
                    </span>
                </div>

                <!-- Context Inspector Trigger -->
                <div v-if="message.matchingResult.context?.length" class="flex justify-end pt-1">
                    <button @click="emit('openContext', message.matchingResult.context)"
                        class="inline-flex items-center gap-1.5 text-[11px] font-medium text-slate-400 hover:text-white transition duration-150 bg-slate-700/50 hover:bg-slate-700 px-2.5 py-1 rounded-md border border-slate-600/40 cursor-pointer">
                        <FileText class="w-3.5 h-3.5" />
                        <span>View Context ({{ message.matchingResult.context.length }})</span>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>