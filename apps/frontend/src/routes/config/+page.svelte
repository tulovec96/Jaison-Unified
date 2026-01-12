<script lang="ts">
	import { onMount } from 'svelte';
	import { 
		Copy, Edit2, Save, X, Settings, FileCode, Book, Key, 
		CheckCircle, Plus, Trash2, RefreshCw, User, MessageSquare,
		Film, AlertCircle, FolderOpen, File, ChevronRight, Sparkles
	} from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import { Input } from '$lib/components/ui/input';
	import * as Tabs from '$lib/components/ui/tabs';
	import { ScrollArea } from '$lib/components/ui/scroll-area/index.js';
	import { API_BASE, coreConnected } from '../socketio';

	// State
	let activeTab = 'prompts';
	let loading = false;
	let error = '';
	let success = '';

	// Prompts state
	interface Prompt {
		name: string;
		filename: string;
	}
	let prompts: { characters: Prompt[]; instructions: Prompt[]; scenes: Prompt[] } = {
		characters: [],
		instructions: [],
		scenes: []
	};
	let selectedPromptCategory: 'characters' | 'instructions' | 'scenes' = 'characters';
	let selectedPrompt: string | null = null;
	let promptContent = '';
	let promptEditMode = false;
	let newPromptName = '';
	let showNewPromptInput = false;

	// Config state
	interface ConfigFile {
		name: string;
		filename: string;
		main?: boolean;
	}
	let configs: ConfigFile[] = [];
	let selectedConfig: string | null = null;
	let configContent = '';
	let configEditMode = false;

	// Env state
	let envContent = '';
	let envEditMode = false;
	let envLoaded = false;

	// Helper functions
	function showError(msg: string) {
		error = msg;
		setTimeout(() => error = '', 5000);
	}

	function showSuccess(msg: string) {
		success = msg;
		setTimeout(() => success = '', 3000);
	}

	// Prompts API
	async function loadPrompts() {
		try {
			loading = true;
			const res = await fetch(`${API_BASE}/api/prompts`);
			const data = await res.json();
			if (data.status === 200) {
				prompts = data.response;
			} else {
				showError(data.message);
			}
		} catch (e) {
			showError('Failed to load prompts. Is core server running?');
		} finally {
			loading = false;
		}
	}

	async function loadPromptContent(category: string, name: string) {
		try {
			loading = true;
			const res = await fetch(`${API_BASE}/api/prompts/${category}/${name}`);
			const data = await res.json();
			if (data.status === 200) {
				promptContent = data.response.content;
				selectedPrompt = name;
				promptEditMode = false;
			} else {
				showError(data.message);
			}
		} catch (e) {
			showError('Failed to load prompt');
		} finally {
			loading = false;
		}
	}

	async function savePrompt() {
		if (!selectedPrompt) return;
		try {
			loading = true;
			const res = await fetch(`${API_BASE}/api/prompts/${selectedPromptCategory}/${selectedPrompt}`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ content: promptContent })
			});
			const data = await res.json();
			if (data.status === 200) {
				showSuccess('Prompt saved successfully');
				promptEditMode = false;
			} else {
				showError(data.message);
			}
		} catch (e) {
			showError('Failed to save prompt');
		} finally {
			loading = false;
		}
	}

	async function createPrompt() {
		if (!newPromptName.trim()) return;
		try {
			loading = true;
			const res = await fetch(`${API_BASE}/api/prompts/${selectedPromptCategory}/${newPromptName}`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ content: `# ${newPromptName}\n\nWrite your prompt here...` })
			});
			const data = await res.json();
			if (data.status === 200) {
				showSuccess('Prompt created');
				newPromptName = '';
				showNewPromptInput = false;
				await loadPrompts();
				loadPromptContent(selectedPromptCategory, data.response.name);
			} else {
				showError(data.message);
			}
		} catch (e) {
			showError('Failed to create prompt');
		} finally {
			loading = false;
		}
	}

	async function deletePrompt(name: string) {
		if (!confirm(`Delete "${name}"?`)) return;
		try {
			loading = true;
			const res = await fetch(`${API_BASE}/api/prompts/${selectedPromptCategory}/${name}`, {
				method: 'DELETE'
			});
			const data = await res.json();
			if (data.status === 200) {
				showSuccess('Prompt deleted');
				if (selectedPrompt === name) {
					selectedPrompt = null;
					promptContent = '';
				}
				await loadPrompts();
			} else {
				showError(data.message);
			}
		} catch (e) {
			showError('Failed to delete prompt');
		} finally {
			loading = false;
		}
	}

	// Configs API
	async function loadConfigs() {
		try {
			loading = true;
			const res = await fetch(`${API_BASE}/api/configs`);
			const data = await res.json();
			if (data.status === 200) {
				configs = data.response;
			} else {
				showError(data.message);
			}
		} catch (e) {
			showError('Failed to load configs');
		} finally {
			loading = false;
		}
	}

	async function loadConfigContent(name: string) {
		try {
			loading = true;
			const res = await fetch(`${API_BASE}/api/configs/${name}`);
			const data = await res.json();
			if (data.status === 200) {
				configContent = data.response.content;
				selectedConfig = name;
				configEditMode = false;
			} else {
				showError(data.message);
			}
		} catch (e) {
			showError('Failed to load config');
		} finally {
			loading = false;
		}
	}

	async function saveConfig() {
		if (!selectedConfig) return;
		try {
			loading = true;
			const res = await fetch(`${API_BASE}/api/configs/${selectedConfig}`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ content: configContent })
			});
			const data = await res.json();
			if (data.status === 200) {
				showSuccess('Config saved successfully');
				configEditMode = false;
			} else {
				showError(data.message);
			}
		} catch (e) {
			showError('Failed to save config');
		} finally {
			loading = false;
		}
	}

	// Env API
	async function loadEnv() {
		try {
			loading = true;
			const res = await fetch(`${API_BASE}/api/env`);
			const data = await res.json();
			if (data.status === 200) {
				envContent = data.response.content;
				envLoaded = true;
				envEditMode = false;
			} else {
				showError(data.message);
			}
		} catch (e) {
			showError('Failed to load .env file');
		} finally {
			loading = false;
		}
	}

	async function saveEnv() {
		try {
			loading = true;
			const res = await fetch(`${API_BASE}/api/env`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ content: envContent })
			});
			const data = await res.json();
			if (data.status === 200) {
				showSuccess('.env saved. Restart core to apply changes.');
				envEditMode = false;
			} else {
				showError(data.message);
			}
		} catch (e) {
			showError('Failed to save .env file');
		} finally {
			loading = false;
		}
	}

	function getCategoryIcon(category: string) {
		switch (category) {
			case 'characters': return User;
			case 'instructions': return MessageSquare;
			case 'scenes': return Film;
			default: return File;
		}
	}

	onMount(() => {
		loadPrompts();
		loadConfigs();
	});
</script>

<!-- Header -->
<div class="mb-8 relative group">
	<div class="absolute -inset-4 bg-gradient-to-r from-violet-500/10 via-purple-500/5 to-pink-500/10 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-all duration-700"></div>
	<div class="relative flex items-center justify-between">
		<div class="flex items-center gap-4">
			<div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg shadow-violet-500/30 hover-scale">
				<Settings class="w-7 h-7 text-white" />
			</div>
			<div>
				<h1 class="text-4xl font-bold gradient-text font-display">Configuration</h1>
				<p class="text-slate-400 mt-1 flex items-center gap-2">
					<span class="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse"></span>
					Manage prompts, configs, and environment
				</p>
			</div>
		</div>
		<div class="flex items-center gap-3">
			{#if !$coreConnected}
				<Badge class="bg-red-500/20 border border-red-500/30 text-red-400 gap-1.5">
					<AlertCircle class="w-3 h-3" />
					Core Offline
				</Badge>
			{/if}
		</div>
	</div>
</div>

<!-- Alerts -->
{#if error}
	<div class="mb-4 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 flex items-center gap-3">
		<AlertCircle class="w-5 h-5 flex-shrink-0" />
		{error}
	</div>
{/if}
{#if success}
	<div class="mb-4 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center gap-3">
		<CheckCircle class="w-5 h-5 flex-shrink-0" />
		{success}
	</div>
{/if}

<!-- Main Tabs -->
<Tabs.Root bind:value={activeTab}>
	<Tabs.List class="mb-6 glass border border-white/10 p-1.5 rounded-2xl">
		<Tabs.Trigger value="prompts" class="rounded-xl data-[state=active]:bg-gradient-to-r data-[state=active]:from-pink-500/30 data-[state=active]:to-rose-500/30 transition-all duration-300">
			<Sparkles class="w-4 h-4 mr-2" />
			Prompts
		</Tabs.Trigger>
		<Tabs.Trigger value="configs" class="rounded-xl data-[state=active]:bg-gradient-to-r data-[state=active]:from-violet-500/30 data-[state=active]:to-purple-500/30 transition-all duration-300">
			<FileCode class="w-4 h-4 mr-2" />
			Configs
		</Tabs.Trigger>
		<Tabs.Trigger value="env" class="rounded-xl data-[state=active]:bg-gradient-to-r data-[state=active]:from-amber-500/30 data-[state=active]:to-orange-500/30 transition-all duration-300">
			<Key class="w-4 h-4 mr-2" />
			Environment
		</Tabs.Trigger>
	</Tabs.List>

	<!-- Prompts Tab -->
	<Tabs.Content value="prompts">
		<div class="grid lg:grid-cols-3 gap-6">
			<!-- Sidebar: Category & Files -->
			<div class="space-y-4">
				<!-- Category Selector -->
				<div class="p-4 rounded-2xl glass border border-white/10">
					<h3 class="text-sm font-semibold text-white mb-3">Category</h3>
					<div class="space-y-2">
						{#each ['characters', 'instructions', 'scenes'] as cat}
							<button
								on:click={() => { selectedPromptCategory = cat; selectedPrompt = null; promptContent = ''; }}
								class="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 {
									selectedPromptCategory === cat 
										? 'bg-gradient-to-r from-pink-500/20 to-rose-500/20 border border-pink-500/30 text-pink-400' 
										: 'bg-white/5 border border-white/5 text-slate-400 hover:bg-white/10 hover:text-white'
								}"
							>
								<svelte:component this={getCategoryIcon(cat)} class="w-5 h-5" />
								<span class="capitalize font-medium">{cat}</span>
								<Badge class="ml-auto bg-white/10 text-slate-400">{prompts[cat]?.length || 0}</Badge>
							</button>
						{/each}
					</div>
				</div>

				<!-- File List -->
				<div class="p-4 rounded-2xl glass border border-white/10">
					<div class="flex items-center justify-between mb-3">
						<h3 class="text-sm font-semibold text-white capitalize">{selectedPromptCategory}</h3>
						<button
							on:click={() => showNewPromptInput = !showNewPromptInput}
							class="p-2 rounded-lg bg-pink-500/20 text-pink-400 hover:bg-pink-500/30 transition-all"
						>
							<Plus class="w-4 h-4" />
						</button>
					</div>

					{#if showNewPromptInput}
						<div class="flex gap-2 mb-3">
							<Input 
								bind:value={newPromptName} 
								placeholder="New prompt name..." 
								class="flex-1 bg-white/5 border-white/10 text-slate-300 rounded-lg text-sm"
							/>
							<Button on:click={createPrompt} size="sm" class="bg-pink-500/20 border border-pink-500/30 text-pink-400 hover:bg-pink-500/30 rounded-lg">
								Create
							</Button>
						</div>
					{/if}

					<ScrollArea class="h-[300px]">
						<div class="space-y-1 pr-2">
							{#each prompts[selectedPromptCategory] || [] as prompt}
								<div class="group flex items-center">
									<button
										on:click={() => loadPromptContent(selectedPromptCategory, prompt.name)}
										class="flex-1 flex items-center gap-2 px-3 py-2.5 rounded-lg transition-all text-left {
											selectedPrompt === prompt.name 
												? 'bg-pink-500/20 text-pink-400' 
												: 'text-slate-400 hover:bg-white/5 hover:text-white'
										}"
									>
										<File class="w-4 h-4 flex-shrink-0" />
										<span class="truncate text-sm">{prompt.name}</span>
									</button>
									<button
										on:click={() => deletePrompt(prompt.name)}
										class="p-1.5 rounded-lg text-slate-600 hover:text-red-400 hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition-all"
									>
										<Trash2 class="w-3.5 h-3.5" />
									</button>
								</div>
							{:else}
								<p class="text-sm text-slate-500 text-center py-4">No prompts yet</p>
							{/each}
						</div>
					</ScrollArea>
				</div>
			</div>

			<!-- Editor -->
			<div class="lg:col-span-2">
				<div class="p-6 rounded-2xl glass border border-white/10 h-full">
					{#if selectedPrompt}
						<div class="flex items-center justify-between mb-4">
							<div class="flex items-center gap-3">
								<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center">
									<svelte:component this={getCategoryIcon(selectedPromptCategory)} class="w-5 h-5 text-white" />
								</div>
								<div>
									<h3 class="font-semibold text-white">{selectedPrompt}</h3>
									<p class="text-xs text-slate-500 capitalize">{selectedPromptCategory}</p>
								</div>
							</div>
							<div class="flex gap-2">
								{#if promptEditMode}
									<Button on:click={savePrompt} size="sm" class="bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/30 rounded-xl">
										<Save class="w-4 h-4 mr-2" />
										Save
									</Button>
									<Button on:click={() => { promptEditMode = false; loadPromptContent(selectedPromptCategory, selectedPrompt); }} size="sm" variant="outline" class="border-white/10 text-slate-400 rounded-xl">
										<X class="w-4 h-4 mr-2" />
										Cancel
									</Button>
								{:else}
									<Button on:click={() => promptEditMode = true} size="sm" class="bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/30 rounded-xl">
										<Edit2 class="w-4 h-4 mr-2" />
										Edit
									</Button>
								{/if}
							</div>
						</div>
						<textarea
							bind:value={promptContent}
							disabled={!promptEditMode}
							class="w-full h-[500px] p-4 rounded-xl bg-black/30 border {promptEditMode ? 'border-pink-500/30' : 'border-white/10'} text-slate-300 font-mono text-sm resize-none focus:outline-none focus:border-pink-500/50 transition-all disabled:opacity-70"
							placeholder="Prompt content..."
						></textarea>
					{:else}
						<div class="h-full flex flex-col items-center justify-center text-slate-500">
							<FolderOpen class="w-16 h-16 mb-4 opacity-30" />
							<p>Select a prompt to view or edit</p>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</Tabs.Content>

	<!-- Configs Tab -->
	<Tabs.Content value="configs">
		<div class="grid lg:grid-cols-3 gap-6">
			<!-- Config List -->
			<div class="p-4 rounded-2xl glass border border-white/10">
				<div class="flex items-center justify-between mb-4">
					<h3 class="text-sm font-semibold text-white">Config Files</h3>
					<button on:click={loadConfigs} class="p-2 rounded-lg bg-white/5 text-slate-400 hover:bg-white/10 hover:text-white transition-all">
						<RefreshCw class="w-4 h-4" />
					</button>
				</div>
				<ScrollArea class="h-[400px]">
					<div class="space-y-1 pr-2">
						{#each configs as config}
							<button
								on:click={() => loadConfigContent(config.name)}
								class="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-left {
									selectedConfig === config.name 
										? 'bg-violet-500/20 border border-violet-500/30 text-violet-400' 
										: 'bg-white/5 border border-white/5 text-slate-400 hover:bg-white/10 hover:text-white'
								}"
							>
								<FileCode class="w-5 h-5 flex-shrink-0" />
								<div class="flex-1 min-w-0">
									<p class="truncate font-medium">{config.filename}</p>
									{#if config.main}
										<p class="text-xs text-violet-400/60">Main configuration</p>
									{/if}
								</div>
								<ChevronRight class="w-4 h-4 opacity-50" />
							</button>
						{:else}
							<p class="text-sm text-slate-500 text-center py-4">No configs found</p>
						{/each}
					</div>
				</ScrollArea>
			</div>

			<!-- Config Editor -->
			<div class="lg:col-span-2">
				<div class="p-6 rounded-2xl glass border border-white/10 h-full">
					{#if selectedConfig}
						<div class="flex items-center justify-between mb-4">
							<div class="flex items-center gap-3">
								<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
									<FileCode class="w-5 h-5 text-white" />
								</div>
								<div>
									<h3 class="font-semibold text-white">{selectedConfig}.yaml</h3>
									<p class="text-xs text-slate-500">YAML Configuration</p>
								</div>
							</div>
							<div class="flex gap-2">
								{#if configEditMode}
									<Button on:click={saveConfig} size="sm" class="bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/30 rounded-xl">
										<Save class="w-4 h-4 mr-2" />
										Save
									</Button>
									<Button on:click={() => { configEditMode = false; loadConfigContent(selectedConfig); }} size="sm" variant="outline" class="border-white/10 text-slate-400 rounded-xl">
										<X class="w-4 h-4 mr-2" />
										Cancel
									</Button>
								{:else}
									<Button on:click={() => configEditMode = true} size="sm" class="bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/30 rounded-xl">
										<Edit2 class="w-4 h-4 mr-2" />
										Edit
									</Button>
								{/if}
							</div>
						</div>
						<textarea
							bind:value={configContent}
							disabled={!configEditMode}
							class="w-full h-[500px] p-4 rounded-xl bg-black/30 border {configEditMode ? 'border-violet-500/30' : 'border-white/10'} text-slate-300 font-mono text-sm resize-none focus:outline-none focus:border-violet-500/50 transition-all disabled:opacity-70"
							placeholder="Config content..."
						></textarea>
					{:else}
						<div class="h-full flex flex-col items-center justify-center text-slate-500">
							<FileCode class="w-16 h-16 mb-4 opacity-30" />
							<p>Select a config file to view or edit</p>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</Tabs.Content>

	<!-- Environment Tab -->
	<Tabs.Content value="env">
		<div class="p-6 rounded-2xl glass border border-white/10">
			<div class="flex items-center justify-between mb-6">
				<div class="flex items-center gap-3">
					<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-amber-500/30">
						<Key class="w-5 h-5 text-white" />
					</div>
					<div>
						<h3 class="font-semibold text-white">Environment Variables</h3>
						<p class="text-xs text-slate-500">.env file - API keys and secrets</p>
					</div>
				</div>
				<div class="flex gap-2">
					{#if !envLoaded}
						<Button on:click={loadEnv} size="sm" class="bg-amber-500/20 border border-amber-500/30 text-amber-400 hover:bg-amber-500/30 rounded-xl">
							<FolderOpen class="w-4 h-4 mr-2" />
							Load .env
						</Button>
					{:else if envEditMode}
						<Button on:click={saveEnv} size="sm" class="bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/30 rounded-xl">
							<Save class="w-4 h-4 mr-2" />
							Save
						</Button>
						<Button on:click={() => { envEditMode = false; loadEnv(); }} size="sm" variant="outline" class="border-white/10 text-slate-400 rounded-xl">
							<X class="w-4 h-4 mr-2" />
							Cancel
						</Button>
					{:else}
						<Button on:click={() => envEditMode = true} size="sm" class="bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/30 rounded-xl">
							<Edit2 class="w-4 h-4 mr-2" />
							Edit
						</Button>
						<Button on:click={loadEnv} size="sm" variant="outline" class="border-white/10 text-slate-400 rounded-xl">
							<RefreshCw class="w-4 h-4" />
						</Button>
					{/if}
				</div>
			</div>

			{#if envLoaded}
				<div class="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 text-sm mb-4 flex items-center gap-2">
					<AlertCircle class="w-4 h-4 flex-shrink-0" />
					<span>⚠️ Be careful! This file contains sensitive API keys. Changes require a core restart.</span>
				</div>
				<textarea
					bind:value={envContent}
					disabled={!envEditMode}
					class="w-full h-[400px] p-4 rounded-xl bg-black/30 border {envEditMode ? 'border-amber-500/30' : 'border-white/10'} text-slate-300 font-mono text-sm resize-none focus:outline-none focus:border-amber-500/50 transition-all disabled:opacity-70"
					placeholder="Environment variables..."
				></textarea>
			{:else}
				<div class="h-[300px] flex flex-col items-center justify-center text-slate-500 border border-dashed border-white/10 rounded-xl">
					<Key class="w-16 h-16 mb-4 opacity-30" />
					<p class="mb-4">Click "Load .env" to view environment variables</p>
					<p class="text-xs text-slate-600">⚠️ Contains sensitive data</p>
				</div>
			{/if}
		</div>
	</Tabs.Content>
</Tabs.Root>
