<script lang="ts">
	import * as Card from "$lib/components/ui/card";
	import { Textarea } from "$lib/components/ui/textarea";
	import { Button } from "$lib/components/ui/button";
	import { Send, Shield, AlertTriangle, Ban } from "lucide-svelte";

	import { socket, blacklist } from "../socketio";

	function submitBlacklist() {
		let data = $blacklist.split("\n")
		socket.emit("set_blacklist", data);
	}
</script>

<!-- Header -->
<div class="mb-8 relative group">
	<div class="absolute -inset-4 bg-gradient-to-r from-amber-500/10 via-orange-500/5 to-red-500/10 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-all duration-700"></div>
	<div class="relative flex items-center gap-4">
		<div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-amber-500/30 hover-scale">
			<Shield class="w-7 h-7 text-white" />
		</div>
		<div>
			<h1 class="text-4xl font-bold gradient-text font-display">
				Moderation
			</h1>
			<p class="text-slate-400 mt-1 flex items-center gap-2">
				<span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
				Configure content filtering and word blacklists
			</p>
		</div>
	</div>
</div>

<div class="grid lg:grid-cols-2 gap-6">
	<!-- Blacklist Editor -->
	<div class="p-6 rounded-2xl glass border border-white/10 flex flex-col h-[600px] hover-glow-amber transition-all duration-500">
		<div class="flex items-center gap-3 mb-4">
			<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-red-500 to-orange-600 flex items-center justify-center shadow-lg shadow-red-500/30">
				<Ban class="w-5 h-5 text-white" />
			</div>
			<div>
				<h3 class="font-semibold text-white">Word Blacklist</h3>
				<p class="text-xs text-slate-500">One word or phrase per line</p>
			</div>
		</div>
		
		<div class="flex-1 mb-4">
			<Textarea 
				placeholder="Enter blacklisted words (one per line)..." 
				class="resize-none h-full bg-white/5 border-white/10 text-slate-300 placeholder:text-slate-600 font-mono text-sm rounded-xl focus:border-amber-500/50"
				bind:value={$blacklist}
			/>
		</div>
		
		<Button 
			on:click={submitBlacklist}
			class="w-full bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 gap-2 rounded-xl shadow-lg shadow-amber-500/25 transition-all duration-300"
		>
			<Send class="w-4 h-4" />
			Update Blacklist
		</Button>
	</div>

	<!-- Info Panel -->
	<div class="space-y-6">
		<div class="p-6 rounded-2xl glass border border-white/10">
			<div class="flex items-center gap-3 mb-4">
				<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
					<Shield class="w-5 h-5 text-white" />
				</div>
				<div>
					<h3 class="font-semibold text-white">Moderation Settings</h3>
					<p class="text-xs text-slate-500">How filtering works</p>
				</div>
			</div>
			
			<div class="space-y-4">
				<div class="p-4 rounded-xl glass-subtle border border-white/10 hover:border-cyan-500/30 transition-all duration-300">
					<h4 class="text-sm font-medium text-white mb-2">Blacklist Behavior</h4>
					<p class="text-xs text-slate-400">Words in the blacklist will be filtered from AI responses. The filter checks for exact matches and common variations.</p>
				</div>
				
				<div class="p-4 rounded-xl glass-subtle border border-white/10 hover:border-cyan-500/30 transition-all duration-300">
					<h4 class="text-sm font-medium text-white mb-2">Case Sensitivity</h4>
					<p class="text-xs text-slate-400">Blacklist matching is case-insensitive. "Word" will match "word", "WORD", and "WoRd".</p>
				</div>
				
				<div class="p-4 rounded-xl glass-subtle border border-white/10 hover:border-cyan-500/30 transition-all duration-300">
					<h4 class="text-sm font-medium text-white mb-2">Phrase Support</h4>
					<p class="text-xs text-slate-400">You can blacklist entire phrases. Each line is treated as a separate entry.</p>
				</div>
			</div>
		</div>

		<div class="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 hover:shadow-lg hover:shadow-amber-500/10 transition-all duration-300">
			<div class="flex items-start gap-3">
				<AlertTriangle class="w-5 h-5 text-amber-400 mt-0.5" />
				<div>
					<h4 class="text-sm font-medium text-amber-400 mb-1">Important Note</h4>
					<p class="text-xs text-amber-400/80">Changes to the blacklist take effect immediately. Be careful when adding common words that might affect normal conversation.</p>
				</div>
			</div>
		</div>
	</div>
</div>
