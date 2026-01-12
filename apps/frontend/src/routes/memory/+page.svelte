<script lang="ts">
	import * as Card from "$lib/components/ui/card";
	import * as Collapsible from "$lib/components/ui/collapsible";
	import { Separator } from "$lib/components/ui/separator/index.js";
	import { Button } from "$lib/components/ui/button";
	import { ScrollArea } from "$lib/components/ui/scroll-area/index.js";
	import { Input } from "$lib/components/ui/input";
	import { Trash2, FileDown, FileUp, Search, Send, Database, Brain, Plus, ChevronDown } from "lucide-svelte";

	import { socket, memories, searchQuery } from "../socketio";

	function getMemories() {
		socket.emit("get_memories", $searchQuery);
	}

	function clearShortTerm() {
		socket.emit("clear_short_term");
	}

	function deleteMemory(id: string) {
		socket.emit("delete_memory", id);
	}

	function importJSON() {
		socket.emit("import_json");
	}

	function exportJSON() {
		socket.emit("export_json");
	}

	let newMemory = "";
	function createMemory() {
		socket.emit("create_memory", newMemory);
		newMemory = "";
	}
</script>

<!-- Header -->
<div class="mb-8 relative group">
	<div class="absolute -inset-4 bg-gradient-to-r from-emerald-500/10 via-teal-500/5 to-cyan-500/10 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-all duration-700"></div>
	<div class="relative flex items-center gap-4">
		<div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/30 hover-scale">
			<Database class="w-7 h-7 text-white" />
		</div>
		<div>
			<h1 class="text-4xl font-bold gradient-text font-display">
				Memory
			</h1>
			<p class="text-slate-400 mt-1 flex items-center gap-2">
				<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
				Manage AI memories and knowledge base
			</p>
		</div>
	</div>
</div>

<div class="grid lg:grid-cols-2 gap-6">
	<!-- Memory Browser -->
	<div class="p-6 rounded-2xl glass border border-white/10 flex flex-col h-[700px]">
		<div class="flex items-center gap-3 mb-4">
			<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
				<Brain class="w-5 h-5 text-white" />
			</div>
			<div>
				<h3 class="font-semibold text-white">Memory Browser</h3>
				<p class="text-xs text-slate-500">Search and manage memories</p>
			</div>
		</div>

		<!-- Search Bar -->
		<div class="flex gap-2 mb-4">
			<Input 
				placeholder="Search memories..." 
				class="flex-1 bg-white/5 border-white/10 text-slate-300 placeholder:text-slate-600 rounded-xl focus:border-cyan-500/50"
				bind:value={$searchQuery}
			/>
			<Button on:click={getMemories} class="bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/30 rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/20">
				<Search class="w-4 h-4" />
			</Button>
		</div>

		<!-- Memory List -->
		<div class="flex-1 overflow-hidden rounded-xl glass-subtle border border-white/10">
			<ScrollArea class="h-full p-4">
				{#each $memories as memory}
					<div class="mb-3 p-3 rounded-xl glass-subtle border border-white/10 hover:border-cyan-500/30 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/10">
						<Collapsible.Root>
							<div class="flex items-start justify-between gap-2">
								<Collapsible.Trigger class="flex-1 text-left">
									<div class="flex items-center gap-2">
										<ChevronDown class="w-4 h-4 text-slate-500" />
										<p class="text-sm text-slate-300 line-clamp-2">{memory.document.slice(0, 80)}...</p>
									</div>
								</Collapsible.Trigger>
								<Button 
									variant="ghost" 
									size="icon" 
									on:click={() => {deleteMemory(memory.id)}}
									class="h-8 w-8 text-red-400 hover:text-red-300 hover:bg-red-500/20 rounded-lg transition-all duration-300"
								>
									<Trash2 class="w-4 h-4" />
								</Button>
							</div>
							<Collapsible.Content>
								<p class="mt-2 text-xs text-slate-400 pl-6">{memory.document.slice(80)}</p>
							</Collapsible.Content>
						</Collapsible.Root>
					</div>
				{/each}
				{#if $memories.length === 0}
					<div class="text-center py-8">
						<div class="w-16 h-16 mx-auto rounded-2xl bg-slate-800/50 flex items-center justify-center mb-4">
							<Database class="w-8 h-8 text-slate-600" />
						</div>
						<p class="text-sm text-slate-400 font-medium">No memories found</p>
						<p class="text-xs text-slate-600">Try searching or add new memories</p>
					</div>
				{/if}
			</ScrollArea>
		</div>

		<!-- Action Buttons -->
		<div class="flex gap-2 mt-4">
			<Button 
				variant="destructive" 
				on:click={clearShortTerm}
				class="flex-1 bg-red-500/20 border border-red-500/30 text-red-400 hover:bg-red-500/30 gap-2 rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-red-500/20"
			>
				<Trash2 class="w-4 h-4" />
				Clear Short-Term
			</Button>
			<Button 
				on:click={importJSON}
				class="bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/30 rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-emerald-500/20"
			>
				<FileDown class="w-4 h-4" />
			</Button>
			<Button 
				on:click={exportJSON}
				class="bg-blue-500/20 border border-blue-500/30 text-blue-400 hover:bg-blue-500/30 rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/20"
			>
				<FileUp class="w-4 h-4" />
			</Button>
		</div>
	</div>

	<!-- Add Memory -->
	<div class="space-y-6">
		<div class="p-6 rounded-2xl glass border border-white/10 hover-glow-purple transition-all duration-500">
			<div class="flex items-center gap-3 mb-4">
				<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-lg shadow-purple-500/30">
					<Plus class="w-5 h-5 text-white" />
				</div>
				<div>
					<h3 class="font-semibold text-white">Add Memory</h3>
					<p class="text-xs text-slate-500">Create new short-term memories</p>
				</div>
			</div>

			<Input 
				placeholder="Enter a new memory..." 
				class="w-full mb-4 bg-white/5 border-white/10 text-slate-300 placeholder:text-slate-600 rounded-xl focus:border-purple-500/50"
				bind:value={newMemory}
			/>

			<Button 
				on:click={createMemory}
				class="w-full bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 gap-2 rounded-xl shadow-lg shadow-purple-500/25 transition-all duration-300"
			>
				<Send class="w-4 h-4" />
				Add Memory
			</Button>
		</div>

		<!-- Memory Stats -->
		<div class="p-6 rounded-2xl glass border border-white/10">
			<h4 class="text-sm font-medium text-white mb-4">Memory Statistics</h4>
			<div class="grid grid-cols-2 gap-4">
				<div class="p-4 rounded-xl glass-subtle border border-white/10 text-center hover:border-cyan-500/30 transition-all duration-300 group">
					<p class="text-2xl font-bold text-cyan-400 font-display group-hover:scale-110 transition-transform">{$memories.length}</p>
					<p class="text-xs text-slate-500">Total Memories</p>
				</div>
				<div class="p-4 rounded-xl glass-subtle border border-white/10 text-center hover:border-purple-500/30 transition-all duration-300 group">
					<p class="text-2xl font-bold text-purple-400 group-hover:scale-110 transition-transform">Active</p>
					<p class="text-xs text-slate-500">Status</p>
				</div>
			</div>
		</div>

		<!-- Info -->
		<div class="p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/20">
			<p class="text-xs text-cyan-400">💡 Tip: Memories help the AI remember context and facts. Short-term memories are used during the current session.</p>
		</div>
	</div>
</div>
