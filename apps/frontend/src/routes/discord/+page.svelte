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
		MessageCircle, Settings, Download, Copy, Check, Server, Hash, Mic, 
		Clock, Zap, Shield, Terminal, RefreshCw, Volume2, Users, Headphones,
		MicOff, VolumeX, Send, Wifi, WifiOff, Activity, Radio, Play, Square,
		PhoneCall, PhoneOff
	} from 'lucide-svelte';
	import { onMount, onDestroy } from 'svelte';
	import { 
		socket, discordStats, discordConnected, discordMessages, 
		discordVoiceUsers, discordConfig 
	} from '../socketio';

	interface DiscordCommand {
		name: string;
		description: string;
		usage: string;
		example: string;
	}

	let commands: DiscordCommand[] = [
		{
			name: '/join_vc',
			description: 'Join a voice channel and start listening',
			usage: '/join_vc [channel]',
			example: '/join_vc #general'
		},
		{
			name: '/leave_vc',
			description: 'Leave current voice channel',
			usage: '/leave_vc',
			example: '/leave_vc'
		},
		{
			name: '/clear_history',
			description: 'Clear conversation history',
			usage: '/clear_history',
			example: '/clear_history'
		},
		{
			name: '/context_add',
			description: 'Add context to conversation',
			usage: '/context_add [content]',
			example: '/context_add Remember that I like cats'
		},
		{
			name: '/get_loaded_operations',
			description: 'List all loaded operations',
			usage: '/get_loaded_operations',
			example: '/get_loaded_operations'
		},
		{
			name: '/respond',
			description: 'Force AI to respond immediately',
			usage: '/respond [optional message]',
			example: '/respond Say hello!'
		},
		{
			name: '/set_config',
			description: 'Update bot configuration',
			usage: '/set_config [key] [value]',
			example: '/set_config patience 30'
		}
	];

	let copied = false;
	let botToken = '••••••••••••••••••••••••••••••••';
	let messageInput = '';
	let updateInterval: ReturnType<typeof setInterval>;

	// Local config form
	let configForm = { ...$discordConfig };

	function copyToken() {
		copied = true;
		setTimeout(() => (copied = false), 2000);
	}

	function connectDiscord() {
		socket.emit("connect_discord");
	}

	function disconnectDiscord() {
		socket.emit("disconnect_discord");
	}

	function joinVoice() {
		socket.emit("discord_join_voice");
	}

	function leaveVoice() {
		socket.emit("discord_leave_voice");
	}

	function sendMessage() {
		if (messageInput.trim()) {
			socket.emit("discord_send_message", messageInput);
			messageInput = '';
		}
	}

	function saveConfig() {
		socket.emit("save_discord_config", configForm);
	}

	function downloadLogs() {
		socket.emit("download_discord_logs");
	}

	function formatTime(isoString: string): string {
		return new Date(isoString).toLocaleTimeString('en-US', { 
			hour: '2-digit', 
			minute: '2-digit' 
		});
	}

	onMount(() => {
		socket.emit("get_discord_stats");
		socket.emit("get_discord_config");

		// Simulate stats updates for demo
		updateInterval = setInterval(() => {
			if ($discordConnected) {
				discordStats.update(stats => ({
					...stats,
					messagesProcessed: stats.messagesProcessed + Math.floor(Math.random() * 3)
				}));
			}
		}, 5000);

		discordConfig.subscribe(cfg => {
			configForm = { ...cfg };
		});
	});

	onDestroy(() => {
		if (updateInterval) clearInterval(updateInterval);
	});
</script>

<!-- Header -->
<div class="mb-8 relative group">
	<div class="absolute -inset-4 bg-gradient-to-r from-indigo-500/10 via-purple-500/5 to-blue-500/10 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-all duration-700"></div>
	<div class="relative flex items-center justify-between">
		<div class="flex items-center gap-4">
			<div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30 hover-scale">
				<MessageCircle class="w-7 h-7 text-white" />
			</div>
			<div>
				<h1 class="text-4xl font-bold gradient-text font-display">
					Discord Integration
				</h1>
				<p class="text-slate-400 mt-1 flex items-center gap-2">
					<span class="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse"></span>
					Manage your Discord bot and voice channels
				</p>
			</div>
		</div>
		<div class="flex items-center gap-3">
			{#if $discordConnected}
				<Badge variant="success" class="status-online gap-1.5 bg-emerald-500/20 border border-emerald-500/30 text-emerald-400">
					<Wifi class="w-3 h-3" />
					Connected
				</Badge>
				<Button on:click={disconnectDiscord} variant="outline" class="border-red-500/30 text-red-400 hover:bg-red-500/20 rounded-xl transition-all duration-300">
					Disconnect
				</Button>
			{:else}
				<Badge variant="destructive" class="status-offline gap-1.5 bg-red-500/20 border border-red-500/30 text-red-400">
					<WifiOff class="w-3 h-3" />
					Disconnected
				</Badge>
				<Button on:click={connectDiscord} class="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 rounded-xl shadow-lg shadow-indigo-500/25 transition-all duration-300">
					Connect
				</Button>
			{/if}
		</div>
	</div>
</div>

<!-- Voice Channel Status -->
<div class="p-6 rounded-2xl glass border border-indigo-500/20 hover-glow-purple transition-all duration-500 mb-6">
	<div class="flex items-center justify-between mb-4">
		<div class="flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-lg shadow-purple-500/30">
				<Headphones class="w-5 h-5 text-white" />
			</div>
			<div>
				<h3 class="font-semibold text-white">Voice Channel</h3>
				<p class="text-xs text-slate-500">Current voice connection status</p>
			</div>
		</div>
		<div class="flex items-center gap-2">
			{#if $discordStats.isInVoice}
				<Badge class="bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 gap-1.5">
					<PhoneCall class="w-3 h-3" />
					In Voice
				</Badge>
				<Button on:click={leaveVoice} variant="outline" class="border-red-500/30 text-red-400 hover:bg-red-500/20 rounded-xl text-sm">
					<PhoneOff class="w-4 h-4 mr-1" />
					Leave
				</Button>
			{:else}
				<Badge variant="outline" class="border-slate-500/30 text-slate-400 gap-1.5">
					<PhoneOff class="w-3 h-3" />
					Not in Voice
				</Badge>
				<Button on:click={joinVoice} class="bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 rounded-xl text-sm">
					<PhoneCall class="w-4 h-4 mr-1" />
					Join
				</Button>
			{/if}
		</div>
	</div>
	
	<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
		<div class="p-4 rounded-xl glass-subtle border border-white/5 hover:border-purple-500/30 transition-all duration-300">
			<p class="text-xs text-slate-500 uppercase tracking-wide mb-1">Channel</p>
			<p class="text-lg font-bold text-white truncate">{$discordStats.currentVoiceChannel || 'None'}</p>
		</div>
		<div class="p-4 rounded-xl glass-subtle border border-white/5 hover:border-cyan-500/30 transition-all duration-300">
			<p class="text-xs text-slate-500 uppercase tracking-wide mb-1">Users in Voice</p>
			<p class="text-lg font-bold text-cyan-400">{$discordStats.usersInVoice}</p>
		</div>
		<div class="p-4 rounded-xl glass-subtle border border-white/5 hover:border-emerald-500/30 transition-all duration-300">
			<p class="text-xs text-slate-500 uppercase tracking-wide mb-1">Voice Sessions</p>
			<p class="text-lg font-bold text-emerald-400">{$discordStats.voiceSessions}</p>
		</div>
		<div class="p-4 rounded-xl glass-subtle border border-white/5 hover:border-amber-500/30 transition-all duration-300">
			<p class="text-xs text-slate-500 uppercase tracking-wide mb-1">Avg Response</p>
			<p class="text-lg font-bold text-amber-400">{$discordStats.avgResponseTime.toFixed(1)}s</p>
		</div>
	</div>
	
	<!-- Voice Users List -->
	{#if $discordVoiceUsers.length > 0}
		<div class="mt-4 pt-4 border-t border-white/10">
			<p class="text-xs text-slate-500 uppercase tracking-wide mb-3">Users in Channel</p>
			<div class="flex flex-wrap gap-2">
				{#each $discordVoiceUsers as user}
					<div class="flex items-center gap-2 px-3 py-1.5 rounded-lg glass-subtle border border-white/10 {user.isSpeaking ? 'border-emerald-500/50 bg-emerald-500/10' : ''}">
						<div class="w-2 h-2 rounded-full {user.isSpeaking ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'}"></div>
						<span class="text-sm text-slate-300">{user.username}</span>
						{#if user.isMuted}
							<MicOff class="w-3 h-3 text-red-400" />
						{/if}
						{#if user.isDeafened}
							<VolumeX class="w-3 h-3 text-red-400" />
						{/if}
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>

<!-- Stats Overview -->
<div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
	<div class="p-4 rounded-xl glass border border-indigo-500/20 hover:shadow-lg hover:shadow-indigo-500/10 transition-all duration-300 group">
		<div class="flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
				<Server class="w-5 h-5 text-indigo-400" />
			</div>
			<div>
				<p class="text-xs text-slate-500 uppercase tracking-wide">Servers</p>
				<p class="text-2xl font-bold text-indigo-400 font-display">{$discordStats.servers}</p>
			</div>
		</div>
	</div>

	<div class="p-4 rounded-xl glass border border-blue-500/20 hover:shadow-lg hover:shadow-blue-500/10 transition-all duration-300 group">
		<div class="flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
				<Hash class="w-5 h-5 text-blue-400" />
			</div>
			<div>
				<p class="text-xs text-slate-500 uppercase tracking-wide">Channels</p>
				<p class="text-2xl font-bold text-blue-400 font-display">{$discordStats.activeChannels}</p>
			</div>
		</div>
	</div>

	<div class="p-4 rounded-xl glass border border-emerald-500/20 hover:shadow-lg hover:shadow-emerald-500/10 transition-all duration-300 group">
		<div class="flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
				<MessageCircle class="w-5 h-5 text-emerald-400" />
			</div>
			<div>
				<p class="text-xs text-slate-500 uppercase tracking-wide">Messages</p>
				<p class="text-2xl font-bold text-emerald-400 font-display">{$discordStats.messagesProcessed.toLocaleString()}</p>
			</div>
		</div>
	</div>

	<div class="p-4 rounded-xl glass border border-purple-500/20 hover-glow-purple transition-all duration-300 group">
		<div class="flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
				<Mic class="w-5 h-5 text-purple-400" />
			</div>
			<div>
				<p class="text-xs text-slate-500 uppercase tracking-wide">Voice</p>
				<p class="text-2xl font-bold text-purple-400 font-display">{$discordStats.voiceSessions}</p>
			</div>
		</div>
	</div>

	<div class="p-4 rounded-xl glass border border-amber-500/20 hover:shadow-lg hover:shadow-amber-500/10 transition-all duration-300 group">
		<div class="flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-amber-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
				<Clock class="w-5 h-5 text-amber-400" />
			</div>
			<div>
				<p class="text-xs text-slate-500 uppercase tracking-wide">Latency</p>
				<p class="text-2xl font-bold text-amber-400 font-display">{$discordStats.avgResponseTime}s</p>
			</div>
		</div>
	</div>
</div>

<!-- Main Content Grid -->
<div class="grid lg:grid-cols-3 gap-6 mb-6">
	<!-- Recent Messages -->
	<div class="lg:col-span-2 rounded-2xl glass border border-white/10 overflow-hidden">
		<div class="p-5 border-b border-white/5 flex items-center justify-between">
			<div class="flex items-center gap-3">
				<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
					<MessageCircle class="w-5 h-5 text-white" />
				</div>
				<div>
					<h3 class="font-semibold text-white">Recent Messages</h3>
					<p class="text-xs text-slate-500">Latest Discord activity</p>
				</div>
			</div>
			<Badge variant="outline" class="border-white/10 text-slate-400 text-xs">
				{$discordMessages.length} messages
			</Badge>
		</div>
		
		<ScrollArea class="h-80">
			<div class="p-4 space-y-3">
				{#each $discordMessages as message}
					<div class="p-3 rounded-xl glass-subtle border border-white/5 hover:border-cyan-500/30 transition-all duration-300">
						<div class="flex items-start justify-between mb-1">
							<div class="flex items-center gap-2">
								<span class="font-semibold text-sm {message.isBot ? 'text-cyan-400' : 'text-white'}">{message.user}</span>
								{#if message.isBot}
									<Badge class="text-[10px] bg-cyan-500/20 text-cyan-400 px-1.5 py-0">BOT</Badge>
								{/if}
							</div>
							<span class="text-xs text-slate-500">{formatTime(message.timestamp)}</span>
						</div>
						<p class="text-sm text-slate-300">{message.content}</p>
						<p class="text-xs text-slate-500 mt-1">#{message.channel}</p>
					</div>
				{:else}
					<div class="text-center py-12">
						<div class="w-16 h-16 mx-auto rounded-2xl bg-slate-800/50 flex items-center justify-center mb-4">
							<MessageCircle class="w-8 h-8 text-slate-600" />
						</div>
						<p class="text-sm text-slate-400">No recent messages</p>
						<p class="text-xs text-slate-600">Messages will appear here</p>
					</div>
				{/each}
			</div>
		</ScrollArea>
		
		<!-- Send Message -->
		<div class="p-4 border-t border-white/5">
			<div class="flex gap-2">
				<Input 
					placeholder="Send a message..." 
					bind:value={messageInput}
					on:keydown={(e) => e.key === 'Enter' && sendMessage()}
					class="flex-1 bg-white/5 border-white/10 text-slate-300 placeholder:text-slate-600 rounded-xl focus:border-cyan-500/50"
				/>
				<Button on:click={sendMessage} class="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 rounded-xl shadow-lg shadow-cyan-500/25">
					<Send class="w-4 h-4" />
				</Button>
			</div>
		</div>
	</div>

	<!-- Quick Actions -->
	<div class="space-y-4">
		<!-- Connection Status -->
		<div class="p-5 rounded-2xl glass border border-white/10">
			<div class="flex items-center gap-3 mb-4">
				<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/30">
					<Activity class="w-5 h-5 text-white" />
				</div>
				<div>
					<h3 class="font-semibold text-white">Connection</h3>
					<p class="text-xs text-slate-500">Bot status</p>
				</div>
			</div>
			<div class="space-y-3">
				<div class="flex items-center justify-between p-3 rounded-xl {$discordConnected ? 'bg-emerald-500/10 border border-emerald-500/30' : 'bg-red-500/10 border border-red-500/30'}">
					<div class="flex items-center gap-2">
						{#if $discordConnected}
							<Wifi class="w-4 h-4 text-emerald-400" />
							<span class="text-sm text-emerald-400">Online</span>
						{:else}
							<WifiOff class="w-4 h-4 text-red-400" />
							<span class="text-sm text-red-400">Offline</span>
						{/if}
					</div>
					<div class="w-2.5 h-2.5 rounded-full {$discordConnected ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}" />
				</div>
				<div class="flex items-center justify-between p-3 rounded-xl {$discordStats.isInVoice ? 'bg-purple-500/10 border border-purple-500/30' : 'bg-white/5 border border-white/10'}">
					<div class="flex items-center gap-2">
						<Headphones class="w-4 h-4 {$discordStats.isInVoice ? 'text-purple-400' : 'text-slate-500'}" />
						<span class="text-sm {$discordStats.isInVoice ? 'text-purple-400' : 'text-slate-400'}">Voice</span>
					</div>
					<div class="w-2.5 h-2.5 rounded-full {$discordStats.isInVoice ? 'bg-purple-400 animate-pulse' : 'bg-slate-600'}" />
				</div>
			</div>
		</div>

		<!-- Quick Stats -->
		<div class="p-5 rounded-2xl glass border border-white/10">
			<h4 class="text-sm font-medium text-white mb-3">Session Stats</h4>
			<div class="space-y-3">
				<div class="flex items-center justify-between">
					<span class="text-sm text-slate-400">Uptime</span>
					<span class="text-sm font-mono text-cyan-400">2h 34m</span>
				</div>
				<div class="flex items-center justify-between">
					<span class="text-sm text-slate-400">Responses</span>
					<span class="text-sm font-mono text-purple-400">{$discordStats.messagesProcessed}</span>
				</div>
				<div class="flex items-center justify-between">
					<span class="text-sm text-slate-400">Voice Time</span>
					<span class="text-sm font-mono text-emerald-400">1h 12m</span>
				</div>
			</div>
		</div>
	</div>
</div>

<!-- Tabs -->
<Tabs.Root value="commands">
	<Tabs.List class="mb-6 glass border border-white/10 p-1.5 rounded-2xl">
		<Tabs.Trigger value="commands" class="rounded-xl data-[state=active]:bg-gradient-to-r data-[state=active]:from-indigo-500/30 data-[state=active]:to-purple-500/30 data-[state=active]:shadow-lg data-[state=active]:shadow-indigo-500/20 transition-all duration-300">
			<Terminal class="w-4 h-4 mr-2" />
			Commands
		</Tabs.Trigger>
		<Tabs.Trigger value="config" class="rounded-xl data-[state=active]:bg-gradient-to-r data-[state=active]:from-indigo-500/30 data-[state=active]:to-purple-500/30 data-[state=active]:shadow-lg data-[state=active]:shadow-indigo-500/20 transition-all duration-300">
			<Settings class="w-4 h-4 mr-2" />
			Configuration
		</Tabs.Trigger>
		<Tabs.Trigger value="security" class="rounded-xl data-[state=active]:bg-gradient-to-r data-[state=active]:from-indigo-500/30 data-[state=active]:to-purple-500/30 data-[state=active]:shadow-lg data-[state=active]:shadow-indigo-500/20 transition-all duration-300">
			<Shield class="w-4 h-4 mr-2" />
			Security
		</Tabs.Trigger>
	</Tabs.List>

	<!-- Commands Tab -->
	<Tabs.Content value="commands">
		<div class="p-6 rounded-2xl glass border border-white/10">
			<div class="flex items-center gap-3 mb-6">
				<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
					<Zap class="w-5 h-5 text-white" />
				</div>
				<div>
					<h3 class="font-semibold text-white">Slash Commands</h3>
					<p class="text-xs text-slate-500">Available Discord commands</p>
				</div>
			</div>

			<div class="grid md:grid-cols-2 gap-4">
				{#each commands as cmd}
					<div class="p-4 rounded-xl glass-subtle border border-white/10 hover:border-indigo-500/30 transition-all duration-300 hover:shadow-lg hover:shadow-indigo-500/10">
						<div class="flex items-start justify-between mb-2">
							<code class="text-indigo-400 font-mono font-bold">{cmd.name}</code>
							<Badge variant="outline" class="text-xs rounded-lg border-white/10">Slash</Badge>
						</div>
						<p class="text-sm text-slate-400 mb-3">{cmd.description}</p>
						<div class="space-y-1 text-xs">
							<div>
								<span class="text-slate-500">Usage:</span>
								<code class="ml-2 px-2 py-0.5 rounded-lg bg-black/40 text-cyan-400">{cmd.usage}</code>
							</div>
							<div>
								<span class="text-slate-500">Example:</span>
								<code class="ml-2 px-2 py-0.5 rounded-lg bg-black/40 text-emerald-400">{cmd.example}</code>
							</div>
						</div>
					</div>
				{/each}
			</div>
		</div>
	</Tabs.Content>

	<!-- Configuration Tab -->
	<Tabs.Content value="config">
		<div class="p-6 rounded-2xl glass border border-white/10">
			<div class="flex items-center gap-3 mb-6">
				<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
					<Settings class="w-5 h-5 text-white" />
				</div>
				<div>
					<h3 class="font-semibold text-white">Bot Configuration</h3>
					<p class="text-xs text-slate-500">Adjust bot behavior and settings</p>
				</div>
			</div>

			<div class="grid gap-6 md:grid-cols-2 mb-6">
				<div class="space-y-2">
					<Label for="prefix" class="text-slate-400">Command Prefix</Label>
					<Input id="prefix" bind:value={configForm.prefix} class="bg-white/5 border-white/10 text-slate-300 rounded-xl focus:border-cyan-500/50" />
				</div>
				<div class="space-y-2">
					<Label for="latency" class="text-slate-400">Response Latency (s)</Label>
					<Input id="latency" type="number" bind:value={configForm.responseLatency} class="bg-white/5 border-white/10 text-slate-300 rounded-xl focus:border-cyan-500/50" />
				</div>
				<div class="space-y-2">
					<Label for="idle" class="text-slate-400">Idle Interval (s)</Label>
					<Input id="idle" type="number" bind:value={configForm.idleInterval} class="bg-white/5 border-white/10 text-slate-300 rounded-xl focus:border-cyan-500/50" />
				</div>
				<div class="space-y-2">
					<Label for="context" class="text-slate-400">Max Context Length</Label>
					<Input id="context" type="number" bind:value={configForm.maxContextLength} class="bg-white/5 border-white/10 text-slate-300 rounded-xl focus:border-cyan-500/50" />
				</div>
			</div>

			<div class="space-y-4 p-4 rounded-xl glass-subtle border border-white/10 mb-6">
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-2">
						<Volume2 class="w-4 h-4 text-slate-400" />
						<span class="text-sm text-slate-300">Voice Channel Support</span>
					</div>
					<Switch bind:checked={configForm.enableVoice} />
				</div>
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-2">
						<MessageCircle class="w-4 h-4 text-slate-400" />
						<span class="text-sm text-slate-300">Text Channel Support</span>
					</div>
					<Switch bind:checked={configForm.enableText} />
				</div>
			</div>

			<div class="flex gap-3">
				<Button on:click={saveConfig} class="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 rounded-xl shadow-lg shadow-cyan-500/25 transition-all duration-300">
					Save Configuration
				</Button>
				<Button variant="outline" class="border-white/10 text-slate-400 hover:text-white rounded-xl transition-all duration-300 hover:border-white/20">
					Reset to Default
				</Button>
			</div>
		</div>
	</Tabs.Content>

	<!-- Security Tab -->
	<Tabs.Content value="security">
		<div class="p-6 rounded-2xl glass border border-white/10">
			<div class="flex items-center gap-3 mb-6">
				<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-red-500 to-orange-600 flex items-center justify-center shadow-lg shadow-red-500/30">
					<Shield class="w-5 h-5 text-white" />
				</div>
				<div>
					<h3 class="font-semibold text-white">Security & Tokens</h3>
					<p class="text-xs text-slate-500">Manage bot token and security settings</p>
				</div>
			</div>

			<div class="p-4 rounded-xl bg-red-500/10 border border-red-500/20 mb-6 hover:shadow-lg hover:shadow-red-500/10 transition-all duration-300">
				<p class="text-sm font-medium text-red-400 mb-3">Bot Token</p>
				<div class="flex items-center gap-2 mb-2">
					<code class="flex-1 bg-black/40 px-4 py-2 rounded-xl font-mono text-sm text-slate-400">{botToken}</code>
					<Button
						size="sm"
						variant="outline"
						on:click={copyToken}
						class="gap-2 border-white/10 text-slate-400 hover:text-white rounded-xl transition-all duration-300 hover:border-white/20"
					>
						{#if copied}
							<Check class="h-4 w-4 text-emerald-400" />
						{:else}
							<Copy class="h-4 w-4" />
						{/if}
					</Button>
				</div>
				<p class="text-xs text-red-400/60">⚠️ Never share your bot token publicly</p>
			</div>

			<div class="grid gap-4 md:grid-cols-2">
				<Button variant="destructive" class="gap-2 bg-red-500/20 border border-red-500/30 text-red-400 hover:bg-red-500/30 rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-red-500/20">
					<RefreshCw class="h-4 w-4" />
					Regenerate Token
				</Button>
				<Button variant="outline" on:click={downloadLogs} class="gap-2 border-white/10 text-slate-400 hover:text-white rounded-xl transition-all duration-300 hover:border-white/20">
					<Download class="h-4 w-4" />
					Download Logs
				</Button>
			</div>
		</div>
	</Tabs.Content>
</Tabs.Root>
