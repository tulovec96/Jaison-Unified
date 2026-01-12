<script lang="ts">
  import { Play, Copy, RotateCw } from 'lucide-svelte';
  import { writable } from 'svelte/store';

  let endpoint = 'http://localhost:7272/api/text';
  let method: 'GET' | 'POST' = 'POST';
  let body = JSON.stringify({ text: 'Hello, JAIson!' }, null, 2);
  let response = writable<string>('');
  let loading = writable<boolean>(false);
  let error = writable<string>('');

  const presets = [
    { name: 'Simple Message', body: { text: 'Hello!' } },
    { name: 'Complex Query', body: { text: 'What is machine learning?', model: 'advanced' } },
    { name: 'Health Check', method: 'GET' as const, endpoint: 'http://localhost:7272/health' },
  ];

  async function sendRequest() {
    loading.set(true);
    error.set('');
    response.set('');

    try {
      const init: RequestInit = {
        method,
        headers: {
          'Content-Type': 'application/json'
        }
      };

      if (method === 'POST') {
        init.body = body;
      }

      const res = await fetch(endpoint, init);
      const data = await res.json();
      response.set(JSON.stringify(data, null, 2));
    } catch (e) {
      error.set(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      loading.set(false);
    }
  }

  function loadPreset(preset: any) {
    endpoint = preset.endpoint || endpoint;
    method = preset.method || 'POST';
    if (preset.body) {
      body = JSON.stringify(preset.body, null, 2);
    }
  }

  function copyResponse() {
    if ($response) {
      navigator.clipboard.writeText($response);
      alert('Response copied!');
    }
  }

  function resetForm() {
    endpoint = 'http://localhost:7272/api/text';
    method = 'POST';
    body = JSON.stringify({ text: 'Hello, JAIson!' }, null, 2);
    response.set('');
    error.set('');
  }
</script>

<div class="space-y-6">
  <h1 class="text-4xl font-bold">API Playground</h1>

  <!-- Presets -->
  <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
    <h3 class="font-semibold mb-3">Quick Presets</h3>
    <div class="flex gap-2 flex-wrap">
      {#each presets as preset}
        <button
          on:click={() => loadPreset(preset)}
          class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded text-sm transition"
        >
          {preset.name}
        </button>
      {/each}
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <!-- Request Panel -->
    <div class="space-y-4">
      <h2 class="text-xl font-semibold">Request</h2>

      <div class="bg-gray-800 rounded-lg p-4 border border-gray-700 space-y-4">
        <!-- Method & Endpoint -->
        <div class="space-y-2">
          <label class="text-sm text-gray-400">Method</label>
          <div class="flex gap-2">
            {#each ['GET', 'POST'] as m}
              <button
                on:click={() => (method = m)}
                class={`px-3 py-1.5 rounded text-sm transition ${
                  method === m
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                {m}
              </button>
            {/each}
          </div>
        </div>

        <!-- Endpoint -->
        <div class="space-y-2">
          <label class="text-sm text-gray-400">Endpoint</label>
          <input
            type="text"
            bind:value={endpoint}
            class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm"
            placeholder="http://localhost:7272/api/text"
          />
        </div>

        <!-- Body -->
        {#if method === 'POST'}
          <div class="space-y-2">
            <label class="text-sm text-gray-400">Request Body (JSON)</label>
            <textarea
              bind:value={body}
              class="w-full h-40 bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm font-mono"
              placeholder="Enter JSON body..."
            />
          </div>
        {/if}

        <!-- Actions -->
        <div class="flex gap-2">
          <button
            on:click={sendRequest}
            disabled={$loading}
            class="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded transition disabled:opacity-50"
          >
            <Play class="w-4 h-4" />
            {$loading ? 'Sending...' : 'Send Request'}
          </button>
          <button
            on:click={resetForm}
            class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded transition"
          >
            <RotateCw class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Response Panel -->
    <div class="space-y-4">
      <h2 class="text-xl font-semibold">Response</h2>

      <div class="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden flex flex-col h-96">
        {#if $error}
          <div class="bg-red-900/30 border-b border-red-700 p-4">
            <p class="text-red-300 text-sm">{$error}</p>
          </div>
        {/if}

        {#if $response}
          <pre class="flex-1 overflow-auto p-4 text-sm font-mono text-gray-300"><code>{$response}</code></pre>
          <div class="border-t border-gray-700 p-2 bg-gray-900 flex justify-end">
            <button
              on:click={copyResponse}
              class="flex items-center gap-1.5 px-2 py-1.5 bg-blue-600 hover:bg-blue-700 rounded text-sm transition"
            >
              <Copy class="w-4 h-4" />
              Copy
            </button>
          </div>
        {:else}
          <div class="flex items-center justify-center h-full text-gray-500">
            <p>Response will appear here</p>
          </div>
        {/if}
      </div>
    </div>
  </div>

  <!-- Documentation -->
  <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
    <h3 class="font-semibold mb-3">Available Endpoints</h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
      <div>
        <p class="font-mono text-blue-400">POST /api/text</p>
        <p class="text-gray-400">Send a text message and get response</p>
      </div>
      <div>
        <p class="font-mono text-blue-400">GET /health</p>
        <p class="text-gray-400">Health check endpoint</p>
      </div>
      <div>
        <p class="font-mono text-blue-400">GET /status</p>
        <p class="text-gray-400">System status and metrics</p>
      </div>
      <div>
        <p class="font-mono text-blue-400">POST /api/audio</p>
        <p class="text-gray-400">Send audio and get response</p>
      </div>
    </div>
  </div>
</div>
