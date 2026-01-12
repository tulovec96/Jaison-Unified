<script lang="ts">
	import * as Card from "$lib/components/ui/card";
	import { Textarea } from "$lib/components/ui/textarea";
	import { Button } from "$lib/components/ui/button";
	import { Input } from "$lib/components/ui/input";
	import { Progress } from "$lib/components/ui/progress";
	import { Switch } from "$lib/components/ui/switch";
	import * as Select from "$lib/components/ui/select";

	import {
		BrainCircuit, VolumeX, MicOff, Move, Play, Sparkles, Send, XOctagon, Pause, PlayCircle,
		MessageSquare, Zap, Activity, Eye, Music, Lightbulb, Radio, Mic, Volume2, Brain, Timer, AlertTriangle,
		Wifi, WifiOff, Heart, Users, TrendingUp, Smile, Power, CircleDot, Waves, AudioLines,
		ArrowUpRight, MoreHorizontal, RefreshCw, Clock, Flame, Star, Target, BarChart3
	} from "lucide-svelte";

	import { socket,
		currentMessage,
		nextMessage,
		AI_thinking,
		AI_speaking,
		human_speaking,
		patiencePercent,
		total_time,
		twitchChat,
		twitchChatEnabled,
		LLMEnabled,
		TTSEnabled,
		STTEnabled,
		multimodalEnabled,
		movementEnabled,
		selectedAudio,
		songs,
		twitchStats,
		twitchConnected,
		discordStats,
		discordConnected,
		vtsStatus} from "./socketio";

	// Current Message Section
	function abortMessage() {
		socket.emit("abort_current_message");
	}

	// Next Message Section
	function cancelMessage() {
		socket.emit("cancel_next_message");
	}

	// Twitch Chat Section
	function toggleTwitchChat() {
		twitchChatEnabled.set(!$twitchChatEnabled);
		if ($twitchChatEnabled) {
			socket.emit("enable_twitch");
		} else {
			socket.emit("disable_twitch");
		}
	}

	// Controls Section
	function toggleLLM() {
		LLMEnabled.set(!$LLMEnabled);
		socket.emit($LLMEnabled ? "enable_LLM" : "disable_LLM");
	}
	function toggleTTS() {
		TTSEnabled.set(!$TTSEnabled);
		socket.emit($TTSEnabled ? "enable_TTS" : "disable_TTS");
	}
	function toggleSTT() {
		STTEnabled.set(!$STTEnabled);
		socket.emit($STTEnabled ? "enable_STT" : "disable_STT");
	}
	function toggleMovement() {
		movementEnabled.set(!$movementEnabled);
		socket.emit($movementEnabled ? "enable_movement" : "disable_movement");
	}
	function toggleMultimodal() {
		multimodalEnabled.set(!$multimodalEnabled);
		socket.emit($multimodalEnabled ? "enable_multimodal" : "disable_multimodal");
	}

	// Music section
	function playAudio() {
		socket.emit("play_audio", $selectedAudio.value);
	}
	function pauseAudio() {
		socket.emit("pause_audio");
	}
	function resumeAudio() {
		socket.emit("resume_audio");
	}
	function abortAudio() {
		socket.emit("abort_audio");
	}

	// Behavior Section
	function funFact() {
		socket.emit("fun_fact");
	}
	let topic = "";
	function newTopic() {
		socket.emit("new_topic", topic);
		topic = "";
	}
</script>

<!-- Dashboard Header -->
<div class="mb-8">
	<div class="flex items-start justify-between">
		<div>
			<h1 class="text-4xl font-bold gradient-text mb-2">Dashboard</h1>
			<p class="text-slate-400">Monitor and control your AI VTuber in real-time</p>
		</div>
		<div class="flex items-center gap-3">
			<button class="p-2.5 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-cyan-500/30 transition-all group">
				<RefreshCw class="w-5 h-5 text-slate-400 group-hover:text-cyan-400 transition-colors" />
			</button>
			<button class="px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-medium text-sm flex items-center gap-2 hover:opacity-90 transition-opacity shadow-lg shadow-cyan-500/25">
				<Sparkles class="w-4 h-4" />
				Quick Actions
			</button>
		</div>
	</div>
</div>

<!-- Hero Status Cards -->
<div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
	<!-- AI Status -->
	<div class="group relative overflow-hidden rounded-2xl p-5 bg-gradient-to-br from-cyan-500/10 via-cyan-500/5 to-transparent border border-cyan-500/20 hover:border-cyan-500/40 transition-all duration-300 hover-lift">
		<div class="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
		<div class="relative">
			<div class="flex items-center justify-between mb-4">
				<div class="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-cyan-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
					<Brain class="w-6 h-6 text-white" />
				</div>
				<div class="w-3 h-3 rounded-full {$AI_thinking ? 'bg-cyan-400 animate-pulse shadow-lg shadow-cyan-400/50' : 'bg-slate-600'}" />
			</div>
			<p class="text-sm text-slate-400 mb-1">AI Status</p>
			<p class="text-2xl font-bold {$AI_thinking ? 'text-cyan-400 text-glow-cyan' : 'text-slate-300'}">
				{$AI_thinking ? 'Thinking' : 'Idle'}
			</p>
		</div>
	</div>

	<!-- Voice Status -->
	<div class="group relative overflow-hidden rounded-2xl p-5 bg-gradient-to-br from-purple-500/10 via-purple-500/5 to-transparent border border-purple-500/20 hover:border-purple-500/40 transition-all duration-300 hover-lift">
		<div class="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
		<div class="relative">
			<div class="flex items-center justify-between mb-4">
				<div class="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center shadow-lg shadow-purple-500/30">
					<AudioLines class="w-6 h-6 text-white" />
				</div>
				<div class="w-3 h-3 rounded-full {$AI_speaking ? 'bg-purple-400 animate-pulse shadow-lg shadow-purple-400/50' : 'bg-slate-600'}" />
			</div>
			<p class="text-sm text-slate-400 mb-1">Voice Output</p>
			<p class="text-2xl font-bold {$AI_speaking ? 'text-purple-400 text-glow-purple' : 'text-slate-300'}">
				{$AI_speaking ? 'Speaking' : 'Silent'}
			</p>
		</div>
	</div>

	<!-- Listener Status -->
	<div class="group relative overflow-hidden rounded-2xl p-5 bg-gradient-to-br from-emerald-500/10 via-emerald-500/5 to-transparent border border-emerald-500/20 hover:border-emerald-500/40 transition-all duration-300 hover-lift">
		<div class="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
		<div class="relative">
			<div class="flex items-center justify-between mb-4">
				<div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-500/30">
					<Mic class="w-6 h-6 text-white" />
				</div>
				<div class="w-3 h-3 rounded-full {$human_speaking ? 'bg-emerald-400 animate-pulse shadow-lg shadow-emerald-400/50' : 'bg-slate-600'}" />
			</div>
			<p class="text-sm text-slate-400 mb-1">Listener</p>
			<p class="text-2xl font-bold {$human_speaking ? 'text-emerald-400' : 'text-slate-300'}">
				{$human_speaking ? 'Active' : 'Waiting'}
			</p>
		</div>
	</div>

	<!-- Patience Timer -->
	<div class="group relative overflow-hidden rounded-2xl p-5 bg-gradient-to-br from-amber-500/10 via-amber-500/5 to-transparent border border-amber-500/20 hover:border-amber-500/40 transition-all duration-300 hover-lift">
		<div class="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
		<div class="relative">
			<div class="flex items-center justify-between mb-4">
				<div class="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center shadow-lg shadow-amber-500/30">
					<Timer class="w-6 h-6 text-white" />
				</div>
				<span class="text-xs font-mono text-amber-400 bg-amber-500/20 px-2 py-1 rounded-lg">{$patiencePercent.toFixed(0)}%</span>
			</div>
			<p class="text-sm text-slate-400 mb-1">Patience</p>
			<p class="text-2xl font-bold text-amber-400">{$total_time || '0'}s</p>
		</div>
	</div>
</div>

<!-- Integration Quick Access -->
<div class="grid md:grid-cols-3 gap-4 mb-8">
	<!-- Discord Card -->
	<a href="/discord" class="group relative overflow-hidden rounded-2xl p-6 glass border border-white/10 hover:border-indigo-500/40 transition-all duration-300 hover-lift cursor-pointer">
		<div class="absolute top-0 right-0 w-48 h-48 bg-indigo-500/5 rounded-full blur-3xl" />
		<div class="relative">
			<div class="flex items-center justify-between mb-5">
				<div class="flex items-center gap-4">
					<div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
						<MessageSquare class="w-7 h-7 text-white" />
					</div>
					<div>
						<h3 class="text-lg font-semibold text-white group-hover:text-indigo-300 transition-colors">Discord</h3>
						<p class="text-sm text-slate-500">Bot Integration</p>
					</div>
				</div>
				<div class="flex items-center gap-2">
					{#if $discordConnected}
						<div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-500/30">
							<div class="status-online" />
							<span class="text-xs text-emerald-400 font-medium">Online</span>
						</div>
					{:else}
						<div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-500/20 border border-slate-500/30">
							<div class="status-offline" />
							<span class="text-xs text-slate-400 font-medium">Offline</span>
						</div>
					{/if}
					<ArrowUpRight class="w-5 h-5 text-slate-500 group-hover:text-indigo-400 transition-colors" />
				</div>
			</div>
			<div class="grid grid-cols-4 gap-3">
				<div class="p-3 rounded-xl bg-white/5 border border-white/5 text-center">
					<p class="text-xl font-bold text-indigo-400">{$discordStats.servers}</p>
					<p class="text-[10px] text-slate-500 uppercase tracking-wide">Servers</p>
				</div>
				<div class="p-3 rounded-xl bg-white/5 border border-white/5 text-center">
					<p class="text-xl font-bold text-violet-400">{$discordStats.channels}</p>
					<p class="text-[10px] text-slate-500 uppercase tracking-wide">Channels</p>
				</div>
				<div class="p-3 rounded-xl bg-white/5 border border-white/5 text-center">
					<p class="text-xl font-bold text-cyan-400">{$discordStats.messages}</p>
					<p class="text-[10px] text-slate-500 uppercase tracking-wide">Messages</p>
				</div>
				<div class="p-3 rounded-xl bg-white/5 border border-white/5 text-center">
					<p class="text-xl font-bold text-pink-400">{$discordStats.voiceConnections}</p>
					<p class="text-[10px] text-slate-500 uppercase tracking-wide">Voice</p>
				</div>
			</div>
		</div>
	</a>

	<!-- Twitch Card -->
	<a href="/twitch" class="group relative overflow-hidden rounded-2xl p-6 glass border border-white/10 hover:border-purple-500/40 transition-all duration-300 hover-lift cursor-pointer">
		<div class="absolute top-0 right-0 w-48 h-48 bg-purple-500/5 rounded-full blur-3xl" />
		<div class="relative">
			<div class="flex items-center justify-between mb-5">
				<div class="flex items-center gap-4">
					<div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-lg shadow-purple-500/30">
						<Radio class="w-7 h-7 text-white" />
					</div>
					<div>
						<h3 class="text-lg font-semibold text-white group-hover:text-purple-300 transition-colors">Twitch</h3>
						<p class="text-sm text-slate-500">Stream Integration</p>
					</div>
				</div>
				<div class="flex items-center gap-2">
					{#if $twitchConnected}
						<div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-500/30">
							<div class="status-online" />
							<span class="text-xs text-emerald-400 font-medium">Live</span>
						</div>
					{:else}
						<div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-500/20 border border-slate-500/30">
							<div class="status-offline" />
							<span class="text-xs text-slate-400 font-medium">Offline</span>
						</div>
					{/if}
					<ArrowUpRight class="w-5 h-5 text-slate-500 group-hover:text-purple-400 transition-colors" />
				</div>
			</div>
			<div class="grid grid-cols-4 gap-3">
				<div class="p-3 rounded-xl bg-white/5 border border-white/5 text-center">
					<p class="text-xl font-bold text-pink-400">{$twitchStats.viewers}</p>
					<p class="text-[10px] text-slate-500 uppercase tracking-wide">Viewers</p>
				</div>
				<div class="p-3 rounded-xl bg-white/5 border border-white/5 text-center">
					<p class="text-xl font-bold text-purple-400">{$twitchStats.followers.toLocaleString()}</p>
					<p class="text-[10px] text-slate-500 uppercase tracking-wide">Followers</p>
				</div>
				<div class="p-3 rounded-xl bg-white/5 border border-white/5 text-center">
					<p class="text-xl font-bold text-cyan-400">{$twitchStats.chatMessages}</p>
					<p class="text-[10px] text-slate-500 uppercase tracking-wide">Messages</p>
				</div>
				<div class="p-3 rounded-xl bg-white/5 border border-white/5 text-center">
					<p class="text-xl font-bold {$twitchStats.isLive ? 'text-red-400' : 'text-slate-500'}">{$twitchStats.isLive ? 'LIVE' : 'OFF'}</p>
					<p class="text-[10px] text-slate-500 uppercase tracking-wide">Status</p>
				</div>
			</div>
		</div>
	</a>

	<!-- VTube Studio Card -->
	<a href="/vtube" class="group relative overflow-hidden rounded-2xl p-6 glass border border-white/10 hover:border-pink-500/40 transition-all duration-300 hover-lift cursor-pointer">
		<div class="absolute top-0 right-0 w-48 h-48 bg-pink-500/5 rounded-full blur-3xl" />
		<div class="relative">
			<div class="flex items-center justify-between mb-5">
				<div class="flex items-center gap-4">
					<div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center shadow-lg shadow-pink-500/30">
						<Eye class="w-7 h-7 text-white" />
					</div>
					<div>
						<h3 class="text-lg font-semibold text-white group-hover:text-pink-300 transition-colors">VTube Studio</h3>
						<p class="text-sm text-slate-500">VTuber Control</p>
					</div>
				</div>
				<div class="flex items-center gap-2">
					{#if $vtsStatus.connected}
						<div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-500/30">
							<div class="status-online" />
							<span class="text-xs text-emerald-400 font-medium">Connected</span>
						</div>
					{:else}
						<div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-500/20 border border-slate-500/30">
							<div class="status-offline" />
							<span class="text-xs text-slate-400 font-medium">Offline</span>
						</div>
					{/if}
					<ArrowUpRight class="w-5 h-5 text-slate-500 group-hover:text-pink-400 transition-colors" />
				</div>
			</div>
			<div class="grid grid-cols-4 gap-3">
				<div class="p-3 rounded-xl bg-white/5 border border-white/5 text-center col-span-2">
					<p class="text-sm font-bold text-pink-400 truncate">{$vtsStatus.modelName || 'No Model'}</p>
					<p class="text-[10px] text-slate-500 uppercase tracking-wide">Current Model</p>
				</div>
				<div class="p-3 rounded-xl bg-white/5 border border-white/5 text-center">
					<p class="text-xl font-bold text-cyan-400 capitalize">{$vtsStatus.currentExpression || '—'}</p>
					<p class="text-[10px] text-slate-500 uppercase tracking-wide">Expression</p>
				</div>
				<div class="p-3 rounded-xl bg-white/5 border border-white/5 text-center">
					<p class="text-xl font-bold {$vtsStatus.modelLoaded ? 'text-emerald-400' : 'text-amber-400'}">{$vtsStatus.modelLoaded ? '✓' : '○'}</p>
					<p class="text-[10px] text-slate-500 uppercase tracking-wide">{$vtsStatus.modelLoaded ? 'Ready' : 'Load'}</p>
				</div>
			</div>
		</div>
	</a>
</div>

<!-- Main Control Grid -->
<div class="grid lg:grid-cols-3 gap-6">
	<!-- Messages Column -->
	<div class="lg:col-span-2 space-y-6">
		<!-- Current & Next Message Row -->
		<div class="grid md:grid-cols-2 gap-6">
			<!-- Current Message -->
			<div class="rounded-2xl glass border border-white/10 overflow-hidden">
				<div class="p-5 border-b border-white/5 flex items-center justify-between">
					<div class="flex items-center gap-3">
						<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-cyan-600 flex items-center justify-center">
							<MessageSquare class="w-5 h-5 text-white" />
						</div>
						<div>
							<h3 class="font-semibold text-white">Current Message</h3>
							<p class="text-xs text-slate-500">Now speaking</p>
						</div>
					</div>
					{#if $currentMessage}
						<div class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
					{/if}
				</div>
				<div class="p-5">
					<Textarea 
						disabled 
						placeholder="Waiting for message..." 
						class="resize-none h-40 bg-white/5 border-white/10 text-slate-300 placeholder:text-slate-600 focus:border-cyan-500/50 rounded-xl" 
						bind:value={$currentMessage}
					/>
					<Button on:click={abortMessage} class="w-full mt-4 bg-red-500/10 border border-red-500/30 text-red-400 hover:bg-red-500/20 hover:text-red-300 rounded-xl">
						<AlertTriangle class="mr-2 h-4 w-4" />
						Abort Message
					</Button>
				</div>
			</div>

			<!-- Next Message -->
			<div class="rounded-2xl glass border border-white/10 overflow-hidden">
				<div class="p-5 border-b border-white/5 flex items-center justify-between">
					<div class="flex items-center gap-3">
						<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center">
							<Zap class="w-5 h-5 text-white" />
						</div>
						<div>
							<h3 class="font-semibold text-white">Next Message</h3>
							<p class="text-xs text-slate-500">In queue</p>
						</div>
					</div>
					{#if $nextMessage}
						<div class="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
					{/if}
				</div>
				<div class="p-5">
					<Textarea 
						disabled 
						placeholder="No message queued..." 
						class="resize-none h-40 bg-white/5 border-white/10 text-slate-300 placeholder:text-slate-600 focus:border-purple-500/50 rounded-xl" 
						bind:value={$nextMessage}
					/>
					<Button on:click={cancelMessage} class="w-full mt-4 bg-amber-500/10 border border-amber-500/30 text-amber-400 hover:bg-amber-500/20 hover:text-amber-300 rounded-xl">
						<XOctagon class="mr-2 h-4 w-4" />
						Cancel Message
					</Button>
				</div>
			</div>
		</div>

		<!-- Twitch Chat -->
		<div class="rounded-2xl glass border border-white/10 overflow-hidden">
			<div class="p-5 border-b border-white/5 flex items-center justify-between">
				<div class="flex items-center gap-3">
					<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-violet-600 flex items-center justify-center">
						<Radio class="w-5 h-5 text-white" />
					</div>
					<div>
						<h3 class="font-semibold text-white">Twitch Chat</h3>
						<p class="text-xs text-slate-500">Live messages</p>
					</div>
				</div>
				<Switch bind:checked={$twitchChatEnabled} on:click={toggleTwitchChat} />
			</div>
			<div class="p-5">
				<Textarea 
					disabled 
					placeholder="Twitch messages will appear here..." 
					class="resize-none h-32 bg-white/5 border-white/10 text-slate-300 placeholder:text-slate-600 rounded-xl" 
					bind:value={$twitchChat}
				/>
			</div>
		</div>
	</div>

	<!-- Controls Column -->
	<div class="space-y-6">
		<!-- AI Engine Controls -->
		<div class="rounded-2xl glass border border-white/10 overflow-hidden">
			<div class="p-5 border-b border-white/5">
				<div class="flex items-center gap-3">
					<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center">
						<Power class="w-5 h-5 text-white" />
					</div>
					<div>
						<h3 class="font-semibold text-white">AI Engine Controls</h3>
						<p class="text-xs text-slate-500">Toggle capabilities</p>
					</div>
				</div>
			</div>
			<div class="p-5 space-y-3">
				<button
					on:click={toggleLLM}
					class="w-full p-4 rounded-xl transition-all duration-200 flex items-center gap-3 group
						{$LLMEnabled 
							? 'bg-emerald-500/10 border border-emerald-500/30 hover:bg-emerald-500/20' 
							: 'bg-red-500/10 border border-red-500/30 hover:bg-red-500/20'}"
				>
					<div class="w-10 h-10 rounded-lg bg-gradient-to-br {$LLMEnabled ? 'from-emerald-500 to-emerald-600' : 'from-red-500 to-red-600'} flex items-center justify-center">
						<BrainCircuit class="w-5 h-5 text-white" />
					</div>
					<div class="flex-1 text-left">
						<p class="font-medium {$LLMEnabled ? 'text-emerald-400' : 'text-red-400'}">Language Model</p>
						<p class="text-xs text-slate-500">{$LLMEnabled ? 'Processing enabled' : 'Processing disabled'}</p>
					</div>
					<div class="w-3 h-3 rounded-full {$LLMEnabled ? 'bg-emerald-400' : 'bg-red-400'}" />
				</button>

				<button
					on:click={toggleTTS}
					class="w-full p-4 rounded-xl transition-all duration-200 flex items-center gap-3 group
						{$TTSEnabled 
							? 'bg-emerald-500/10 border border-emerald-500/30 hover:bg-emerald-500/20' 
							: 'bg-red-500/10 border border-red-500/30 hover:bg-red-500/20'}"
				>
					<div class="w-10 h-10 rounded-lg bg-gradient-to-br {$TTSEnabled ? 'from-emerald-500 to-emerald-600' : 'from-red-500 to-red-600'} flex items-center justify-center">
						<Volume2 class="w-5 h-5 text-white" />
					</div>
					<div class="flex-1 text-left">
						<p class="font-medium {$TTSEnabled ? 'text-emerald-400' : 'text-red-400'}">Text to Speech</p>
						<p class="text-xs text-slate-500">{$TTSEnabled ? 'Voice output on' : 'Voice output off'}</p>
					</div>
					<div class="w-3 h-3 rounded-full {$TTSEnabled ? 'bg-emerald-400' : 'bg-red-400'}" />
				</button>

				<button
					on:click={toggleSTT}
					class="w-full p-4 rounded-xl transition-all duration-200 flex items-center gap-3 group
						{$STTEnabled 
							? 'bg-emerald-500/10 border border-emerald-500/30 hover:bg-emerald-500/20' 
							: 'bg-red-500/10 border border-red-500/30 hover:bg-red-500/20'}"
				>
					<div class="w-10 h-10 rounded-lg bg-gradient-to-br {$STTEnabled ? 'from-emerald-500 to-emerald-600' : 'from-red-500 to-red-600'} flex items-center justify-center">
						<Mic class="w-5 h-5 text-white" />
					</div>
					<div class="flex-1 text-left">
						<p class="font-medium {$STTEnabled ? 'text-emerald-400' : 'text-red-400'}">Speech to Text</p>
						<p class="text-xs text-slate-500">{$STTEnabled ? 'Listening active' : 'Listening paused'}</p>
					</div>
					<div class="w-3 h-3 rounded-full {$STTEnabled ? 'bg-emerald-400' : 'bg-red-400'}" />
				</button>

				<button
					on:click={toggleMovement}
					class="w-full p-4 rounded-xl transition-all duration-200 flex items-center gap-3 group
						{$movementEnabled 
							? 'bg-emerald-500/10 border border-emerald-500/30 hover:bg-emerald-500/20' 
							: 'bg-red-500/10 border border-red-500/30 hover:bg-red-500/20'}"
				>
					<div class="w-10 h-10 rounded-lg bg-gradient-to-br {$movementEnabled ? 'from-emerald-500 to-emerald-600' : 'from-red-500 to-red-600'} flex items-center justify-center">
						<Move class="w-5 h-5 text-white" />
					</div>
					<div class="flex-1 text-left">
						<p class="font-medium {$movementEnabled ? 'text-emerald-400' : 'text-red-400'}">Movement</p>
						<p class="text-xs text-slate-500">{$movementEnabled ? 'Animations on' : 'Animations off'}</p>
					</div>
					<div class="w-3 h-3 rounded-full {$movementEnabled ? 'bg-emerald-400' : 'bg-red-400'}" />
				</button>

				<!-- Vision Toggle -->
				<div class="p-4 rounded-xl bg-white/5 border border-white/10 flex items-center gap-3">
					<div class="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-cyan-600 flex items-center justify-center">
						<Eye class="w-5 h-5 text-white" />
					</div>
					<div class="flex-1">
						<p class="font-medium text-slate-300">Vision Mode</p>
						<p class="text-xs text-slate-500">Multimodal input</p>
					</div>
					<Switch bind:checked={$multimodalEnabled} on:click={toggleMultimodal} />
				</div>
			</div>
		</div>

		<!-- Music Player -->
		<div class="rounded-2xl glass border border-white/10 overflow-hidden">
			<div class="p-5 border-b border-white/5">
				<div class="flex items-center gap-3">
					<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-pink-600 flex items-center justify-center">
						<Music class="w-5 h-5 text-white" />
					</div>
					<div>
						<h3 class="font-semibold text-white">Music Player</h3>
						<p class="text-xs text-slate-500">Audio playback</p>
					</div>
				</div>
			</div>
			<div class="p-5">
				<Select.Root portal={null} bind:selected={$selectedAudio}>
					<Select.Trigger class="w-full bg-white/5 border-white/10 text-slate-300 rounded-xl mb-4">
						<Select.Value placeholder="Select a song"/>
					</Select.Trigger>
					<Select.Content class="bg-slate-900 border-white/10 rounded-xl">
						<Select.Group>
							<Select.Label class="text-slate-500">Playlist</Select.Label>
							{#each $songs as song}
								<Select.Item value={song.value} label={song.label} class="text-slate-300 hover:bg-white/10 rounded-lg">
									{song.label}
								</Select.Item>
							{/each}
						</Select.Group>
					</Select.Content>
					<Select.Input name="fileName" />
				</Select.Root>

				<div class="grid grid-cols-4 gap-2">
					<button on:click={playAudio} class="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20 transition-all">
						<PlayCircle class="w-5 h-5 mx-auto" />
					</button>
					<button on:click={pauseAudio} class="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 hover:bg-amber-500/20 transition-all">
						<Pause class="w-5 h-5 mx-auto" />
					</button>
					<button on:click={resumeAudio} class="p-3 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-400 hover:bg-blue-500/20 transition-all">
						<Play class="w-5 h-5 mx-auto" />
					</button>
					<button on:click={abortAudio} class="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 hover:bg-red-500/20 transition-all">
						<XOctagon class="w-5 h-5 mx-auto" />
					</button>
				</div>
			</div>
		</div>

		<!-- Quick Actions -->
		<div class="rounded-2xl glass border border-white/10 overflow-hidden">
			<div class="p-5 border-b border-white/5">
				<div class="flex items-center gap-3">
					<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
						<Lightbulb class="w-5 h-5 text-white" />
					</div>
					<div>
						<h3 class="font-semibold text-white">Quick Actions</h3>
						<p class="text-xs text-slate-500">Trigger behaviors</p>
					</div>
				</div>
			</div>
			<div class="p-5 space-y-4">
				<button 
					on:click={funFact} 
					class="w-full p-4 rounded-xl bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-500/30 text-cyan-400 hover:from-cyan-500/30 hover:to-purple-500/30 transition-all flex items-center justify-center gap-3 group"
				>
					<Sparkles class="w-5 h-5 group-hover:rotate-12 transition-transform" />
					<span class="font-medium">Generate Fun Fact</span>
				</button>

				<div class="flex gap-2">
					<Input 
						placeholder="Enter a topic..." 
						bind:value={topic}
						class="flex-1 bg-white/5 border-white/10 text-slate-300 placeholder:text-slate-600 focus:border-cyan-500/50 rounded-xl"
					/>
					<Button 
						size="icon" 
						on:click={newTopic}
						class="bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/30 rounded-xl w-12"
					>
						<Send class="h-4 w-4" />
					</Button>
				</div>
			</div>
		</div>

		<!-- Status Indicators -->
		<div class="rounded-2xl glass border border-white/10 overflow-hidden">
			<div class="p-5 border-b border-white/5">
				<div class="flex items-center gap-3">
					<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
						<Activity class="w-5 h-5 text-white" />
					</div>
					<div>
						<h3 class="font-semibold text-white">Live Status</h3>
						<p class="text-xs text-slate-500">Real-time indicators</p>
					</div>
				</div>
			</div>
			<div class="p-5 space-y-3">
				<div class="flex items-center justify-between p-3 rounded-xl {$AI_thinking ? 'bg-cyan-500/10 border border-cyan-500/30' : 'bg-white/5 border border-white/10'}">
					<div class="flex items-center gap-3">
						<BrainCircuit class="w-5 h-5 {$AI_thinking ? 'text-cyan-400' : 'text-slate-500'}" />
						<span class="text-sm {$AI_thinking ? 'text-cyan-400' : 'text-slate-400'}">AI Processing</span>
					</div>
					<div class="w-2.5 h-2.5 rounded-full {$AI_thinking ? 'bg-cyan-400 animate-pulse' : 'bg-slate-600'}" />
				</div>

				<div class="flex items-center justify-between p-3 rounded-xl {$AI_speaking ? 'bg-purple-500/10 border border-purple-500/30' : 'bg-white/5 border border-white/10'}">
					<div class="flex items-center gap-3">
						<Volume2 class="w-5 h-5 {$AI_speaking ? 'text-purple-400' : 'text-slate-500'}" />
						<span class="text-sm {$AI_speaking ? 'text-purple-400' : 'text-slate-400'}">Voice Output</span>
					</div>
					<div class="w-2.5 h-2.5 rounded-full {$AI_speaking ? 'bg-purple-400 animate-pulse' : 'bg-slate-600'}" />
				</div>

				<div class="flex items-center justify-between p-3 rounded-xl {$human_speaking ? 'bg-emerald-500/10 border border-emerald-500/30' : 'bg-white/5 border border-white/10'}">
					<div class="flex items-center gap-3">
						<Mic class="w-5 h-5 {$human_speaking ? 'text-emerald-400' : 'text-slate-500'}" />
						<span class="text-sm {$human_speaking ? 'text-emerald-400' : 'text-slate-400'}">Audio Input</span>
					</div>
					<div class="w-2.5 h-2.5 rounded-full {$human_speaking ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}" />
				</div>

				<!-- Patience Progress -->
				<div class="p-3 rounded-xl bg-white/5 border border-white/10">
					<div class="flex items-center justify-between mb-2">
						<span class="text-sm text-slate-400">Patience Timer</span>
						<span class="text-sm font-mono text-amber-400">{$total_time || '0'}s</span>
					</div>
					<Progress value={$patiencePercent} class="h-2" />
				</div>
			</div>
		</div>
	</div>
</div>
