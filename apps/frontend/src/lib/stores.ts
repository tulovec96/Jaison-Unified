import { writable } from 'svelte/store';

export interface ServiceStatus {
  name: string;
  status: 'running' | 'stopped' | 'error' | 'starting';
  uptime: number;
  memory: number;
  cpu: number;
  version?: string;
  lastPing?: number;
}

export interface SystemMetrics {
  cpu: number;
  memory: number;
  memoryTotal: number;
  latency: number;
  requestsPerSecond: number;
  errors: number;
  uptime: number;
  activeJobs: number;
  completedJobs: number;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'warn' | 'error' | 'debug';
  service: string;
  message: string;
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

export const services = writable<ServiceStatus[]>([
  { name: 'Core Server', status: 'running', uptime: 3600000, memory: 512000, cpu: 15, version: '2.0.0' },
  { name: 'Discord Bot', status: 'running', uptime: 3500000, memory: 256000, cpu: 8, version: '1.2.0' },
  { name: 'Twitch Monitor', status: 'running', uptime: 3400000, memory: 128000, cpu: 5, version: '1.1.0' },
  { name: 'VTube Studio Plugin', status: 'stopped', uptime: 0, memory: 0, cpu: 0, version: '1.0.0' }
]);

export const metrics = writable<SystemMetrics>({
  cpu: 15,
  memory: 45,
  memoryTotal: 16384,
  latency: 125,
  requestsPerSecond: 42,
  errors: 0,
  uptime: 0,
  activeJobs: 0,
  completedJobs: 0
});

export const logs = writable<LogEntry[]>([]);

export const notifications = writable<Notification[]>([]);

export const theme = writable<'light' | 'dark'>('dark');

export const isConnected = writable(false);

// Health check status
export const healthStatus = writable<{
  overall: 'healthy' | 'degraded' | 'unhealthy';
  checks: {
    name: string;
    status: 'pass' | 'fail' | 'warn';
    message?: string;
  }[];
}>({
  overall: 'healthy',
  checks: []
});
