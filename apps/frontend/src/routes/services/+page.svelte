<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { API_BASE, coreConnected } from '../socketio';
	import { 
		AlertCircle, CheckCircle2, Zap, Settings, Play, Power, Server,
		Activity, Cpu, HardDrive, Clock, RefreshCw, Wifi, WifiOff,
		TrendingUp, AlertTriangle, XCircle, RotateCcw, Sparkles, 
		Globe, Layers, Radio, Eye, Database, MonitorDot, Gauge, Disc3
	} from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import { Progress } from '$lib/components/ui/progress';

	interface Service {
		name: string;
		id: string;
		status: 'running' | 'stopped' | 'error' | 'starting' | 'not_installed';
		uptime: number;
		memory: number;
		cpu: number;
		version?: string;
		port?: number;
		installed?: boolean;
		description?: string;
	}

	interface SystemMetrics {
		cpu: number;
		memory: number;
		memoryUsed: number;
		memoryTotal: number;
		disk: number;
		diskUsed: number;
		diskTotal: number;
		uptime: number;
		process: {
			memory: number;
			cpu: number;
		};
	}

	let services: Service[] = [];
	let metrics: SystemMetrics = {
		cpu: 0, memory: 0, memoryUsed: 0, memoryTotal: 0,
		disk: 0, diskUsed: 0, diskTotal: 0, uptime: 0,
		process: { memory: 0, cpu: 0 }
	};
	let loading = true;
	let error = '';
	let selectedService: string | null = null;
	let refreshInterval: ReturnType<typeof setInterval>;

	// Animated values for smooth transitions
	let animatedCpu = 0;
	let animatedMemory = 0;

	function formatUptime(ms: number): string {
		const seconds = Math.floor(ms / 1000);
		const minutes = Math.floor(seconds / 60);
		const hours = Math.floor(minutes / 60);
		const days = Math.floor(hours / 24);

		if (days > 0) return `${days}d ${hours % 24}h ${minutes % 60}m`;
		if (hours > 0) return `${hours}h ${minutes % 60}m`;
		if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
		return `${seconds}s`;
	}

	function formatBytes(bytes: number): string {
		if (bytes === 0) return '0 B';
		const k = 1024;
		const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
	}

	function getStatusConfig(status: string) {
		switch (status) {
			case 'running':
				return { 
					icon: CheckCircle2, 
					color: 'emerald',
					glow: 'shadow-emerald-500/50',
					bg: 'from-emerald-500/20 to-teal-500/20',
					border: 'border-emerald-500/30',
					text: 'text-emerald-400',
					pulse: true
				};
			case 'error':
				return { 
					icon: XCircle, 
					color: 'red',
					glow: 'shadow-red-500/50',
					bg: 'from-red-500/20 to-rose-500/20',
					border: 'border-red-500/30',
					text: 'text-red-400',
					pulse: false
				};
			case 'starting':
				return { 
					icon: RefreshCw, 
					color: 'amber',
					glow: 'shadow-amber-500/50',
					bg: 'from-amber-500/20 to-orange-500/20',
					border: 'border-amber-500/30',
					text: 'text-amber-400',
					pulse: true
				};
			case 'not_installed':
				return { 
					icon: AlertTriangle, 
					color: 'slate',
					glow: '',
					bg: 'from-slate-500/10 to-slate-600/10',
					border: 'border-slate-500/20',
					text: 'text-slate-500',
					pulse: false
				};
			default:
				return { 
					icon: Power, 
					color: 'slate',
					glow: '',
					bg: 'from-slate-500/20 to-gray-500/20',
					border: 'border-slate-500/30',
					text: 'text-slate-400',
					pulse: false
				};
		}
	}

	async function fetchServices() {
		try {
			const res = await fetch(`${API_BASE}/api/services`);
			const data = await res.json();
			if (data.status === 200) {
				services = data.response;
			}
		} catch (e) {
			console.error('Failed to fetch services');
		}
	}

	async function fetchMetrics() {
		try {
			const res = await fetch(`${API_BASE}/api/system/metrics`);
			const data = await res.json();
			if (data.status === 200) {
				metrics = data.response;
				// Animate values
				animatedCpu = metrics.cpu;
				animatedMemory = metrics.memory;
			}
		} catch (e) {
			console.error('Failed to fetch metrics');
		}
	}

	async function refreshAll() {
		loading = true;
		await Promise.all([fetchServices(), fetchMetrics()]);
		loading = false;
	}

	onMount(() => {
		refreshAll();
		// Refresh every 3 seconds for live updates
		refreshInterval = setInterval(() => {
			fetchServices();
			fetchMetrics();
		}, 3000);
	});

	onDestroy(() => {
		if (refreshInterval) clearInterval(refreshInterval);
	});

	$: runningServices = services.filter(s => s.status === 'running').length;
	$: totalServices = services.filter(s => s.status !== 'not_installed').length;
</script>

<!-- Animated Background -->
<div class="fixed inset-0 pointer-events-none overflow-hidden -z-10">
	<div class="absolute top-1/4 -left-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl animate-pulse"></div>
	<div class="absolute bottom-1/4 -right-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl animate-pulse" style="animation-delay: 1s"></div>
</div>

<!-- Header -->
<div class="mb-8 relative">
	<div class="flex items-center justify-between">
		<div class="flex items-center gap-5">
			<div class="relative">
				<div class="absolute inset-0 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl blur-xl opacity-50 animate-pulse"></div>
				<div class="relative w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-2xl shadow-blue-500/30">
					<Layers class="w-8 h-8 text-white" />
				</div>
			</div>
			<div>
				<h1 class="text-4xl font-bold bg-gradient-to-r from-white via-blue-100 to-indigo-200 bg-clip-text text-transparent font-display">
					System Services
				</h1>
				<p class="text-slate-400 mt-1 flex items-center gap-2">
					<span class="relative flex h-2 w-2">
						<span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
						<span class="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
					</span>
					Real-time monitoring & control
				</p>
			</div>
		</div>
		<div class="flex items-center gap-3">
			{#if !$coreConnected}
				<Badge class="bg-red-500/20 border border-red-500/30 text-red-400 gap-1.5 animate-pulse">
					<WifiOff class="w-3 h-3" />
					Offline
				</Badge>
			{/if}
			<Button 
				on:click={refreshAll} 
				variant="outline" 
				class="border-white/10 text-slate-400 hover:text-white rounded-xl transition-all duration-300 hover:border-blue-500/50 hover:bg-blue-500/10 gap-2"
			>
				<RefreshCw class="w-4 h-4 {loading ? 'animate-spin' : ''}" />
				Refresh
			</Button>
		</div>
	</div>
</div>

<!-- System Vitals - Futuristic Dashboard -->
<div class="mb-8">
	<div class="grid lg:grid-cols-4 gap-4">
		<!-- CPU Gauge -->
		<div class="relative group">
			<div class="absolute inset-0 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
			<div class="relative p-6 rounded-2xl glass border border-white/10 overflow-hidden">
				<div class="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2"></div>
				<div class="relative">
					<div class="flex items-center justify-between mb-4">
						<div class="flex items-center gap-3">
							<div class="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
								<Cpu class="w-6 h-6 text-white" />
							</div>
							<div>
								<p class="text-xs text-slate-500 uppercase tracking-wider font-medium">CPU Usage</p>
								<p class="text-3xl font-bold text-cyan-400 font-display tabular-nums">{metrics.cpu.toFixed(1)}%</p>
							</div>
						</div>
					</div>
					<div class="relative h-2 bg-black/30 rounded-full overflow-hidden">
						<div 
							class="absolute inset-y-0 left-0 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-500 ease-out"
							style="width: {metrics.cpu}%"
						></div>
						<div 
							class="absolute inset-y-0 left-0 bg-gradient-to-r from-cyan-400 to-blue-400 rounded-full blur-sm opacity-50 transition-all duration-500"
							style="width: {metrics.cpu}%"
						></div>
					</div>
				</div>
			</div>
		</div>

		<!-- Memory Gauge -->
		<div class="relative group">
			<div class="absolute inset-0 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
			<div class="relative p-6 rounded-2xl glass border border-white/10 overflow-hidden">
				<div class="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2"></div>
				<div class="relative">
					<div class="flex items-center justify-between mb-4">
						<div class="flex items-center gap-3">
							<div class="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-lg shadow-purple-500/30">
								<HardDrive class="w-6 h-6 text-white" />
							</div>
							<div>
								<p class="text-xs text-slate-500 uppercase tracking-wider font-medium">Memory</p>
								<p class="text-3xl font-bold text-purple-400 font-display tabular-nums">{metrics.memory.toFixed(1)}%</p>
							</div>
						</div>
					</div>
					<div class="relative h-2 bg-black/30 rounded-full overflow-hidden">
						<div 
							class="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500 ease-out"
							style="width: {metrics.memory}%"
						></div>
					</div>
					<p class="text-xs text-slate-500 mt-2">{formatBytes(metrics.memoryUsed)} / {formatBytes(metrics.memoryTotal)}</p>
				</div>
			</div>
		</div>

		<!-- Disk Usage -->
		<div class="relative group">
			<div class="absolute inset-0 bg-gradient-to-br from-amber-500/20 to-orange-500/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
			<div class="relative p-6 rounded-2xl glass border border-white/10 overflow-hidden">
				<div class="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2"></div>
				<div class="relative">
					<div class="flex items-center justify-between mb-4">
						<div class="flex items-center gap-3">
							<div class="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-amber-500/30">
								<Disc3 class="w-6 h-6 text-white" />
							</div>
							<div>
								<p class="text-xs text-slate-500 uppercase tracking-wider font-medium">Disk</p>
								<p class="text-3xl font-bold text-amber-400 font-display tabular-nums">{metrics.disk.toFixed(1)}%</p>
							</div>
						</div>
					</div>
					<div class="relative h-2 bg-black/30 rounded-full overflow-hidden">
						<div 
							class="absolute inset-y-0 left-0 bg-gradient-to-r from-amber-500 to-orange-500 rounded-full transition-all duration-500 ease-out"
							style="width: {metrics.disk}%"
						></div>
					</div>
					<p class="text-xs text-slate-500 mt-2">{formatBytes(metrics.diskUsed)} / {formatBytes(metrics.diskTotal)}</p>
				</div>
			</div>
		</div>

		<!-- Uptime -->
		<div class="relative group">
			<div class="absolute inset-0 bg-gradient-to-br from-emerald-500/20 to-teal-500/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
			<div class="relative p-6 rounded-2xl glass border border-white/10 overflow-hidden">
				<div class="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2"></div>
				<div class="relative">
					<div class="flex items-center gap-3 mb-4">
						<div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/30">
							<Clock class="w-6 h-6 text-white" />
						</div>
						<div>
							<p class="text-xs text-slate-500 uppercase tracking-wider font-medium">Uptime</p>
							<p class="text-2xl font-bold text-emerald-400 font-display">{formatUptime(metrics.uptime * 1000)}</p>
						</div>
					</div>
					<div class="flex items-center gap-2 text-xs">
						<span class="flex items-center gap-1 text-emerald-400">
							<Activity class="w-3 h-3" />
							{runningServices}/{totalServices} services active
						</span>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>

<!-- Services Grid -->
<div class="mb-6">
	<div class="flex items-center justify-between mb-5">
		<h2 class="text-xl font-semibold text-white font-display flex items-center gap-2">
			<Server class="w-5 h-5 text-blue-400" />
			Active Services
		</h2>
		<div class="flex items-center gap-2 text-sm">
			<span class="flex items-center gap-1.5 text-emerald-400">
				<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
				{runningServices} Running
			</span>
			<span class="text-slate-600">|</span>
			<span class="text-slate-400">{totalServices} Total</span>
		</div>
	</div>

	<div class="grid gap-4 md:grid-cols-2">
		{#each services as service (service.id)}
			{@const config = getStatusConfig(service.status)}
			<div
				class="relative group cursor-pointer"
				on:click={() => selectedService = selectedService === service.id ? null : service.id}
				on:keydown={(e) => e.key === 'Enter' && (selectedService = selectedService === service.id ? null : service.id)}
				role="button"
				tabindex="0"
			>
				<!-- Glow effect -->
				{#if service.status === 'running'}
					<div class="absolute -inset-0.5 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 rounded-2xl blur opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
				{/if}
				
				<div class="relative p-5 rounded-2xl glass border {config.border} transition-all duration-300 hover:shadow-xl {
					selectedService === service.id ? 'ring-2 ring-blue-500/50 shadow-lg shadow-blue-500/10' : ''
				}">
					<!-- Status indicator line -->
					<div class="absolute top-0 left-6 right-6 h-px bg-gradient-to-r {config.bg} opacity-50"></div>
					
					<div class="flex items-start justify-between">
						<div class="flex items-center gap-4">
							<!-- Icon with status glow -->
							<div class="relative">
								{#if config.pulse}
									<div class="absolute inset-0 bg-{config.color}-500 rounded-xl blur-md opacity-30 animate-pulse"></div>
								{/if}
								<div class="relative w-14 h-14 rounded-xl bg-gradient-to-br {config.bg} border {config.border} flex items-center justify-center">
									<svelte:component this={config.icon} class="w-7 h-7 {config.text}" />
								</div>
							</div>
							<div>
								<h3 class="text-lg font-semibold text-white font-display">{service.name}</h3>
								<p class="text-xs text-slate-500 mt-0.5">{service.description || 'Service'}</p>
								<div class="flex items-center gap-2 mt-2">
									<Badge class="bg-gradient-to-r {config.bg} {config.border} {config.text} text-xs capitalize px-2 py-0.5">
										{#if config.pulse && service.status === 'running'}
											<span class="w-1.5 h-1.5 rounded-full bg-current mr-1.5 animate-pulse"></span>
										{/if}
										{service.status.replace('_', ' ')}
									</Badge>
									{#if service.version}
										<span class="text-xs text-slate-600">v{service.version}</span>
									{/if}
									{#if service.port}
										<span class="text-xs text-slate-600">:{service.port}</span>
									{/if}
								</div>
							</div>
						</div>

						<!-- Action Buttons -->
						<div class="flex gap-2">
							{#if service.status === 'running'}
								<button 
									on:click|stopPropagation={() => {}} 
									class="w-10 h-10 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-400 hover:bg-red-500/20 hover:scale-105 transition-all duration-300"
									title="Stop"
								>
									<Power class="h-4 h-4" />
								</button>
							{:else if service.status !== 'not_installed'}
								<button 
									on:click|stopPropagation={() => {}} 
									class="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 hover:bg-emerald-500/20 hover:scale-105 transition-all duration-300"
									title="Start"
								>
									<Play class="h-4 w-4" />
								</button>
							{/if}
							{#if service.status !== 'not_installed'}
								<button 
									on:click|stopPropagation={() => {}} 
									class="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-slate-400 hover:text-white hover:border-white/30 hover:scale-105 transition-all duration-300"
									title="Restart"
								>
									<RotateCcw class="h-4 w-4" />
								</button>
							{/if}
						</div>
					</div>

					<!-- Expanded Details -->
					{#if selectedService === service.id && service.status !== 'not_installed'}
						<div class="mt-5 pt-5 border-t border-white/10 space-y-4 animate-in slide-in-from-top-2 duration-300">
							<!-- Stats Grid -->
							<div class="grid grid-cols-3 gap-3">
								<div class="p-3 rounded-xl bg-black/20 border border-white/5">
									<p class="text-[10px] text-slate-500 uppercase tracking-wide mb-1">Uptime</p>
									<p class="text-sm font-bold text-blue-400 font-display">
										{service.status === 'running' ? formatUptime(service.uptime) : '—'}
									</p>
								</div>
								<div class="p-3 rounded-xl bg-black/20 border border-white/5">
									<p class="text-[10px] text-slate-500 uppercase tracking-wide mb-1">Memory</p>
									<p class="text-sm font-bold text-purple-400 font-display">{formatBytes(service.memory)}</p>
								</div>
								<div class="p-3 rounded-xl bg-black/20 border border-white/5">
									<p class="text-[10px] text-slate-500 uppercase tracking-wide mb-1">CPU</p>
									<p class="text-sm font-bold text-cyan-400 font-display">{service.cpu.toFixed(1)}%</p>
								</div>
							</div>

							<!-- Resource Bars -->
							<div class="space-y-3">
								<div>
									<div class="flex justify-between text-xs mb-1">
										<span class="text-slate-500">Memory Usage</span>
										<span class="text-purple-400">{formatBytes(service.memory)}</span>
									</div>
									<div class="h-1.5 bg-black/30 rounded-full overflow-hidden">
										<div 
											class="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500"
											style="width: {Math.min((service.memory / (512 * 1024 * 1024)) * 100, 100)}%"
										></div>
									</div>
								</div>
								<div>
									<div class="flex justify-between text-xs mb-1">
										<span class="text-slate-500">CPU Usage</span>
										<span class="text-cyan-400">{service.cpu.toFixed(1)}%</span>
									</div>
									<div class="h-1.5 bg-black/30 rounded-full overflow-hidden">
										<div 
											class="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-500"
											style="width: {service.cpu}%"
										></div>
									</div>
								</div>
							</div>

							<!-- Quick Actions -->
							<div class="flex gap-2 pt-2">
								<Button 
									on:click={(e) => e.stopPropagation()} 
									variant="outline" 
									size="sm"
									class="flex-1 border-white/10 text-slate-400 hover:text-white hover:border-cyan-500/50 hover:bg-cyan-500/10 rounded-xl"
								>
									<Eye class="w-4 h-4 mr-2" />
									View Logs
								</Button>
								<Button 
									on:click={(e) => e.stopPropagation()} 
									variant="outline" 
									size="sm"
									class="flex-1 border-white/10 text-slate-400 hover:text-white hover:border-violet-500/50 hover:bg-violet-500/10 rounded-xl"
								>
									<Settings class="w-4 h-4 mr-2" />
									Configure
								</Button>
							</div>
						</div>
					{/if}
				</div>
			</div>
		{/each}
	</div>
</div>

<!-- System Health -->
<div class="p-6 rounded-2xl glass border border-white/10 relative overflow-hidden">
	<div class="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl"></div>
	
	<div class="relative">
		<div class="flex items-center justify-between mb-6">
			<div class="flex items-center gap-3">
				<div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/30">
					<Activity class="w-6 h-6 text-white" />
				</div>
				<div>
					<h3 class="text-lg font-semibold text-white font-display">System Health</h3>
					<p class="text-xs text-slate-500">Real-time diagnostics</p>
				</div>
			</div>
			<Badge class="bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 gap-1.5">
				<Sparkles class="w-3 h-3" />
				All Systems Operational
			</Badge>
		</div>

		<div class="grid md:grid-cols-2 lg:grid-cols-4 gap-3">
			{#each [
				{ name: 'API Server', status: $coreConnected ? 'operational' : 'offline', icon: Globe },
				{ name: 'WebSocket', status: 'connected', icon: Radio },
				{ name: 'LLM Engine', status: 'ready', icon: Sparkles },
				{ name: 'Audio Pipeline', status: 'active', icon: Activity }
			] as check}
				<div class="p-4 rounded-xl bg-black/20 border border-white/5 flex items-center gap-3 hover:border-emerald-500/30 transition-all duration-300 group">
					<div class="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center group-hover:bg-emerald-500/20 transition-colors">
						<svelte:component this={check.icon} class="w-5 h-5 text-emerald-400" />
					</div>
					<div>
						<p class="text-sm font-medium text-white">{check.name}</p>
						<p class="text-xs text-emerald-400 capitalize">{check.status}</p>
					</div>
				</div>
			{/each}
		</div>
	</div>
</div>
