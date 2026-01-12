<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import * as Tabs from '$lib/components/ui/tabs';
	import { Switch } from '$lib/components/ui/switch';
	import { ScrollArea } from '$lib/components/ui/scroll-area/index.js';
	import { 
		Radio, Users, MessageSquare, TrendingUp, Activity, Eye, Settings,
		Heart, Star, Zap, Clock, BarChart3, Sparkles, Wifi, WifiOff, RefreshCcw,
		ArrowUp, ArrowDown, Gift, Crown, Send, ExternalLink, Copy, Check
	} from 'lucide-svelte';
	import { onMount, onDestroy } from 'svelte';
	import { 
		socket, twitchStats, twitchEvents, twitchChatHistory, twitchViewerHistory,
		twitchChatRate, twitchConnected, twitchConfig, twitchChat, twitchChatEnabled
	} from '../socketio';

	// Local state for charts
	let viewerHistory: number[] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
	let chatRateHistory: number[] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
	let peakViewers = 0;
	let sessionMessages = 0;
	let copied = false;

	// Config form
	let configForm = {
		channelName: '',
		chatMode: 'DISABLE',
		keywords: '',
		bitsThreshold: 100,
		summaryInterval: 10
	};

	// Simulated live data updates
	let updateInterval: ReturnType<typeof setInterval>;

	onMount(() => {
		// Request initial data
		socket.emit("get_twitch_stats");
		socket.emit("get_twitch_config");

		// Simulate live viewer updates for demo
		updateInterval = setInterval(() => {
			// Update viewer history
			const currentViewers = $twitchStats.viewers || Math.floor(Math.random() * 500 + 100);
			viewerHistory = [...viewerHistory.slice(1), currentViewers];
			peakViewers = Math.max(peakViewers, currentViewers);

			// Update chat rate
			const chatRate = Math.floor(Math.random() * 30 + 5);
			chatRateHistory = [...chatRateHistory.slice(1), chatRate];
			sessionMessages += chatRate;
		}, 3000);

		// Load config
		twitchConfig.subscribe(cfg => {
			configForm = { ...cfg };
		});
	});

	onDestroy(() => {
		if (updateInterval) clearInterval(updateInterval);
	});

	function connectTwitch() {
		socket.emit("connect_twitch");
	}

	function disconnectTwitch() {
		socket.emit("disconnect_twitch");
	}

	function saveConfig() {
		socket.emit("save_twitch_config", configForm);
	}

	function copyChannelUrl() {
		navigator.clipboard.writeText(`https://twitch.tv/${configForm.channelName}`);
		copied = true;
		setTimeout(() => copied = false, 2000);
	}

	function openChannel() {
		window.open(`https://twitch.tv/${configForm.channelName}`, '_blank');
	}

	function getEventIcon(type: string) {
		switch(type) {
			case 'follow': return Heart;
			case 'subscribe': return Star;
			case 'raid': return TrendingUp;
			case 'gift': return Gift;
			case 'bits': case 'cheer': return Sparkles;
			case 'hype_train': return Zap;
			default: return Activity;
		}
	}

	function getEventColor(type: string) {
		switch(type) {
			case 'follow': return 'bg-pink-500/20 border-pink-500/30 text-pink-400';
			case 'subscribe': return 'bg-purple-500/20 border-purple-500/30 text-purple-400';
			case 'raid': return 'bg-orange-500/20 border-orange-500/30 text-orange-400';
			case 'gift': return 'bg-emerald-500/20 border-emerald-500/30 text-emerald-400';
			case 'bits': case 'cheer': return 'bg-amber-500/20 border-amber-500/30 text-amber-400';
			case 'hype_train': return 'bg-cyan-500/20 border-cyan-500/30 text-cyan-400';
			default: return 'bg-slate-500/20 border-slate-500/30 text-slate-400';
		}
	}

	// Calculate chart max for scaling
	$: maxViewers = Math.max(...viewerHistory, 1);
	$: maxChatRate = Math.max(...chatRateHistory, 1);
</script>

<!-- Header -->
<div class="mb-8 relative group">
	<div class="absolute -inset-4 bg-gradient-to-r from-purple-500/10 via-pink-500/5 to-cyan-500/10 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-all duration-700"></div>
	<div class="relative flex items-center justify-between">
		<div class="flex items-center gap-4">
			<div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-lg shadow-purple-500/30 hover-scale">
				<Radio class="w-7 h-7 text-white" />
			</div>
			<div>
				<h1 class="text-4xl font-bold gradient-text font-display">
					Twitch Integration
				</h1>
				<p class="text-slate-400 mt-1 flex items-center gap-2">
					<span class="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse"></span>
					Live stream monitoring & chat analysis
				</p>
			</div>
		</div>
		<div class="flex items-center gap-3">
			{#if $twitchConnected}
				<Badge variant="success" class="status-online gap-1.5">
					<Wifi class="w-3 h-3" />
					Connected
				</Badge>
				<Button on:click={disconnectTwitch} variant="outline" class="border-red-500/30 text-red-400 hover:bg-red-500/20 rounded-xl transition-all duration-300">
					Disconnect
				</Button>
			{:else}
				<Badge variant="destructive" class="status-offline gap-1.5">
					<WifiOff class="w-3 h-3" />
					Disconnected
				</Badge>
				<Button on:click={connectTwitch} class="bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 rounded-xl shadow-lg shadow-purple-500/25 transition-all duration-300">
					Connect
				</Button>
			{/if}
		</div>
	</div>
</div>

<!-- Stream Status Card -->
<div class="p-6 rounded-2xl glass border border-purple-500/20 hover-glow-purple transition-all duration-500 mb-6">
	<div class="flex items-center justify-between mb-4">
		<div class="flex items-center gap-3">
			<div class="w-8 h-8 rounded-lg bg-purple-500/20 flex items-center justify-center">
				<Activity class="w-4 h-4 text-purple-400" />
			</div>
			<span class="font-semibold text-white">Stream Status</span>
		</div>
		{#if $twitchStats.isLive}
			<Badge class="bg-red-500 animate-pulse gap-1.5 shadow-lg shadow-red-500/50">
				<span class="w-2 h-2 rounded-full bg-white"></span>
				LIVE
			</Badge>
		{:else}
			<Badge variant="outline" class="border-slate-500/30 text-slate-400">OFFLINE</Badge>
		{/if}
	</div>
	<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
		<div class="p-4 rounded-xl glass-subtle border border-white/5 hover:border-cyan-500/30 transition-all duration-300">
			<p class="text-xs text-slate-500 uppercase tracking-wide mb-1">Uptime</p>
			<p class="text-2xl font-bold text-white font-display">{Math.floor($twitchStats.uptime / 60)}h {$twitchStats.uptime % 60}m</p>
		</div>
		<div class="p-4 rounded-xl glass-subtle border border-white/5 hover:border-cyan-500/30 transition-all duration-300">
			<p class="text-xs text-slate-500 uppercase tracking-wide mb-1">Current Viewers</p>
			<p class="text-2xl font-bold text-cyan-400 font-display">{$twitchStats.viewers.toLocaleString()}</p>
		</div>
		<div class="p-4 rounded-xl glass-subtle border border-white/5 hover:border-purple-500/30 transition-all duration-300">
			<p class="text-xs text-slate-500 uppercase tracking-wide mb-1">Peak Viewers</p>
			<p class="text-2xl font-bold text-purple-400 font-display">{peakViewers.toLocaleString()}</p>
		</div>
		<div class="p-4 rounded-xl glass-subtle border border-white/5 hover:border-pink-500/30 transition-all duration-300">
			<p class="text-xs text-slate-500 uppercase tracking-wide mb-1">Channel</p>
			<div class="flex items-center gap-2">
				<p class="text-lg font-bold text-white truncate">{$twitchStats.channelName || 'Not Set'}</p>
				{#if $twitchStats.channelName}
					<button on:click={openChannel} class="text-purple-400 hover:text-purple-300 transition-colors">
						<ExternalLink class="w-4 h-4" />
					</button>
				{/if}
			</div>
		</div>
	</div>
</div>

<!-- Live Charts Row -->
<div class="grid lg:grid-cols-2 gap-6 mb-6">
	<!-- Viewer Chart -->
	<div class="p-6 rounded-2xl glass border border-white/10 hover-glow-cyan transition-all duration-500">
		<div class="flex items-center justify-between mb-4">
			<div class="flex items-center gap-3">
				<div class="w-10 h-10 rounded-xl bg-cyan-500/20 flex items-center justify-center">
					<Eye class="w-5 h-5 text-cyan-400" />
				</div>
				<div>
					<h3 class="font-semibold text-white">Viewer Count</h3>
					<p class="text-xs text-slate-500">Last 60 seconds</p>
				</div>
			</div>
			<div class="text-right">
				<p class="text-2xl font-bold text-cyan-400 font-display">{viewerHistory[viewerHistory.length - 1]}</p>
				<p class="text-xs text-slate-500">current</p>
			</div>
		</div>
		<div class="h-32 flex items-end gap-1.5 mt-4">
			{#each viewerHistory as value, i}
				<div class="flex-1 relative group">
					<div 
						class="bg-gradient-to-t from-cyan-600 to-cyan-400 rounded-t transition-all duration-500 hover:from-cyan-500 hover:to-cyan-300 shadow-lg shadow-cyan-500/20"
						style="height: {Math.max(4, (value / maxViewers) * 100)}%"
					></div>
					<div class="absolute -top-8 left-1/2 -translate-x-1/2 px-2 py-1 rounded-lg bg-black/90 text-xs text-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 border border-cyan-500/30">
						{value}
					</div>
				</div>
			{/each}
		</div>
	</div>

	<!-- Chat Rate Chart -->
	<div class="p-6 rounded-2xl glass border border-white/10 hover-glow-purple transition-all duration-500">
		<div class="flex items-center justify-between mb-4">
			<div class="flex items-center gap-3">
				<div class="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center">
					<MessageSquare class="w-5 h-5 text-purple-400" />
				</div>
				<div>
					<h3 class="font-semibold text-white">Chat Activity</h3>
					<p class="text-xs text-slate-500">Messages per interval</p>
				</div>
			</div>
			<div class="text-right">
				<p class="text-2xl font-bold text-purple-400 font-display">{sessionMessages.toLocaleString()}</p>
				<p class="text-xs text-slate-500">session total</p>
			</div>
		</div>
		<div class="h-32 flex items-end gap-1.5 mt-4">
			{#each chatRateHistory as value, i}
				<div class="flex-1 relative group">
					<div 
						class="bg-gradient-to-t from-purple-600 to-purple-400 rounded-t transition-all duration-500 hover:from-purple-500 hover:to-purple-300 shadow-lg shadow-purple-500/20"
						style="height: {Math.max(4, (value / maxChatRate) * 100)}%"
					></div>
					<div class="absolute -top-8 left-1/2 -translate-x-1/2 px-2 py-1 rounded-lg bg-black/90 text-xs text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 border border-purple-500/30">
						{value}
					</div>
				</div>
			{/each}
		</div>
	</div>
</div>

<!-- Stats Grid -->
<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
	<div class="p-4 rounded-xl glass border border-pink-500/20 hover-glow-pink transition-all duration-300 group">
		<div class="flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-pink-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
				<Heart class="w-5 h-5 text-pink-400" />
			</div>
			<div>
				<p class="text-xs text-slate-500">Followers</p>
				<p class="text-xl font-bold text-pink-400 font-display">{$twitchStats.followers.toLocaleString()}</p>
			</div>
		</div>
	</div>

	<div class="p-4 rounded-xl glass border border-purple-500/20 hover-glow-purple transition-all duration-300 group">
		<div class="flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
				<Crown class="w-5 h-5 text-purple-400" />
			</div>
			<div>
				<p class="text-xs text-slate-500">Subscribers</p>
				<p class="text-xl font-bold text-purple-400 font-display">{$twitchStats.subscribers}</p>
			</div>
		</div>
	</div>

	<div class="p-4 rounded-xl glass border border-amber-500/20 hover:shadow-lg hover:shadow-amber-500/10 transition-all duration-300 group">
		<div class="flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-amber-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
				<Sparkles class="w-5 h-5 text-amber-400" />
			</div>
			<div>
				<p class="text-xs text-slate-500">Bits</p>
				<p class="text-xl font-bold text-amber-400 font-display">{$twitchStats.bitsReceived.toLocaleString()}</p>
			</div>
		</div>
	</div>

	<div class="p-4 rounded-xl glass border border-orange-500/20 hover:shadow-lg hover:shadow-orange-500/10 transition-all duration-300 group">
		<div class="flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-orange-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
				<TrendingUp class="w-5 h-5 text-orange-400" />
			</div>
			<div>
				<p class="text-xs text-slate-500">Raids</p>
				<p class="text-xl font-bold text-orange-400 font-display">{$twitchStats.raids}</p>
			</div>
		</div>
	</div>

	<div class="p-4 rounded-xl glass border border-emerald-500/20 hover:shadow-lg hover:shadow-emerald-500/10 transition-all duration-300 group">
		<div class="flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
				<MessageSquare class="w-5 h-5 text-emerald-400" />
			</div>
			<div>
				<p class="text-xs text-slate-500">Messages</p>
				<p class="text-xl font-bold text-emerald-400 font-display">{$twitchStats.chatMessages.toLocaleString()}</p>
			</div>
		</div>
	</div>

	<div class="p-4 rounded-xl glass border border-cyan-500/20 hover-glow-cyan transition-all duration-300 group">
		<div class="flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-cyan-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
				<Zap class="w-5 h-5 text-cyan-400" />
			</div>
			<div>
				<p class="text-xs text-slate-500">AI Mode</p>
				<p class="text-sm font-bold text-cyan-400">{$twitchChatEnabled ? 'Active' : 'Off'}</p>
			</div>
		</div>
	</div>
</div>

<!-- Tabs Section -->
<Tabs.Root value="events" class="mt-6">
	<Tabs.List class="mb-6 glass border border-white/10 p-1.5 rounded-2xl">
		<Tabs.Trigger value="events" class="rounded-xl data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-500/30 data-[state=active]:to-pink-500/30 data-[state=active]:shadow-lg data-[state=active]:shadow-purple-500/20 transition-all duration-300">
			<Zap class="w-4 h-4 mr-2" />
			Live Events
		</Tabs.Trigger>
		<Tabs.Trigger value="chat" class="rounded-xl data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-500/30 data-[state=active]:to-pink-500/30 data-[state=active]:shadow-lg data-[state=active]:shadow-purple-500/20 transition-all duration-300">
			<MessageSquare class="w-4 h-4 mr-2" />
			Chat Feed
		</Tabs.Trigger>
		<Tabs.Trigger value="config" class="rounded-xl data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-500/30 data-[state=active]:to-pink-500/30 data-[state=active]:shadow-lg data-[state=active]:shadow-purple-500/20 transition-all duration-300">
			<Settings class="w-4 h-4 mr-2" />
			Configuration
		</Tabs.Trigger>
	</Tabs.List>

	<!-- Events Tab -->
	<Tabs.Content value="events">
		<div class="p-6 rounded-2xl glass border border-white/10">
			<div class="flex items-center justify-between mb-6">
				<div class="flex items-center gap-3">
					<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-lg shadow-purple-500/30">
						<Activity class="w-5 h-5 text-white" />
					</div>
					<div>
						<h3 class="font-semibold text-white">Live Events</h3>
						<p class="text-xs text-slate-500">Real-time stream interactions</p>
					</div>
				</div>
				<Button variant="outline" on:click={() => socket.emit("get_twitch_events")} class="border-white/10 text-slate-400 hover:text-white rounded-xl transition-all duration-300 hover:border-purple-500/30">
					<RefreshCcw class="w-4 h-4 mr-2" />
					Refresh
				</Button>
			</div>

			<ScrollArea class="h-[400px]">
				<div class="space-y-3 pr-4">
					{#each $twitchEvents as event (event.id)}
						<div class="flex items-center justify-between p-4 rounded-xl border {getEventColor(event.type)} transition-all hover:scale-[1.01] hover:shadow-lg animate-in slide-in-from-top-2">
							<div class="flex items-center gap-4">
								<div class="w-10 h-10 rounded-xl bg-black/30 flex items-center justify-center">
									<svelte:component this={getEventIcon(event.type)} class="w-5 h-5" />
								</div>
								<div>
									<p class="font-medium text-white">{event.user}</p>
									<p class="text-sm text-slate-400">{event.details}</p>
								</div>
							</div>
							<div class="text-right">
								{#if event.value}
									<p class="font-bold text-white">{event.value}</p>
								{/if}
								<span class="text-xs text-slate-500">{event.timestamp}</span>
							</div>
						</div>
					{:else}
						<div class="text-center py-12">
							<div class="w-16 h-16 mx-auto rounded-2xl bg-slate-800/50 flex items-center justify-center mb-4">
								<Zap class="w-8 h-8 text-slate-600" />
							</div>
							<p class="text-slate-400 font-medium">No events yet</p>
							<p class="text-sm text-slate-600">Events will appear here when they occur</p>
						</div>
					{/each}
				</div>
			</ScrollArea>
		</div>
	</Tabs.Content>

	<!-- Chat Tab -->
	<Tabs.Content value="chat">
		<div class="p-6 rounded-2xl glass border border-white/10">
			<div class="flex items-center justify-between mb-6">
				<div class="flex items-center gap-3">
					<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/30">
						<MessageSquare class="w-5 h-5 text-white" />
					</div>
					<div>
						<h3 class="font-semibold text-white">Chat Summary</h3>
						<p class="text-xs text-slate-500">AI-analyzed chat messages</p>
					</div>
				</div>
				<div class="flex items-center gap-3 px-3 py-2 rounded-xl glass-subtle border border-white/5">
					<span class="text-xs text-slate-400">AI Analysis:</span>
					<Switch bind:checked={$twitchChatEnabled} on:click={() => socket.emit("toggle_twitch_chat")} />
				</div>
			</div>

			<div class="rounded-xl glass-subtle border border-white/10 p-4 h-[400px] overflow-auto">
				<pre class="text-sm text-slate-300 whitespace-pre-wrap font-mono">{$twitchChat || 'No chat messages captured yet...'}</pre>
			</div>
		</div>
	</Tabs.Content>

	<!-- Config Tab -->
	<Tabs.Content value="config">
		<div class="p-6 rounded-2xl glass border border-white/10">
			<div class="flex items-center gap-3 mb-6">
				<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
					<Settings class="w-5 h-5 text-white" />
				</div>
				<div>
					<h3 class="font-semibold text-white">Twitch Configuration</h3>
					<p class="text-xs text-slate-500">Configure your Twitch integration settings</p>
				</div>
			</div>

			<div class="grid gap-6 md:grid-cols-2 mb-6">
				<div class="space-y-2">
					<Label for="channel" class="text-slate-400">Channel Name</Label>
					<div class="flex gap-2">
						<Input id="channel" bind:value={configForm.channelName} placeholder="your_channel" class="bg-white/5 border-white/10 text-slate-300 flex-1 rounded-xl focus:border-cyan-500/50" />
						<Button on:click={copyChannelUrl} variant="outline" class="border-white/10 text-slate-400 hover:text-white px-3 rounded-xl transition-all duration-300 hover:border-cyan-500/30">
							{#if copied}
								<Check class="w-4 h-4 text-emerald-400" />
							{:else}
								<Copy class="w-4 h-4" />
							{/if}
						</Button>
					</div>
				</div>

				<div class="space-y-2">
					<Label for="mode" class="text-slate-400">Chat Response Mode</Label>
					<select id="mode" bind:value={configForm.chatMode} class="w-full rounded-xl bg-white/5 border border-white/10 px-3 py-2 text-slate-300 focus:border-purple-500/50 focus:outline-none transition-all duration-300">
						<option value="ALL">All Messages</option>
						<option value="KEYWORD">Keywords Only</option>
						<option value="HIGHLIGHT">Highlighted Only</option>
						<option value="BITS">Bits Only</option>
						<option value="DISABLE">Disabled</option>
					</select>
				</div>

				<div class="space-y-2">
					<Label for="keywords" class="text-slate-400">Keywords (comma-separated)</Label>
					<Input id="keywords" bind:value={configForm.keywords} placeholder="hello, help, question" class="bg-white/5 border-white/10 text-slate-300 rounded-xl focus:border-purple-500/50" />
				</div>

				<div class="space-y-2">
					<Label for="bits" class="text-slate-400">Minimum Bits Threshold</Label>
					<Input id="bits" type="number" bind:value={configForm.bitsThreshold} class="bg-white/5 border-white/10 text-slate-300 rounded-xl focus:border-amber-500/50" />
				</div>

				<div class="space-y-2 md:col-span-2">
					<Label for="summary" class="text-slate-400">Summary Interval (seconds, 0 to disable)</Label>
					<Input id="summary" type="number" bind:value={configForm.summaryInterval} class="bg-white/5 border-white/10 text-slate-300 rounded-xl focus:border-cyan-500/50" />
				</div>
			</div>

			<div class="flex gap-3">
				<Button on:click={saveConfig} class="bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 rounded-xl shadow-lg shadow-purple-500/25 transition-all duration-300">
					<Send class="w-4 h-4 mr-2" />
					Save Configuration
				</Button>
				<Button variant="outline" class="border-white/10 text-slate-400 hover:text-white rounded-xl transition-all duration-300 hover:border-white/20">
					Reset to Default
				</Button>
			</div>
		</div>
	</Tabs.Content>
</Tabs.Root>
