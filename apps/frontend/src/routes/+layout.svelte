<script lang="ts">
	import * as Avatar from "$lib/components/ui/avatar";
	import { ModeWatcher, toggleMode } from "mode-watcher";
	import "../app.pcss";

	import { Button } from "$lib/components/ui/button";
	import { 
		Sun, Moon, Menu, X, BarChart3, Settings,
		Zap, Brain, MessageSquare, Terminal,
		Wifi, WifiOff, ChevronRight, Sparkles, Radio, Eye, Shield, Database,
		Activity, Bell, Search, Command, Layers, Cpu, Headphones, Globe, Server
	} from "lucide-svelte";
	import { Toaster } from "$lib/components/ui/sonner";
	import { page } from "$app/stores";

	import { socket, notifications, unreadNotifications, markNotificationRead, markAllNotificationsRead, clearNotifications, coreConnected, coreStatus } from "./socketio";

	let isConnected = false;
	let sidebarOpen = false;
	let sidebarCollapsed = false;
	let currentTime = new Date().toLocaleTimeString('en-US', { hour12: false });
	let currentDate = new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
	let searchOpen = false;
	let notificationsOpen = false;

	function toggleNotifications() {
		notificationsOpen = !notificationsOpen;
	}

	function closeNotifications() {
		notificationsOpen = false;
	}

	function getNotificationIcon(type: string) {
		switch(type) {
			case 'success': return '✓';
			case 'warning': return '⚠';
			case 'error': return '✕';
			default: return 'ℹ';
		}
	}

	function getNotificationColor(type: string) {
		switch(type) {
			case 'success': return 'text-emerald-400 bg-emerald-500/20';
			case 'warning': return 'text-amber-400 bg-amber-500/20';
			case 'error': return 'text-red-400 bg-red-500/20';
			default: return 'text-cyan-400 bg-cyan-500/20';
		}
	}

	// Update clock
	setInterval(() => {
		currentTime = new Date().toLocaleTimeString('en-US', { hour12: false });
		currentDate = new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
	}, 1000);

	socket.on("connect", () => {
		isConnected = true;
	});
	socket.on("disconnect", () => {
		isConnected = false;
	});

	function toggleSidebar() {
		sidebarOpen = !sidebarOpen;
	}

	function toggleCollapse() {
		sidebarCollapsed = !sidebarCollapsed;
	}

	// Navigation items with icons and colors
	const navItems = [
		{ href: "/", label: "Dashboard", icon: Activity, color: "cyan" },
		{ href: "/services", label: "Services", icon: Server, color: "blue" },
		{ href: "/metrics", label: "Metrics", icon: BarChart3, color: "purple" },
		{ href: "/logs", label: "System Logs", icon: Terminal, color: "emerald" },
		{ href: "/config", label: "Settings", icon: Settings, color: "amber" },
	];

	const aiItems = [
		{ href: "/lobotomy", label: "Lobotomy", icon: Brain, color: "pink" },
		{ href: "/moderation", label: "Moderation", icon: Shield, color: "red" },
		{ href: "/memory", label: "Memory Bank", icon: Database, color: "violet" },
	];

	const integrationItems = [
		{ href: "/discord", label: "Discord", icon: MessageSquare, color: "indigo" },
		{ href: "/twitch", label: "Twitch", icon: Radio, color: "purple" },
		{ href: "/vtube", label: "VTube Studio", icon: Eye, color: "pink" },
	];

	const colorMap: Record<string, string> = {
		cyan: "from-cyan-500 to-cyan-600",
		blue: "from-blue-500 to-blue-600",
		purple: "from-purple-500 to-purple-600",
		emerald: "from-emerald-500 to-emerald-600",
		amber: "from-amber-500 to-amber-600",
		pink: "from-pink-500 to-pink-600",
		red: "from-red-500 to-red-600",
		violet: "from-violet-500 to-violet-600",
		indigo: "from-indigo-500 to-indigo-600",
	};

	const activeColorMap: Record<string, string> = {
		cyan: "text-cyan-400 border-cyan-500/40 bg-cyan-500/10",
		blue: "text-blue-400 border-blue-500/40 bg-blue-500/10",
		purple: "text-purple-400 border-purple-500/40 bg-purple-500/10",
		emerald: "text-emerald-400 border-emerald-500/40 bg-emerald-500/10",
		amber: "text-amber-400 border-amber-500/40 bg-amber-500/10",
		pink: "text-pink-400 border-pink-500/40 bg-pink-500/10",
		red: "text-red-400 border-red-500/40 bg-red-500/10",
		violet: "text-violet-400 border-violet-500/40 bg-violet-500/10",
		indigo: "text-indigo-400 border-indigo-500/40 bg-indigo-500/10",
	};

	$: currentPath = $page.url.pathname;
</script>

<svelte:head>
	<title>Voxelle Control Panel</title>
	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous">
	<link href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@300..700&display=swap" rel="stylesheet">
</svelte:head>

<Toaster richColors position="bottom-right" />
<ModeWatcher />

<div class="h-screen flex bg-[hsl(240,10%,4%)] overflow-hidden">
	<!-- Animated Background -->
	<div class="fixed inset-0 pointer-events-none">
		<!-- Grid pattern -->
		<div class="absolute inset-0 bg-grid opacity-50" />
		<!-- Gradient orbs -->
		<div class="absolute top-0 left-1/4 w-[600px] h-[600px] bg-cyan-500/10 rounded-full blur-[120px] animate-pulse" style="animation-duration: 8s;" />
		<div class="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-[100px] animate-pulse" style="animation-duration: 10s;" />
		<div class="absolute top-1/2 left-1/2 w-[400px] h-[400px] bg-pink-500/5 rounded-full blur-[80px] animate-pulse" style="animation-duration: 12s;" />
		<!-- Noise texture -->
		<div class="absolute inset-0 noise opacity-30" />
	</div>
	
	<!-- Sidebar -->
	<aside class="hidden lg:flex {sidebarCollapsed ? 'w-20' : 'w-72'} glass-heavy flex-col relative z-20 transition-all duration-300">
		<!-- Logo Section -->
		<div class="p-5 border-b border-white/5">
			<div class="flex items-center gap-3">
				<div class="relative group">
					<div class="absolute -inset-1 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-xl blur-sm opacity-60 group-hover:opacity-100 transition-opacity" />
					<div class="relative w-11 h-11 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center shadow-lg">
						<Zap class="w-6 h-6 text-white" />
					</div>
				</div>
				{#if !sidebarCollapsed}
					<div class="flex-1">
						<h1 class="text-xl font-bold gradient-text font-['Space_Grotesk']">Voxelle</h1>
						<p class="text-[11px] text-slate-500 font-medium tracking-wide">AI VTUBER PLATFORM</p>
					</div>
					<button on:click={toggleCollapse} class="p-1.5 hover:bg-white/5 rounded-lg transition-colors">
						<ChevronRight class="w-4 h-4 text-slate-500 rotate-180" />
					</button>
				{/if}
			</div>
		</div>

		<!-- Navigation -->
		<nav class="flex-1 px-3 py-5 space-y-6 overflow-y-auto scrollbar-thin">
			<!-- Main Navigation -->
			<div>
				{#if !sidebarCollapsed}
					<p class="px-3 mb-3 text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em]">Main</p>
				{/if}
				<div class="space-y-1">
					{#each navItems as item}
						<a 
							href={item.href} 
							class="flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative
								{currentPath === item.href 
									? `${activeColorMap[item.color]} border` 
									: 'text-slate-400 hover:text-white hover:bg-white/5'}"
							title={sidebarCollapsed ? item.label : undefined}
						>
							<div class="w-8 h-8 rounded-lg bg-gradient-to-br {colorMap[item.color]} flex items-center justify-center shadow-lg {currentPath === item.href ? 'opacity-100' : 'opacity-60 group-hover:opacity-100'} transition-opacity">
								<svelte:component this={item.icon} class="w-4 h-4 text-white" />
							</div>
							{#if !sidebarCollapsed}
								<span class="font-medium text-sm">{item.label}</span>
								{#if currentPath === item.href}
									<div class="ml-auto w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
								{/if}
							{/if}
						</a>
					{/each}
				</div>
			</div>

			<!-- AI Controls -->
			<div>
				{#if !sidebarCollapsed}
					<p class="px-3 mb-3 text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em]">AI Controls</p>
				{/if}
				<div class="space-y-1">
					{#each aiItems as item}
						<a 
							href={item.href} 
							class="flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative
								{currentPath === item.href 
									? `${activeColorMap[item.color]} border` 
									: 'text-slate-400 hover:text-white hover:bg-white/5'}"
							title={sidebarCollapsed ? item.label : undefined}
						>
							<div class="w-8 h-8 rounded-lg bg-gradient-to-br {colorMap[item.color]} flex items-center justify-center shadow-lg {currentPath === item.href ? 'opacity-100' : 'opacity-60 group-hover:opacity-100'} transition-opacity">
								<svelte:component this={item.icon} class="w-4 h-4 text-white" />
							</div>
							{#if !sidebarCollapsed}
								<span class="font-medium text-sm">{item.label}</span>
							{/if}
						</a>
					{/each}
				</div>
			</div>

			<!-- Integrations -->
			<div>
				{#if !sidebarCollapsed}
					<p class="px-3 mb-3 text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em]">Integrations</p>
				{/if}
				<div class="space-y-1">
					{#each integrationItems as item}
						<a 
							href={item.href} 
							class="flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative
								{currentPath === item.href 
									? `${activeColorMap[item.color]} border` 
									: 'text-slate-400 hover:text-white hover:bg-white/5'}"
							title={sidebarCollapsed ? item.label : undefined}
						>
							<div class="w-8 h-8 rounded-lg bg-gradient-to-br {colorMap[item.color]} flex items-center justify-center shadow-lg {currentPath === item.href ? 'opacity-100' : 'opacity-60 group-hover:opacity-100'} transition-opacity">
								<svelte:component this={item.icon} class="w-4 h-4 text-white" />
							</div>
							{#if !sidebarCollapsed}
								<span class="font-medium text-sm">{item.label}</span>
							{/if}
						</a>
					{/each}
				</div>
			</div>
		</nav>

		<!-- Connection Status -->
		<div class="p-4 border-t border-white/5 space-y-2">
			<!-- Core Server Status -->
			<div class="flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-300
				{$coreConnected ? 'bg-emerald-500/10 border border-emerald-500/20' : 'bg-red-500/10 border border-red-500/20'}">
				{#if $coreConnected}
					<div class="relative">
						<Cpu class="w-4 h-4 text-emerald-400" />
						<div class="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
					</div>
					{#if !sidebarCollapsed}
						<div class="flex-1">
							<p class="text-xs font-semibold text-emerald-400">Core Online</p>
							<p class="text-[9px] text-emerald-400/60">v{$coreStatus.version}</p>
						</div>
					{/if}
				{:else}
					<Cpu class="w-4 h-4 text-red-400" />
					{#if !sidebarCollapsed}
						<div class="flex-1">
							<p class="text-xs font-semibold text-red-400">Core Offline</p>
							<p class="text-[9px] text-red-400/60">Not connected</p>
						</div>
					{/if}
				{/if}
			</div>
			<!-- WebSocket Status -->
			<div class="flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-300
				{isConnected ? 'bg-cyan-500/10 border border-cyan-500/20' : 'bg-amber-500/10 border border-amber-500/20'}">
				{#if isConnected}
					<div class="relative">
						<Wifi class="w-4 h-4 text-cyan-400" />
					</div>
					{#if !sidebarCollapsed}
						<div class="flex-1">
							<p class="text-xs font-semibold text-cyan-400">WebSocket</p>
							<p class="text-[9px] text-cyan-400/60">Connected</p>
						</div>
					{/if}
				{:else}
					<WifiOff class="w-4 h-4 text-amber-400" />
					{#if !sidebarCollapsed}
						<div class="flex-1">
							<p class="text-xs font-semibold text-amber-400">WebSocket</p>
							<p class="text-[9px] text-amber-400/60">Reconnecting...</p>
						</div>
					{/if}
				{/if}
			</div>
		</div>
	</aside>

	<!-- Mobile Sidebar Overlay -->
	{#if sidebarOpen}
		<div 
			class="lg:hidden fixed inset-0 z-40 bg-black/80 backdrop-blur-sm" 
			on:click={toggleSidebar} 
			on:keydown={(e) => e.key === 'Escape' && toggleSidebar()} 
			role="button" 
			tabindex="0" 
		/>
	{/if}

	<!-- Main Content Area -->
	<div class="flex-1 flex flex-col overflow-hidden relative z-10">
		<!-- Top Bar -->
		<header class="h-16 glass-subtle px-6 flex items-center justify-between border-b border-white/5">
			<div class="flex items-center gap-4">
				<!-- Mobile menu toggle -->
				<button on:click={toggleSidebar} class="lg:hidden p-2 hover:bg-white/5 rounded-xl transition-colors">
					{#if sidebarOpen}
						<X class="w-5 h-5 text-slate-400" />
					{:else}
						<Menu class="w-5 h-5 text-slate-400" />
					{/if}
				</button>
				
				<!-- Search bar -->
				<div class="hidden md:flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/5 hover:border-white/10 transition-colors cursor-pointer group">
					<Search class="w-4 h-4 text-slate-500 group-hover:text-slate-400" />
					<span class="text-sm text-slate-500 group-hover:text-slate-400">Search...</span>
					<div class="flex items-center gap-1 ml-8">
						<kbd class="px-1.5 py-0.5 text-[10px] bg-white/5 rounded text-slate-500 font-mono">⌘</kbd>
						<kbd class="px-1.5 py-0.5 text-[10px] bg-white/5 rounded text-slate-500 font-mono">K</kbd>
					</div>
				</div>
			</div>

			<div class="flex items-center gap-4">
				<!-- Date & Time -->
				<div class="hidden lg:flex flex-col items-end">
					<span class="text-sm font-mono text-cyan-400 font-medium">{currentTime}</span>
					<span class="text-[10px] text-slate-500">{currentDate}</span>
				</div>

				<div class="w-px h-8 bg-white/10 hidden lg:block" />

				<!-- Quick Status Indicators -->
				<div class="hidden md:flex items-center gap-3 px-3 py-1.5 rounded-xl bg-white/5">
					<div class="flex items-center gap-1.5" title="Core Server">
						<div class="status-online" />
						<span class="text-xs text-slate-400">Core</span>
					</div>
					<div class="flex items-center gap-1.5" title="TTS Engine">
						<div class="status-online" />
						<span class="text-xs text-slate-400">TTS</span>
					</div>
					<div class="flex items-center gap-1.5" title="STT Engine">
						<div class="status-online" />
						<span class="text-xs text-slate-400">STT</span>
					</div>
				</div>

				<!-- Notifications -->
				<div class="relative">
					<button 
						on:click={toggleNotifications}
						class="relative p-2 hover:bg-white/5 rounded-xl transition-colors"
					>
						<Bell class="w-5 h-5 text-slate-400" />
						{#if $unreadNotifications > 0}
							<div class="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] rounded-full bg-cyan-500 text-xs font-bold text-white flex items-center justify-center px-1">
								{$unreadNotifications > 9 ? '9+' : $unreadNotifications}
							</div>
						{/if}
					</button>

					<!-- Notifications Dropdown -->
					{#if notificationsOpen}
						<div 
							class="absolute right-0 top-full mt-2 w-80 max-h-96 glass-heavy border border-white/10 rounded-2xl shadow-2xl overflow-hidden z-50"
						>
							<div class="p-4 border-b border-white/10 flex items-center justify-between">
								<h3 class="font-semibold text-white">Notifications</h3>
								<div class="flex gap-2">
									{#if $notifications.length > 0}
										<button 
											on:click={() => markAllNotificationsRead()}
											class="text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
										>
											Mark all read
										</button>
										<button 
											on:click={() => clearNotifications()}
											class="text-xs text-slate-400 hover:text-slate-300 transition-colors"
										>
											Clear
										</button>
									{/if}
								</div>
							</div>
							<div class="max-h-72 overflow-y-auto scrollbar-thin">
								{#if $notifications.length > 0}
									{#each $notifications as notif (notif.id)}
										<button
											on:click={() => markNotificationRead(notif.id)}
											class="w-full p-4 border-b border-white/5 hover:bg-white/5 transition-colors text-left flex gap-3 {notif.read ? 'opacity-60' : ''}"
										>
											<div class="w-8 h-8 rounded-lg {getNotificationColor(notif.type)} flex items-center justify-center flex-shrink-0">
												{getNotificationIcon(notif.type)}
											</div>
											<div class="flex-1 min-w-0">
												<p class="text-sm font-medium text-white truncate">{notif.title}</p>
												<p class="text-xs text-slate-400 line-clamp-2">{notif.message}</p>
												<p class="text-[10px] text-slate-500 mt-1">{notif.timestamp}</p>
											</div>
											{#if !notif.read}
												<div class="w-2 h-2 rounded-full bg-cyan-400 flex-shrink-0 mt-1" />
											{/if}
										</button>
									{/each}
								{:else}
									<div class="p-8 text-center">
										<Bell class="w-8 h-8 text-slate-600 mx-auto mb-2" />
										<p class="text-sm text-slate-500">No notifications</p>
									</div>
								{/if}
							</div>
						</div>
					{/if}
				</div>

				<!-- Theme Toggle -->
				<Button on:click={toggleMode} variant="ghost" size="icon" class="text-slate-400 hover:text-white hover:bg-white/10 rounded-xl">
					<Sun class="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
					<Moon class="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
				</Button>

				<!-- User Avatar -->
				<div class="relative group cursor-pointer">
					<div class="absolute -inset-1 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full blur-sm opacity-40 group-hover:opacity-70 transition-opacity" />
					<Avatar.Root class="relative ring-2 ring-white/10 ring-offset-2 ring-offset-[hsl(240,10%,4%)]">
						<Avatar.Image src="https://api.dicebear.com/7.x/bottts/svg?seed=voxelle&backgroundColor=1e293b" alt="@voxelle" />
						<Avatar.Fallback class="bg-gradient-to-br from-cyan-500 to-purple-600 text-white font-bold">VX</Avatar.Fallback>
					</Avatar.Root>
				</div>
			</div>
		</header>

		<!-- Page Content -->
		<main class="flex-1 overflow-auto p-6 scrollbar-thin">
			<slot />
		</main>

		<!-- Footer Status Bar -->
		<footer class="h-8 glass-subtle border-t border-white/5 px-6 flex items-center justify-between text-[11px]">
			<div class="flex items-center gap-4 text-slate-500">
				<span class="flex items-center gap-1.5">
					<Cpu class="w-3 h-3" />
					<span>CPU: 23%</span>
				</span>
				<span class="flex items-center gap-1.5">
					<Layers class="w-3 h-3" />
					<span>RAM: 4.2 GB</span>
				</span>
				<span class="flex items-center gap-1.5">
					<Globe class="w-3 h-3" />
					<span>Latency: 12ms</span>
				</span>
			</div>
			<div class="flex items-center gap-2 text-slate-500">
				<span class="text-cyan-400">●</span>
				<span>Voxelle v2.0.0</span>
			</div>
		</footer>
	</div>
</div>

<style>
	:global(body) {
		font-family: 'Inter', system-ui, sans-serif;
	}
	
	:global(.font-mono) {
		font-family: 'JetBrains Mono', monospace;
	}

	:global(h1, h2, h3) {
		font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif;
	}
</style>
