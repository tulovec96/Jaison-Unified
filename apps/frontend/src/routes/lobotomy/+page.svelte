<script lang="ts">
	import * as Card from "$lib/components/ui/card";
	import { Textarea } from "$lib/components/ui/textarea";
	import { Button } from "$lib/components/ui/button";
	import { Send, Trash2, Brain, Sparkles, AlertTriangle } from "lucide-svelte";
	import { Input } from "$lib/components/ui/input";
	import { socket, lobotomy, customPrompt, priority } from "../socketio";

	function nukeHistory() {
		socket.emit("nuke_history");
	}

	function submitCustomPrompt() {
		socket.emit("set_custom_prompt", { "prompt": $customPrompt + "\n", "priority": $priority });
	}
</script>

<!-- Header -->
<div class="mb-8">
	<div class="flex items-center justify-between">
		<div class="flex items-center gap-4">
			<div class="relative group">
				<div class="absolute -inset-1 bg-gradient-to-r from-red-500 to-orange-500 rounded-xl blur-sm opacity-60 group-hover:opacity-100 transition-opacity" />
				<div class="relative w-14 h-14 rounded-xl bg-gradient-to-br from-red-500 to-orange-600 flex items-center justify-center shadow-lg">
					<Brain class="w-7 h-7 text-white" />
				</div>
			</div>
			<div>
				<h1 class="text-4xl font-bold gradient-text">Lobotomy</h1>
				<p class="text-slate-400 mt-1">View and manage AI context and memory</p>
			</div>
		</div>
	</div>
</div>

<div class="grid lg:grid-cols-2 gap-6">
	<!-- Current Context -->
	<div class="rounded-2xl glass border border-white/10 overflow-hidden flex flex-col h-[600px]">
		<div class="p-5 border-b border-white/5 flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-cyan-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
				<Brain class="w-5 h-5 text-white" />
			</div>
			<div>
				<h3 class="font-semibold text-white">Current Context</h3>
				<p class="text-xs text-slate-500">Active AI conversation history</p>
			</div>
		</div>
		
		<div class="flex-1 p-5 flex flex-col">
			<Textarea 
				bind:value={$lobotomy} 
				disabled 
				placeholder="No context loaded..." 
				class="resize-none flex-1 bg-white/5 border-white/10 text-slate-300 placeholder:text-slate-600 font-mono text-sm rounded-xl"
			/>
		</div>
		
		<div class="p-5 pt-0 space-y-3">
			<Button 
				variant="destructive" 
				on:click={nukeHistory}
				class="w-full bg-red-500/10 border border-red-500/30 text-red-400 hover:bg-red-500/20 gap-2 rounded-xl"
			>
				<Trash2 class="w-4 h-4" />
				Nuke History
			</Button>
			
			<div class="p-3 rounded-xl bg-red-500/10 border border-red-500/20">
				<div class="flex items-start gap-2">
					<AlertTriangle class="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
					<p class="text-xs text-red-400/80">Warning: This will permanently clear all conversation history and context.</p>
				</div>
			</div>
		</div>
	</div>

	<!-- Custom Prompt -->
	<div class="rounded-2xl glass border border-white/10 overflow-hidden flex flex-col h-[600px]">
		<div class="p-5 border-b border-white/5 flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-lg shadow-purple-500/30">
				<Sparkles class="w-5 h-5 text-white" />
			</div>
			<div>
				<h3 class="font-semibold text-white">Custom Prompt</h3>
				<p class="text-xs text-slate-500">Inject custom instructions into the AI</p>
			</div>
		</div>
		
		<div class="flex-1 p-5 flex flex-col">
			<Textarea 
				placeholder="Enter custom prompt to inject..." 
				class="resize-none flex-1 bg-white/5 border-white/10 text-slate-300 placeholder:text-slate-600 rounded-xl"
				bind:value={$customPrompt}
			/>
		</div>
		
		<div class="p-5 pt-0 space-y-4">
			<div class="flex items-center gap-4 p-4 rounded-xl bg-white/5 border border-white/10">
				<div class="flex items-center gap-2">
					<span class="text-sm text-slate-400">Priority:</span>
					<Input 
						placeholder="0" 
						class="w-20 bg-black/40 border-white/10 text-slate-300 text-center rounded-lg"
						bind:value={$priority}
					/>
				</div>
			<p class="text-xs text-slate-500 flex-1">Higher priority = placed earlier in context</p>
			</div>
			
			<Button 
				on:click={submitCustomPrompt}
				class="w-full bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 gap-2 rounded-xl shadow-lg shadow-purple-500/25"
			>
				<Send class="w-4 h-4" />
				Submit Prompt
			</Button>
		</div>
	</div>
</div>
