<script lang="ts">
	import * as Card from "$lib/components/ui/card";
	import { Button } from "$lib/components/ui/button";
	import { Badge } from "$lib/components/ui/badge";
	import * as Tabs from "$lib/components/ui/tabs";
	import { ScrollArea } from "$lib/components/ui/scroll-area/index.js";
	import { 
		RefreshCcw, Eye, Move, Mic, MicOff, Sparkles, Zap, Monitor, 
		Wifi, WifiOff, Activity, Heart, Smile, Frown, Meh, AlertCircle,
		Clock, TrendingUp, Play, Pause, RotateCcw, Settings, BarChart3,
		Check, X, Layers
	} from "lucide-svelte";
	import { onMount, onDestroy } from "svelte";

	import { 
		socket, hotkeys, vtsStatus, vtsExpressionHistory, 
		vtsHotkeyExecutions, vtsEmotionCounts, vtsAnimations 
	} from "../socketio";

	// Local state
	let hotkeyQueue: string[] = [];
	let isPlaying = true;
	let lastExecution = '';
	let executionHistory: { name: string; time: string; success: boolean }[] = [];
	let emotionChartData: { emotion: string; count: number; color: string }[] = [];

	// Emotion colors
	const emotionColors: Record<string, string> = {
		joy: 'from-yellow-500 to-amber-500',
		love: 'from-pink-500 to-rose-500',
		surprise: 'from-cyan-500 to-blue-500',
		anger: 'from-red-500 to-orange-500',
		sadness: 'from-blue-500 to-indigo-500',
		fear: 'from-purple-500 to-violet-500',
		neutral: 'from-slate-500 to-gray-500',
		amusement: 'from-green-500 to-emerald-500',
		excitement: 'from-orange-500 to-yellow-500',
		curiosity: 'from-teal-500 to-cyan-500',
	};

	function getEmotionColor(emotion: string): string {
		return emotionColors[emotion] || emotionColors.neutral;
	}

	function getEmotionIcon(emotion: string) {
		switch(emotion) {
			case 'joy': case 'amusement': case 'excitement': case 'love': return Smile;
			case 'sadness': case 'fear': case 'anger': return Frown;
			default: return Meh;
		}
	}

	function getHotkeys() {
		socket.emit("get_hotkeys");
	}

	function sendHotkey(hotkey: string) {
		socket.emit("send_hotkey", hotkey);
		lastExecution = hotkey;
		executionHistory = [
			{ name: hotkey, time: new Date().toLocaleTimeString(), success: true },
			...executionHistory.slice(0, 19)
		];
	}

	function triggerProp(prop_action: string) {
		socket.emit("trigger_prop", prop_action);
	}

	function moveModel(mode: string) {
		socket.emit("move_model", mode);
	}

	function connectVTS() {
		socket.emit("connect_vts");
	}

	function disconnectVTS() {
		socket.emit("disconnect_vts");
	}

	function togglePlayback() {
		isPlaying = !isPlaying;
		socket.emit("vts_toggle_playback", isPlaying);
	}

	function clearQueue() {
		socket.emit("vts_clear_queue");
		hotkeyQueue = [];
	}

	// Update emotion chart data when counts change
	$: {
		const counts = $vtsEmotionCounts;
		emotionChartData = Object.entries(counts)
			.map(([emotion, count]) => ({
				emotion,
				count: count as number,
				color: getEmotionColor(emotion)
			}))
			.sort((a, b) => b.count - a.count)
			.slice(0, 8);
	}

	$: maxEmotionCount = Math.max(...emotionChartData.map(d => d.count), 1);

	onMount(() => {
		getHotkeys();
		socket.emit("get_vts_status");

		// Subscribe to execution updates
		vtsHotkeyExecutions.subscribe(execs => {
			executionHistory = execs.map(e => ({
				name: e.hotkeyName,
				time: e.timestamp,
				success: e.success
			}));
		});
	});
</script>

<!-- Header -->
<div class="mb-8 relative group">
	<div class="absolute -inset-4 bg-gradient-to-r from-pink-500/10 via-rose-500/5 to-purple-500/10 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-all duration-700"></div>
	<div class="relative flex items-center justify-between">
		<div class="flex items-center gap-4">
			<div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center shadow-lg shadow-pink-500/30 hover-scale">
				<Eye class="w-7 h-7 text-white" />
			</div>
			<div>
				<h1 class="text-4xl font-bold gradient-text font-display">
					VTube Studio
				</h1>
				<p class="text-slate-400 mt-1 flex items-center gap-2">
					<span class="w-1.5 h-1.5 rounded-full bg-pink-400 animate-pulse"></span>
					Control your VTuber model and animations
				</p>
			</div>
		</div>
		<div class="flex items-center gap-3">
			{#if $vtsStatus.connected}
				<Badge variant="success" class="status-online gap-1.5">
					<Wifi class="w-3 h-3" />
					Connected
				</Badge>
				<Button on:click={disconnectVTS} variant="outline" class="border-red-500/30 text-red-400 hover:bg-red-500/20 rounded-xl transition-all duration-300">
					Disconnect
				</Button>
			{:else}
				<Badge variant="destructive" class="status-offline gap-1.5">
					<WifiOff class="w-3 h-3" />
					Disconnected
				</Badge>
				<Button on:click={connectVTS} class="bg-gradient-to-r from-pink-500 to-rose-600 hover:from-pink-600 hover:to-rose-700 rounded-xl shadow-lg shadow-pink-500/25 transition-all duration-300">
					Connect
				</Button>
			{/if}
		</div>
	</div>
</div>

<!-- Status Bar -->
<div class="p-6 rounded-2xl glass border border-pink-500/20 hover-glow-pink transition-all duration-500 mb-6">
	<div class="grid grid-cols-2 md:grid-cols-5 gap-4">
		<div class="p-4 rounded-xl glass-subtle border border-white/5 hover:border-pink-500/30 transition-all duration-300">
			<p class="text-xs text-slate-500 uppercase tracking-wide mb-1">Model</p>
			<p class="text-lg font-bold text-white truncate font-display">{$vtsStatus.modelName || 'None'}</p>
		</div>
		<div class="p-4 rounded-xl glass-subtle border border-white/5 hover:border-emerald-500/30 transition-all duration-300">
			<p class="text-xs text-slate-500 uppercase tracking-wide mb-1">Status</p>
			<div class="flex items-center gap-2">
				{#if $vtsStatus.modelLoaded}
					<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-lg shadow-emerald-500/50"></span>
					<p class="text-lg font-bold text-emerald-400">Ready</p>
				{:else}
					<span class="w-2 h-2 rounded-full bg-amber-500"></span>
					<p class="text-lg font-bold text-amber-400">Loading</p>
				{/if}
			</div>
		</div>
		<div class="p-4 rounded-xl glass-subtle border border-white/5 hover:border-pink-500/30 transition-all duration-300">
			<p class="text-xs text-slate-500 uppercase tracking-wide mb-1">Current Expression</p>
			<p class="text-lg font-bold text-pink-400 capitalize font-display">{$vtsStatus.currentExpression || 'neutral'}</p>
		</div>
		<div class="p-4 rounded-xl glass-subtle border border-white/5 hover:border-cyan-500/30 transition-all duration-300">
			<p class="text-xs text-slate-500 uppercase tracking-wide mb-1">Queue Length</p>
			<p class="text-lg font-bold text-cyan-400 font-display">{$vtsStatus.hotkeyQueueLength}</p>
		</div>
		<div class="p-4 rounded-xl glass-subtle border border-white/5 hover:border-purple-500/30 transition-all duration-300">
			<p class="text-xs text-slate-500 uppercase tracking-wide mb-1">Last Hotkey</p>
			<p class="text-lg font-bold text-purple-400 truncate font-display">{$vtsStatus.lastHotkey || 'None'}</p>
		</div>
	</div>
</div>

<!-- Main Content -->
<Tabs.Root value="hotkeys" class="mb-6">
	<Tabs.List class="mb-6 glass border border-white/10 p-1.5 rounded-2xl">
		<Tabs.Trigger value="hotkeys" class="rounded-xl data-[state=active]:bg-gradient-to-r data-[state=active]:from-pink-500/30 data-[state=active]:to-rose-500/30 data-[state=active]:shadow-lg data-[state=active]:shadow-pink-500/20 transition-all duration-300">
			<Zap class="w-4 h-4 mr-2" />
			Hotkeys
		</Tabs.Trigger>
		<Tabs.Trigger value="emotions" class="rounded-xl data-[state=active]:bg-gradient-to-r data-[state=active]:from-pink-500/30 data-[state=active]:to-rose-500/30 data-[state=active]:shadow-lg data-[state=active]:shadow-pink-500/20 transition-all duration-300">
			<Smile class="w-4 h-4 mr-2" />
			Emotions
		</Tabs.Trigger>
		<Tabs.Trigger value="history" class="rounded-xl data-[state=active]:bg-gradient-to-r data-[state=active]:from-pink-500/30 data-[state=active]:to-rose-500/30 data-[state=active]:shadow-lg data-[state=active]:shadow-pink-500/20 transition-all duration-300">
			<Clock class="w-4 h-4 mr-2" />
			History
		</Tabs.Trigger>
	</Tabs.List>

	<!-- Hotkeys Tab -->
	<Tabs.Content value="hotkeys">
		<div class="grid lg:grid-cols-2 xl:grid-cols-3 gap-6">
			<!-- Trigger Hotkeys -->
			<div class="xl:col-span-2 p-6 rounded-2xl glass border border-white/10">
				<div class="flex items-center justify-between mb-6">
					<div class="flex items-center gap-3">
						<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
							<Zap class="w-5 h-5 text-white" />
						</div>
						<div>
							<h3 class="font-semibold text-white">Trigger Hotkeys</h3>
							<p class="text-xs text-slate-500">{$hotkeys.length} hotkeys available</p>
						</div>
					</div>
					<div class="flex gap-2">
						<Button variant="outline" on:click={togglePlayback} class="border-white/10 text-slate-400 hover:text-white rounded-xl transition-all duration-300 hover:border-pink-500/30">
							{#if isPlaying}
								<Pause class="w-4 h-4 mr-2" />
								Pause
							{:else}
								<Play class="w-4 h-4 mr-2" />
								Resume
							{/if}
						</Button>
						<Button variant="outline" on:click={getHotkeys} class="border-white/10 text-slate-400 hover:text-white rounded-xl transition-all duration-300 hover:border-cyan-500/30">
							<RefreshCcw class="w-4 h-4" />
						</Button>
					</div>
				</div>
				
				<div class="flex flex-wrap gap-2 max-h-[400px] overflow-auto">
					{#each $hotkeys as hotkey}
						<button 
							on:click={() => {sendHotkey(hotkey)}}
							class="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 text-cyan-400 hover:from-cyan-500/30 hover:to-blue-500/30 hover:border-cyan-400/50 hover:shadow-lg hover:shadow-cyan-500/20 transition-all font-medium text-sm"
						>
							{hotkey}
						</button>
					{/each}
					{#if $hotkeys.length === 0}
						<div class="w-full text-center py-8">
							<div class="w-16 h-16 mx-auto rounded-2xl bg-slate-800/50 flex items-center justify-center mb-4">
								<Zap class="w-8 h-8 text-slate-600" />
							</div>
							<p class="text-slate-400 font-medium">No hotkeys loaded</p>
							<p class="text-sm text-slate-600">Click Refresh to load from VTube Studio</p>
						</div>
					{/if}
				</div>
			</div>

			<!-- Move Model -->
			<div class="p-6 rounded-2xl glass border border-white/10">
				<div class="flex items-center gap-3 mb-6">
					<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-lg shadow-purple-500/30">
						<Move class="w-5 h-5 text-white" />
					</div>
					<div>
						<h3 class="font-semibold text-white">Model Positions</h3>
						<p class="text-xs text-slate-500">Move to preset locations</p>
					</div>
				</div>

				<div class="space-y-3">
					<button 
						on:click={() => {moveModel("chat")}}
						class="w-full p-4 rounded-xl bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30 text-purple-400 hover:from-purple-500/30 hover:to-pink-500/30 hover:border-purple-400/50 hover:shadow-lg hover:shadow-purple-500/20 transition-all flex items-center gap-3 group"
					>
						<div class="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
							<Sparkles class="w-5 h-5" />
						</div>
						<div class="text-left">
							<p class="font-medium">Chatting</p>
							<p class="text-xs text-purple-400/60">Default streaming position</p>
						</div>
					</button>

					<button 
						on:click={() => {moveModel("screen")}}
						class="w-full p-4 rounded-xl bg-gradient-to-r from-blue-500/20 to-cyan-500/20 border border-blue-500/30 text-blue-400 hover:from-blue-500/30 hover:to-cyan-500/30 hover:border-blue-400/50 hover:shadow-lg hover:shadow-blue-500/20 transition-all flex items-center gap-3 group"
					>
						<div class="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
							<Monitor class="w-5 h-5" />
						</div>
						<div class="text-left">
							<p class="font-medium">Full Screen</p>
							<p class="text-xs text-blue-400/60">Centered full display</p>
						</div>
					</button>

					<button 
						on:click={() => {moveModel("react")}}
						class="w-full p-4 rounded-xl bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/30 text-amber-400 hover:from-amber-500/30 hover:to-orange-500/30 hover:border-amber-400/50 hover:shadow-lg hover:shadow-amber-500/20 transition-all flex items-center gap-3 group"
					>
						<div class="w-10 h-10 rounded-xl bg-amber-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
							<Eye class="w-5 h-5" />
						</div>
						<div class="text-left">
							<p class="font-medium">Reacting</p>
							<p class="text-xs text-amber-400/60">Side position for reactions</p>
						</div>
					</button>
				</div>

				<!-- Props Section -->
				<div class="mt-6 pt-6 border-t border-white/10">
					<div class="flex items-center gap-3 mb-4">
						<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/30">
							<Layers class="w-5 h-5 text-white" />
						</div>
						<div>
							<h3 class="font-semibold text-white">Props</h3>
							<p class="text-xs text-slate-500">Toggle props</p>
						</div>
					</div>

					<div class="grid grid-cols-2 gap-3">
						<button 
							on:click={() => {triggerProp("spawn_microphone")}}
							class="p-4 rounded-xl bg-gradient-to-r from-emerald-500/20 to-teal-500/20 border border-emerald-500/30 text-emerald-400 hover:from-emerald-500/30 hover:to-teal-500/30 hover:border-emerald-400/50 hover:shadow-lg hover:shadow-emerald-500/20 transition-all flex flex-col items-center gap-2"
						>
							<Mic class="w-6 h-6" />
							<span class="text-sm font-medium">Spawn Mic</span>
						</button>

						<button 
							on:click={() => {triggerProp("despawn_microphone")}}
							class="p-4 rounded-xl bg-gradient-to-r from-red-500/20 to-orange-500/20 border border-red-500/30 text-red-400 hover:from-red-500/30 hover:to-orange-500/30 hover:border-red-400/50 hover:shadow-lg hover:shadow-red-500/20 transition-all flex flex-col items-center gap-2"
						>
							<MicOff class="w-6 h-6" />
							<span class="text-sm font-medium">Despawn Mic</span>
						</button>
					</div>
				</div>
			</div>
		</div>
	</Tabs.Content>

	<!-- Emotions Tab -->
	<Tabs.Content value="emotions">
		<div class="grid lg:grid-cols-2 gap-6">
			<!-- Emotion Distribution Chart -->
			<div class="p-6 rounded-2xl glass border border-white/10 hover-glow-pink transition-all duration-500">
				<div class="flex items-center gap-3 mb-6">
					<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center shadow-lg shadow-pink-500/30">
						<BarChart3 class="w-5 h-5 text-white" />
					</div>
					<div>
						<h3 class="font-semibold text-white">Emotion Distribution</h3>
						<p class="text-xs text-slate-500">Expression frequency this session</p>
					</div>
				</div>

				{#if emotionChartData.length > 0}
					<div class="space-y-3">
						{#each emotionChartData as item}
							<div class="flex items-center gap-3 group">
								<div class="w-20 text-sm text-slate-400 capitalize group-hover:text-slate-300 transition-colors">{item.emotion}</div>
								<div class="flex-1 h-8 bg-white/5 rounded-lg overflow-hidden border border-white/5">
									<div 
										class="h-full bg-gradient-to-r {item.color} transition-all duration-500 flex items-center justify-end pr-2 shadow-lg"
										style="width: {(item.count / maxEmotionCount) * 100}%"
									>
										<span class="text-xs text-white font-bold drop-shadow">{item.count}</span>
									</div>
								</div>
							</div>
						{/each}
					</div>
				{:else}
					<div class="text-center py-12">
						<div class="w-16 h-16 mx-auto rounded-2xl bg-slate-800/50 flex items-center justify-center mb-4">
							<Smile class="w-8 h-8 text-slate-600" />
						</div>
						<p class="text-slate-400 font-medium">No emotion data yet</p>
						<p class="text-sm text-slate-600">Emotions will be tracked as AI responds</p>
					</div>
				{/if}
			</div>

			<!-- Expression Timeline -->
			<div class="p-6 rounded-2xl glass border border-white/10 hover-glow-cyan transition-all duration-500">
				<div class="flex items-center gap-3 mb-6">
					<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
						<TrendingUp class="w-5 h-5 text-white" />
					</div>
					<div>
						<h3 class="font-semibold text-white">Expression Timeline</h3>
						<p class="text-xs text-slate-500">Recent expression changes</p>
					</div>
				</div>

				<div class="flex flex-wrap gap-2">
					{#each $vtsExpressionHistory as expression, i}
						<div 
							class="px-3 py-1.5 rounded-xl bg-gradient-to-r {getEmotionColor(expression)} text-white text-sm font-medium capitalize transition-all hover:scale-105 shadow-lg"
							style="opacity: {0.4 + (i / $vtsExpressionHistory.length) * 0.6}"
						>
							{expression}
						</div>
					{:else}
						<p class="text-slate-500 text-sm">No expressions recorded yet</p>
					{/each}
				</div>
			</div>
		</div>
	</Tabs.Content>

	<!-- History Tab -->
	<Tabs.Content value="history">
		<div class="p-6 rounded-2xl glass border border-white/10">
			<div class="flex items-center justify-between mb-6">
				<div class="flex items-center gap-3">
					<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-amber-500/30">
						<Clock class="w-5 h-5 text-white" />
					</div>
					<div>
						<h3 class="font-semibold text-white">Execution History</h3>
						<p class="text-xs text-slate-500">Recent hotkey executions</p>
					</div>
				</div>
				<Button variant="outline" on:click={clearQueue} class="border-red-500/30 text-red-400 hover:bg-red-500/20 rounded-xl transition-all duration-300">
					<RotateCcw class="w-4 h-4 mr-2" />
					Clear Queue
				</Button>
			</div>

			<ScrollArea class="h-[400px]">
				<div class="space-y-2 pr-4">
					{#each executionHistory as exec, i}
						<div class="flex items-center justify-between p-3 rounded-xl glass-subtle border border-white/10 hover:border-pink-500/30 transition-all duration-300 {i === 0 ? 'ring-2 ring-pink-500/30' : ''}">
							<div class="flex items-center gap-3">
								<div class="w-8 h-8 rounded-lg {exec.success ? 'bg-emerald-500/20' : 'bg-red-500/20'} flex items-center justify-center">
									{#if exec.success}
										<Check class="w-4 h-4 text-emerald-400" />
									{:else}
										<X class="w-4 h-4 text-red-400" />
									{/if}
								</div>
								<div>
									<p class="font-medium text-white">{exec.name}</p>
									<p class="text-xs text-slate-500">{exec.time}</p>
								</div>
							</div>
							{#if i === 0}
								<Badge class="bg-pink-500/20 border border-pink-500/30 text-pink-400">Latest</Badge>
							{/if}
						</div>
					{:else}
						<div class="text-center py-12">
							<Clock class="w-12 h-12 text-slate-600 mx-auto mb-3" />
							<p class="text-slate-400">No executions yet</p>
							<p class="text-sm text-slate-600">Trigger a hotkey to see it here</p>
						</div>
					{/each}
				</div>
			</ScrollArea>
		</div>
	</Tabs.Content>
</Tabs.Root>

<!-- Quick Stats Footer -->
<div class="mt-6 p-4 rounded-xl bg-pink-500/10 border border-pink-500/20 flex items-center justify-between">
	<div class="flex items-center gap-3">
		<div class="w-2 h-2 rounded-full {$vtsStatus.connected ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}"></div>
		<span class="text-sm {$vtsStatus.connected ? 'text-emerald-400' : 'text-red-400'}">
			{$vtsStatus.connected ? 'VTube Studio connected' : 'VTube Studio disconnected'}
		</span>
	</div>
	<div class="flex items-center gap-4 text-xs text-slate-500">
		<span>Plugin: {$vtsStatus.pluginName || 'Voxelle VTS'}</span>
		<span>•</span>
		<span>Total Executions: {executionHistory.length}</span>
	</div>
</div>
