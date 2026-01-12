import { writable, get } from 'svelte/store';
import {io} from "socket.io-client";
import {toast} from "svelte-sonner";

// API base URL for REST calls
export const API_BASE = "http://localhost:7272";

//Connect to the backend and handle storing received data.
export const socket = io("localhost:8080");

// Core server connection status
export const coreConnected = writable(false);
export const coreStatus = writable<{
	status: string;
	version: string;
	uptime: number;
}>({ status: 'unknown', version: '', uptime: 0 });

// Check core health periodically
async function checkCoreHealth() {
	try {
		const response = await fetch(`${API_BASE}/api/health`);
		if (response.ok) {
			const data = await response.json();
			coreConnected.set(true);
			coreStatus.set(data.response || { status: 'healthy', version: '2.0.0', uptime: 0 });
		} else {
			coreConnected.set(false);
			coreStatus.set({ status: 'error', version: '', uptime: 0 });
		}
	} catch (e) {
		coreConnected.set(false);
		coreStatus.set({ status: 'disconnected', version: '', uptime: 0 });
	}
}

// Check health on load and every 5 seconds
if (typeof window !== 'undefined') {
	checkCoreHealth();
	setInterval(checkCoreHealth, 5000);
}

socket.on("error", (data) => {
	toast.error(data);
});

////// MAIN PAGE

//Current Message Section
export let currentMessage = writable("");
socket.on("current_message", (message: string) => {
	currentMessage.set(message);
});

//Next Message Section
export let nextMessage = writable("");
socket.on("reset_next_message", () => {
	nextMessage.set("");
});
socket.on("next_chunk", (message: string) => {
	nextMessage.update(n => n + message);
});

//Signals Section
export let AI_thinking = writable(false);
socket.on("AI_thinking", (message: boolean) => {
	AI_thinking.set(message);
});
export let AI_speaking = writable(false);
socket.on("AI_speaking", (message: boolean) => {
	AI_speaking.set(message);
});
export let human_speaking = writable(false);
socket.on("human_speaking", (message: boolean) => {
	human_speaking.set(message);
});
export let patiencePercent = writable(0);
export let total_time = writable(0);
socket.on("patience_update", (message) => {
	patiencePercent.set((message.crr_time / message.total_time) * 100);
	total_time.set(message.total_time);
});

//Twitch Chat Section
export let twitchChat = writable("");
export let twitchChatEnabled = writable(true);
socket.on("recent_twitch_messages", (message) => {
	twitchChat.set(message.join("\n"));
});
socket.on("twitch_status", (message: boolean) => {
	twitchChatEnabled.set(message);
});

//Controls Section
export let LLMEnabled = writable(true);
export let TTSEnabled = writable(true);
export let STTEnabled = writable(true);
export let movementEnabled = writable(true);
export let multimodalEnabled = writable(true);
socket.on("LLM_status", (message: boolean) => {
	LLMEnabled.set(message);
});
socket.on("TTS_status", (message: boolean) => {
	TTSEnabled.set(message);
});
socket.on("STT_status", (message: boolean) => {
	STTEnabled.set(message);
});
socket.on("movement_status", (message: boolean) => {
	movementEnabled.set(message);
});
socket.on("multimodal_status", (message: boolean) => {
	multimodalEnabled.set(message);
});

//Sing Section
export let selectedAudio = writable<any>(null);
export let songs = writable([
	{ value: "", label: "Loading..." }
]);
socket.on("audio_list", (message) => {
	let songList: any[] = [];
	message.forEach((song : any) => {
		songList.push({ value: song, label: song });
	});
	songs.set(songList);
});

////// LOBOTOMY PAGE

//Lobotomy Section
export const lobotomy = writable("");
socket.on("full_prompt", (message: string) => {
	lobotomy.set(message);
});

//Custom Prompt Section
export const priority = writable(200);
export const customPrompt = writable("");
socket.on("get_custom_prompt", (message: any) => {
	customPrompt.set(message.prompt);
	priority.set(message.priority);
});

////// MEMORY PAGE

export const memories = writable<any>([]);
export const searchQuery = writable("");
socket.on("get_memories", (data) => {
	memories.set(data);
});

////// MODERATION PAGE

export const blacklist = writable("");
socket.on("get_blacklist", (data) => {
	blacklist.set(data.join("\n"));
});

////// VTUBE PAGE

export const hotkeys = writable<any>([]);
socket.on("get_hotkeys", (data) => {
	hotkeys.set(data);
});

////// TWITCH PAGE - Live Stats

export interface TwitchStats {
	followers: number;
	subscribers: number;
	viewers: number;
	chatMessages: number;
	bitsReceived: number;
	raids: number;
	isLive: boolean;
	uptime: number;
	channelName: string;
}

export interface TwitchEvent {
	id: string;
	type: 'follow' | 'subscribe' | 'raid' | 'bits' | 'cheer' | 'gift' | 'hype_train';
	user: string;
	timestamp: string;
	details: string;
	value?: number;
}

export interface TwitchChatMessage {
	id: string;
	user: string;
	message: string;
	timestamp: string;
	badges: string[];
	color?: string;
}

export const twitchStats = writable<TwitchStats>({
	followers: 0,
	subscribers: 0,
	viewers: 0,
	chatMessages: 0,
	bitsReceived: 0,
	raids: 0,
	isLive: false,
	uptime: 0,
	channelName: ''
});

export const twitchEvents = writable<TwitchEvent[]>([]);
export const twitchChatHistory = writable<TwitchChatMessage[]>([]);
export const twitchViewerHistory = writable<number[]>([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]);
export const twitchChatRate = writable<number[]>([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]);
export const twitchConnected = writable(false);
export const twitchConfig = writable({
	channelName: '',
	chatMode: 'DISABLE',
	keywords: '',
	bitsThreshold: 100,
	summaryInterval: 10
});

socket.on("twitch_stats", (data: TwitchStats) => {
	twitchStats.set(data);
	// Update viewer history for chart
	twitchViewerHistory.update(history => {
		const newHistory = [...history.slice(1), data.viewers];
		return newHistory;
	});
});

socket.on("twitch_event", (event: TwitchEvent) => {
	twitchEvents.update(events => {
		const newEvents = [event, ...events].slice(0, 50);
		return newEvents;
	});
});

socket.on("twitch_chat_message", (message: TwitchChatMessage) => {
	twitchChatHistory.update(messages => {
		const newMessages = [message, ...messages].slice(0, 100);
		return newMessages;
	});
	twitchChatRate.update(rate => {
		const newRate = [...rate.slice(1), rate[rate.length - 1] + 1];
		return newRate;
	});
});

socket.on("twitch_connected", (status: boolean) => {
	twitchConnected.set(status);
});

socket.on("twitch_config", (config: any) => {
	twitchConfig.set(config);
});

////// DISCORD PAGE - Live Stats

export interface DiscordStats {
	servers: number;
	activeChannels: number;
	messagesProcessed: number;
	voiceSessions: number;
	avgResponseTime: number;
	currentVoiceChannel: string;
	isInVoice: boolean;
	usersInVoice: number;
}

export interface DiscordMessage {
	id: string;
	user: string;
	content: string;
	timestamp: string;
	channel: string;
	isBot: boolean;
}

export interface DiscordVoiceUser {
	id: string;
	username: string;
	isSpeaking: boolean;
	isMuted: boolean;
	isDeafened: boolean;
}

export const discordStats = writable<DiscordStats>({
	servers: 0,
	activeChannels: 0,
	messagesProcessed: 0,
	voiceSessions: 0,
	avgResponseTime: 0,
	currentVoiceChannel: '',
	isInVoice: false,
	usersInVoice: 0
});

export const discordConnected = writable(false);
export const discordMessages = writable<DiscordMessage[]>([]);
export const discordVoiceUsers = writable<DiscordVoiceUser[]>([]);
export const discordConfig = writable({
	prefix: '!',
	responseLatency: 2,
	idleInterval: 30,
	maxContextLength: 500,
	enableVoice: true,
	enableText: true
});

socket.on("discord_stats", (data: DiscordStats) => {
	discordStats.set(data);
});

socket.on("discord_connected", (status: boolean) => {
	discordConnected.set(status);
});

socket.on("discord_message", (message: DiscordMessage) => {
	discordMessages.update(messages => {
		return [message, ...messages].slice(0, 100);
	});
});

socket.on("discord_voice_users", (users: DiscordVoiceUser[]) => {
	discordVoiceUsers.set(users);
});

socket.on("discord_config", (config: any) => {
	discordConfig.set(config);
});

////// VTS PAGE - Live Stats

export interface VTSStatus {
	connected: boolean;
	modelLoaded: boolean;
	modelName: string;
	currentExpression: string;
	hotkeyQueueLength: number;
	lastHotkey: string;
	pluginName: string;
}

export interface VTSHotkeyExecution {
	hotkeyName: string;
	timestamp: string;
	success: boolean;
}

export const vtsStatus = writable<VTSStatus>({
	connected: false,
	modelLoaded: false,
	modelName: '',
	currentExpression: 'neutral',
	hotkeyQueueLength: 0,
	lastHotkey: '',
	pluginName: ''
});

export const vtsExpressionHistory = writable<string[]>([]);
export const vtsHotkeyExecutions = writable<VTSHotkeyExecution[]>([]);
export const vtsEmotionCounts = writable<Record<string, number>>({});
export const vtsAnimations = writable<string[]>([]);

socket.on("vts_status", (status: VTSStatus) => {
	vtsStatus.set(status);
});

socket.on("vts_expression_change", (expression: string) => {
	vtsExpressionHistory.update(history => {
		return [...history.slice(-19), expression];
	});
	vtsEmotionCounts.update(counts => {
		const newCounts = { ...counts };
		newCounts[expression] = (newCounts[expression] || 0) + 1;
		return newCounts;
	});
});

socket.on("vts_hotkey_executed", (execution: VTSHotkeyExecution) => {
	vtsHotkeyExecutions.update(executions => {
		return [execution, ...executions].slice(0, 50);
	});
});

socket.on("vts_animations", (animations: string[]) => {
	vtsAnimations.set(animations);
});

////// NOTIFICATIONS

export interface Notification {
	id: string;
	type: 'info' | 'success' | 'warning' | 'error';
	title: string;
	message: string;
	timestamp: string;
	read: boolean;
}

export const notifications = writable<Notification[]>([]);
export const unreadNotifications = writable(0);

socket.on("notification", (notification: Notification) => {
	notifications.update(n => [notification, ...n].slice(0, 50));
	unreadNotifications.update(n => n + 1);
	
	// Show toast based on notification type
	switch(notification.type) {
		case 'success':
			toast.success(notification.title, { description: notification.message });
			break;
		case 'warning':
			toast.warning(notification.title, { description: notification.message });
			break;
		case 'error':
			toast.error(notification.title, { description: notification.message });
			break;
		default:
			toast.info(notification.title, { description: notification.message });
	}
});

export function markNotificationRead(id: string) {
	notifications.update(n => n.map(notif => 
		notif.id === id ? { ...notif, read: true } : notif
	));
	unreadNotifications.update(n => Math.max(0, n - 1));
}

export function markAllNotificationsRead() {
	notifications.update(n => n.map(notif => ({ ...notif, read: true })));
	unreadNotifications.set(0);
}

export function clearNotifications() {
	notifications.set([]);
	unreadNotifications.set(0);
}