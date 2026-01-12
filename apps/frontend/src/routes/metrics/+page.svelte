<script lang="ts">
  import { Activity, Cpu, HardDrive, Zap, BarChart3, TrendingUp } from 'lucide-svelte';
  import { onMount } from 'svelte';

  let metrics = {
    cpu: 15,
    memory: 45,
    latency: 125,
    requestsPerSecond: 42,
    errors: 0,
    cpuHistory: [15, 18, 16, 20, 19, 22, 21] as number[],
    memoryHistory: [45, 46, 48, 47, 49, 50, 45] as number[]
  };

  onMount(() => {
    const interval = setInterval(() => {
      const newCpu = Math.max(5, Math.min(95, metrics.cpu + (Math.random() - 0.5) * 10));
      const newMemory = Math.max(20, Math.min(90, metrics.memory + (Math.random() - 0.5) * 5));
      
      metrics = {
        ...metrics,
        cpu: newCpu,
        memory: newMemory,
        latency: Math.max(50, Math.min(500, metrics.latency + (Math.random() - 0.5) * 20)),
        requestsPerSecond: Math.max(0, Math.min(100, metrics.requestsPerSecond + (Math.random() - 0.5) * 5)),
        cpuHistory: [...metrics.cpuHistory.slice(1), newCpu],
        memoryHistory: [...metrics.memoryHistory.slice(1), newMemory]
      };
    }, 2000);

    return () => clearInterval(interval);
  });

  function getColor(value: number, high: number = 80): string {
    if (value < high * 0.5) return 'text-emerald-400';
    if (value < high * 0.8) return 'text-amber-400';
    return 'text-red-400';
  }

  function getGradient(value: number, high: number = 80): string {
    if (value < high * 0.5) return 'from-emerald-500 to-teal-500';
    if (value < high * 0.8) return 'from-amber-500 to-orange-500';
    return 'from-red-500 to-pink-500';
  }
</script>

<!-- Header -->
<div class="mb-8 relative group">
  <div class="absolute -inset-4 bg-gradient-to-r from-pink-500/10 via-rose-500/5 to-purple-500/10 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-all duration-700"></div>
  <div class="relative flex items-center gap-4">
    <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center shadow-lg shadow-pink-500/30 hover-scale">
      <BarChart3 class="w-7 h-7 text-white" />
    </div>
    <div>
      <h1 class="text-4xl font-bold gradient-text font-display">
        Performance Metrics
      </h1>
      <p class="text-slate-400 mt-1 flex items-center gap-2">
        <span class="w-1.5 h-1.5 rounded-full bg-pink-400 animate-pulse"></span>
        Real-time system performance monitoring
      </p>
    </div>
  </div>
</div>

<!-- Main Metrics -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
  <div class="glass p-6 rounded-2xl hover-glow-cyan group transition-all duration-300">
    <div class="flex items-center justify-between mb-4">
      <span class="text-sm text-slate-400 font-medium">CPU Usage</span>
      <div class="w-10 h-10 rounded-xl bg-cyan-500/20 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
        <Cpu class="w-5 h-5 text-cyan-400" />
      </div>
    </div>
    <div class={`text-3xl font-bold font-display ${getColor(metrics.cpu)}`}>{metrics.cpu.toFixed(1)}%</div>
    <div class="w-full bg-white/10 rounded-full h-2.5 mt-4 overflow-hidden">
      <div class={`bg-gradient-to-r ${getGradient(metrics.cpu)} h-2.5 rounded-full transition-all duration-500`} style="width: {metrics.cpu}%" />
    </div>
    <div class="flex items-center gap-1 mt-3">
      <TrendingUp class="w-3 h-3 text-emerald-400" />
      <span class="text-xs text-slate-500">Last 14s</span>
    </div>
  </div>

  <div class="glass p-6 rounded-2xl hover-glow-purple group transition-all duration-300">
    <div class="flex items-center justify-between mb-4">
      <span class="text-sm text-slate-400 font-medium">Memory Usage</span>
      <div class="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
        <HardDrive class="w-5 h-5 text-purple-400" />
      </div>
    </div>
    <div class={`text-3xl font-bold font-display ${getColor(metrics.memory)}`}>{metrics.memory.toFixed(1)}%</div>
    <div class="w-full bg-white/10 rounded-full h-2.5 mt-4 overflow-hidden">
      <div class={`bg-gradient-to-r ${getGradient(metrics.memory)} h-2.5 rounded-full transition-all duration-500`} style="width: {metrics.memory}%" />
    </div>
    <div class="flex items-center gap-1 mt-3">
      <TrendingUp class="w-3 h-3 text-emerald-400" />
      <span class="text-xs text-slate-500">Last 14s</span>
    </div>
  </div>

  <div class="glass p-6 rounded-2xl hover-glow-amber group transition-all duration-300">
    <div class="flex items-center justify-between mb-4">
      <span class="text-sm text-slate-400 font-medium">API Latency</span>
      <div class="w-10 h-10 rounded-xl bg-amber-500/20 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
        <Zap class="w-5 h-5 text-amber-400" />
      </div>
    </div>
    <div class={`text-3xl font-bold font-display ${getColor(metrics.latency, 300)}`}>{metrics.latency.toFixed(0)}ms</div>
    <p class="text-xs text-slate-500 mt-4">95th percentile</p>
  </div>

  <div class="glass p-6 rounded-2xl hover-glow-green group transition-all duration-300">
    <div class="flex items-center justify-between mb-4">
      <span class="text-sm text-slate-400 font-medium">Requests/sec</span>
      <div class="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
        <Activity class="w-5 h-5 text-emerald-400" />
      </div>
    </div>
    <div class="text-3xl font-bold font-display text-emerald-400">{metrics.requestsPerSecond.toFixed(1)}</div>
    <div class="flex items-center gap-2 mt-4">
      <span class={`px-2.5 py-1 rounded-lg text-xs font-semibold ${metrics.errors === 0 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
        {metrics.errors} errors
      </span>
    </div>
  </div>
</div>

<!-- Detailed Charts -->
<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
  <div class="glass p-6 rounded-2xl hover-glow-cyan">
    <div class="flex items-center gap-3 mb-6">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
        <Cpu class="w-5 h-5 text-white" />
      </div>
      <div>
        <h3 class="font-semibold text-white font-display">CPU Usage</h3>
        <p class="text-xs text-slate-500">Last 14 seconds</p>
      </div>
    </div>
    <div class="h-32 flex items-end gap-2">
      {#each metrics.cpuHistory as value, i}
        <div 
          class="flex-1 bg-gradient-to-t from-cyan-600 to-cyan-400 rounded-t-lg hover:from-cyan-500 hover:to-cyan-300 transition-all duration-300 cursor-pointer relative group shadow-lg shadow-cyan-500/20" 
          style="height: {Math.max(5, (value / 100) * 100)}%"
        >
          <div class="absolute -top-8 left-1/2 -translate-x-1/2 px-2 py-1 rounded-lg bg-black/80 border border-cyan-500/30 text-xs text-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
            {value.toFixed(1)}%
          </div>
        </div>
      {/each}
    </div>
    <div class="flex justify-between text-xs text-slate-600 mt-3 border-t border-white/10 pt-3">
      <span>0%</span>
      <span>50%</span>
      <span>100%</span>
    </div>
  </div>

  <div class="glass p-6 rounded-2xl hover-glow-purple">
    <div class="flex items-center gap-3 mb-6">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-lg shadow-purple-500/30">
        <HardDrive class="w-5 h-5 text-white" />
      </div>
      <div>
        <h3 class="font-semibold text-white font-display">Memory Usage</h3>
        <p class="text-xs text-slate-500">Last 14 seconds</p>
      </div>
    </div>
    <div class="h-32 flex items-end gap-2">
      {#each metrics.memoryHistory as value, i}
        <div 
          class="flex-1 bg-gradient-to-t from-purple-600 to-purple-400 rounded-t-lg hover:from-purple-500 hover:to-purple-300 transition-all duration-300 cursor-pointer relative group shadow-lg shadow-purple-500/20" 
          style="height: {Math.max(5, (value / 100) * 100)}%"
        >
          <div class="absolute -top-8 left-1/2 -translate-x-1/2 px-2 py-1 rounded-lg bg-black/80 border border-purple-500/30 text-xs text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
            {value.toFixed(1)}%
          </div>
        </div>
      {/each}
    </div>
    <div class="flex justify-between text-xs text-slate-600 mt-3 border-t border-white/10 pt-3">
      <span>0%</span>
      <span>50%</span>
      <span>100%</span>
    </div>
  </div>
</div>

<!-- System Status -->
<div class="mt-6 p-5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-between backdrop-blur-sm shadow-lg shadow-emerald-500/10">
  <div class="flex items-center gap-3">
    <div class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse shadow-lg shadow-emerald-500/50"></div>
    <span class="text-sm text-emerald-400 font-medium">All systems operational</span>
  </div>
  <span class="text-xs text-slate-500 bg-black/30 px-3 py-1.5 rounded-lg">Auto-refresh: 2s</span>
</div>
