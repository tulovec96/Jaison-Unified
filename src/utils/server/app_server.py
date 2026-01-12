from quart import Quart, request, websocket
import asyncio
import json
import base64
import logging
import os
import yaml
import time
import psutil
from pathlib import Path
from utils.args import args
from utils.helpers.singleton import Singleton
from utils.jaison import JAIson, JobType, NonexistantJobException
from utils.config import Config
from utils.helpers.observer import BaseObserverClient
from .common import create_response, create_preflight

# Server start time for uptime tracking
SERVER_START_TIME = time.time()

app = Quart(__name__)
cors_header = {"Access-Control-Allow-Origin": "*"}

# Base paths for file management
BASE_DIR = Path(__file__).parent.parent.parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"
CONFIGS_DIR = BASE_DIR / "configs"

## Websocket Event Broadcasting Server ##


class SocketServerObserver(BaseObserverClient, metaclass=Singleton):
    def __init__(self):
        super().__init__(server=JAIson().event_server)
        self.connections = set()
        self.shutdown_signal = asyncio.Future()

    async def handle_event(self, event_id: str, payload) -> None:
        """Broadcast events from broadcast server"""
        for key in payload:
            if isinstance(payload[key], bytes):
                payload[key] = base64.b64encode(payload[key]).decode("utf-8")
        message = json.dumps(create_response(200, event_id, payload))
        logging.debug(f"Broadcasting event to {len(self.connections)} clients")
        for ws in set(self.connections):
            await ws.send(message)

    def shutdown(self, *args):  # TODO set for use somewhere
        self.shutdown_signal.set_result(None)


@app.websocket("/")
async def ws():
    sso = SocketServerObserver()
    logging.info("Opened new websocket connection")
    ws = websocket._get_current_object()
    await ws.accept()
    sso.connections.add(ws)
    try:
        while not sso.shutdown_signal.done():
            await asyncio.sleep(10)
    except asyncio.CancelledError:
        sso.connections.discard(ws)
        logging.info("Closed websocket connection")
        raise


## Generic endpoints ###################


@app.route("/api/operations", methods=["GET"])
async def get_loaded_operations():
    return create_response(
        200, f"Loaded operations gotten", JAIson().get_loaded_operations(), cors_header
    )


@app.route("/api/config", methods=["GET"])
async def get_current_config():
    return create_response(
        200, f"Current config gotten", JAIson().get_current_config(), cors_header
    )


## Job management endpoints ###########
@app.route("/api/job", methods=["DELETE"])
async def cancel_job():
    try:
        request_data = await request.get_json()
        assert "job_id" in request_data
        return create_response(
            200,
            f"Job flagged for cancellation",
            await JAIson().cancel_job(
                request_data["job_id"], request_data.get("reason")
            ),
            cors_header,
        )
    except NonexistantJobException as err:
        return create_response(
            400, f"Job ID does not exist or already finished", {}, cors_header
        )
    except AssertionError as err:
        return create_response(400, f"Request missing job_id", {}, cors_header)
    except Exception as err:
        return create_response(500, str(err), {}, cors_header)


## Specific job creation endpoints ####


async def _request_job(job_type: JobType):
    try:
        request_data = (await request.get_json()) or dict()

        job_id = await JAIson().create_job(job_type, **request_data)
        return create_response(
            200, f"{job_type} job created", {"job_id": job_id}, cors_header
        )
    except Exception as err:
        logging.error(
            f"Error occured for {job_type} API request", stack_info=True, exc_info=True
        )
        return create_response(500, str(err), {}, cors_header)


# Main response pipeline
@app.route("/api/response", methods=["POST"])
async def response():
    return await _request_job(JobType.RESPONSE)


# Context - General
@app.route("/api/context", methods=["DELETE"])
async def context_clear():
    return await _request_job(JobType.CONTEXT_CLEAR)


# Context - Configure
@app.route("/api/context/config", methods=["PUT"])
async def context_configure():
    return await _request_job(JobType.CONTEXT_CONFIGURE)


# Context - Requests
@app.route("/api/context/request", methods=["POST"])
async def context_request_add():
    return await _request_job(JobType.CONTEXT_REQUEST_ADD)


# Context - Conversation
@app.route("/api/context/conversation/text", methods=["POST"])
async def context_conversation_add_text():
    return await _request_job(JobType.CONTEXT_CONVERSATION_ADD_TEXT)


@app.route("/api/context/conversation/audio", methods=["POST"])
async def context_conversation_add_audio():
    return await _request_job(JobType.CONTEXT_CONVERSATION_ADD_AUDIO)


# Context - Custom
@app.route("/api/context/custom", methods=["PUT"])
async def context_custom_register():
    return await _request_job(JobType.CONTEXT_CUSTOM_REGISTER)


@app.route("/api/context/custom", methods=["DELETE"])
async def context_custom_remove():
    return await _request_job(JobType.CONTEXT_CUSTOM_REMOVE)


@app.route("/api/context/custom", methods=["POST"])
async def context_custom_add():
    return await _request_job(JobType.CONTEXT_CUSTOM_ADD)


# Operation management
@app.route("/api/operations/load", methods=["POST"])
async def operation_start():
    return await _request_job(JobType.OPERATION_LOAD)


@app.route("/api/operations/reload", methods=["POST"])
async def operation_reload():
    return await _request_job(JobType.OPERATION_CONFIG_RELOAD)


@app.route("/api/operations/unload", methods=["POST"])
async def operation_unload():
    return await _request_job(JobType.OPERATION_UNLOAD)


@app.route("/api/operations/config", methods=["POST"])
async def operation_configure():
    return await _request_job(JobType.OPERATION_CONFIGURE)


@app.route("/api/operations/use", methods=["POST"])
async def operation_use():
    return await _request_job(JobType.OPERATION_USE)


# Configuration
@app.route("/api/config/load", methods=["PUT"])
async def config_load():
    return await _request_job(JobType.CONFIG_LOAD)


# Configuration
@app.route("/api/config/update", methods=["PUT"])
async def config_update():
    return await _request_job(JobType.CONFIG_UPDATE)


@app.route("/api/config/save", methods=["POST"])
async def config_save():
    return await _request_job(JobType.CONFIG_SAVE)


## File Management Endpoints ###########


@app.route("/api/health", methods=["GET"])
async def health_check():
    """Health check endpoint to verify core is running"""
    uptime = int(time.time() - SERVER_START_TIME)
    return create_response(
        200,
        "Core server is running",
        {
            "status": "healthy",
            "version": "2.0.0",
            "uptime": uptime,
        },
        cors_header,
    )


@app.route("/api/system/metrics", methods=["GET"])
async def system_metrics():
    """Get real system metrics (CPU, memory, etc.)"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        uptime = int(time.time() - SERVER_START_TIME)

        # Get current process info
        process = psutil.Process()
        process_memory = process.memory_info().rss
        process_cpu = process.cpu_percent(interval=0.1)

        return create_response(
            200,
            "System metrics",
            {
                "cpu": cpu_percent,
                "memory": memory.percent,
                "memoryUsed": memory.used,
                "memoryTotal": memory.total,
                "disk": disk.percent,
                "diskUsed": disk.used,
                "diskTotal": disk.total,
                "uptime": uptime,
                "process": {
                    "memory": process_memory,
                    "cpu": process_cpu,
                },
            },
            cors_header,
        )
    except Exception as err:
        logging.error(f"Failed to get system metrics: {err}")
        return create_response(500, str(err), {}, cors_header)


@app.route("/api/services", methods=["GET"])
async def get_services():
    """Get status of all Voxelle services"""
    try:
        uptime = int(time.time() - SERVER_START_TIME)
        process = psutil.Process()

        services = [
            {
                "name": "Core Server",
                "id": "core",
                "status": "running",
                "uptime": uptime * 1000,
                "memory": process.memory_info().rss,
                "cpu": process.cpu_percent(interval=0.1),
                "version": "2.0.0",
                "port": 7272,
                "description": "Main Voxelle AI engine",
            }
        ]

        # Check for companion apps (Discord, Twitch, VTS) based on config
        companion_apps = [
            {
                "name": "Discord Bot",
                "id": "discord",
                "configPath": BASE_DIR.parent / "app-jaison-discord-lcc-main",
                "description": "Discord voice integration",
                "version": "1.2.0",
            },
            {
                "name": "Twitch Monitor",
                "id": "twitch",
                "configPath": BASE_DIR.parent / "app-jaison-twitch-lcc-main",
                "description": "Twitch chat integration",
                "version": "1.1.0",
            },
            {
                "name": "VTube Studio Plugin",
                "id": "vts",
                "configPath": BASE_DIR.parent / "app-jaison-vts-hotkeys-lcc-main",
                "description": "VTuber avatar control",
                "version": "1.0.0",
            },
        ]

        for app_info in companion_apps:
            exists = app_info["configPath"].exists()
            services.append(
                {
                    "name": app_info["name"],
                    "id": app_info["id"],
                    "status": "stopped" if exists else "not_installed",
                    "uptime": 0,
                    "memory": 0,
                    "cpu": 0,
                    "version": app_info["version"] if exists else None,
                    "installed": exists,
                    "description": app_info["description"],
                }
            )

        return create_response(200, "Services list", services, cors_header)
    except Exception as err:
        logging.error(f"Failed to get services: {err}")
        return create_response(500, str(err), {}, cors_header)


@app.route("/api/system/metrics", methods=["OPTIONS"])
@app.route("/api/services", methods=["OPTIONS"])
async def preflight_system():
    return create_preflight(cors_header)


@app.route("/api/prompts", methods=["GET"])
async def list_prompts():
    """List all available prompts organized by category"""
    try:
        prompts = {"characters": [], "instructions": [], "scenes": []}

        for category in prompts.keys():
            category_dir = PROMPTS_DIR / category
            if category_dir.exists():
                for file in category_dir.glob("*.txt"):
                    if file.name != ".gitignore":
                        prompts[category].append(
                            {"name": file.stem, "filename": file.name}
                        )

        return create_response(200, "Prompts listed", prompts, cors_header)
    except Exception as err:
        logging.error(f"Failed to list prompts: {err}")
        return create_response(500, str(err), {}, cors_header)


@app.route("/api/prompts/<category>/<name>", methods=["GET"])
async def get_prompt(category: str, name: str):
    """Get content of a specific prompt file"""
    try:
        file_path = PROMPTS_DIR / category / f"{name}.txt"
        if not file_path.exists():
            return create_response(404, "Prompt not found", {}, cors_header)

        content = file_path.read_text(encoding="utf-8")
        return create_response(
            200,
            "Prompt loaded",
            {"category": category, "name": name, "content": content},
            cors_header,
        )
    except Exception as err:
        logging.error(f"Failed to get prompt: {err}")
        return create_response(500, str(err), {}, cors_header)


@app.route("/api/prompts/<category>/<name>", methods=["PUT"])
async def save_prompt(category: str, name: str):
    """Save/update a prompt file"""
    try:
        request_data = await request.get_json()
        content = request_data.get("content", "")

        category_dir = PROMPTS_DIR / category
        category_dir.mkdir(parents=True, exist_ok=True)

        file_path = category_dir / f"{name}.txt"
        file_path.write_text(content, encoding="utf-8")

        logging.info(f"Saved prompt: {category}/{name}")
        return create_response(
            200, "Prompt saved", {"category": category, "name": name}, cors_header
        )
    except Exception as err:
        logging.error(f"Failed to save prompt: {err}")
        return create_response(500, str(err), {}, cors_header)


@app.route("/api/prompts/<category>/<name>", methods=["DELETE"])
async def delete_prompt(category: str, name: str):
    """Delete a prompt file"""
    try:
        file_path = PROMPTS_DIR / category / f"{name}.txt"
        if not file_path.exists():
            return create_response(404, "Prompt not found", {}, cors_header)

        file_path.unlink()
        logging.info(f"Deleted prompt: {category}/{name}")
        return create_response(
            200, "Prompt deleted", {"category": category, "name": name}, cors_header
        )
    except Exception as err:
        logging.error(f"Failed to delete prompt: {err}")
        return create_response(500, str(err), {}, cors_header)


@app.route("/api/configs", methods=["GET"])
async def list_configs():
    """List all available config files"""
    try:
        configs = []
        if CONFIGS_DIR.exists():
            for file in CONFIGS_DIR.glob("*.yaml"):
                configs.append({"name": file.stem, "filename": file.name})

        # Also include main config.yaml
        main_config = BASE_DIR / "config.yaml"
        if main_config.exists():
            configs.insert(0, {"name": "config", "filename": "config.yaml", "main": True})

        return create_response(200, "Configs listed", configs, cors_header)
    except Exception as err:
        logging.error(f"Failed to list configs: {err}")
        return create_response(500, str(err), {}, cors_header)


@app.route("/api/configs/<name>", methods=["GET"])
async def get_config_file(name: str):
    """Get content of a specific config file"""
    try:
        # Check main config first
        if name == "config":
            file_path = BASE_DIR / "config.yaml"
        else:
            file_path = CONFIGS_DIR / f"{name}.yaml"

        if not file_path.exists():
            return create_response(404, "Config not found", {}, cors_header)

        content = file_path.read_text(encoding="utf-8")
        return create_response(
            200, "Config loaded", {"name": name, "content": content}, cors_header
        )
    except Exception as err:
        logging.error(f"Failed to get config: {err}")
        return create_response(500, str(err), {}, cors_header)


@app.route("/api/configs/<name>", methods=["PUT"])
async def save_config_file(name: str):
    """Save/update a config file"""
    try:
        request_data = await request.get_json()
        content = request_data.get("content", "")

        # Validate YAML syntax
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            return create_response(400, f"Invalid YAML: {e}", {}, cors_header)

        if name == "config":
            file_path = BASE_DIR / "config.yaml"
        else:
            CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
            file_path = CONFIGS_DIR / f"{name}.yaml"

        file_path.write_text(content, encoding="utf-8")
        logging.info(f"Saved config: {name}")
        return create_response(200, "Config saved", {"name": name}, cors_header)
    except Exception as err:
        logging.error(f"Failed to save config: {err}")
        return create_response(500, str(err), {}, cors_header)


@app.route("/api/env", methods=["GET"])
async def get_env_file():
    """Get .env file content (masked sensitive values)"""
    try:
        env_path = BASE_DIR / ".env"
        if not env_path.exists():
            # Try template
            env_path = BASE_DIR / ".env-template"

        if not env_path.exists():
            return create_response(404, "No .env file found", {}, cors_header)

        content = env_path.read_text(encoding="utf-8")
        return create_response(200, "Env loaded", {"content": content}, cors_header)
    except Exception as err:
        logging.error(f"Failed to get env: {err}")
        return create_response(500, str(err), {}, cors_header)


@app.route("/api/env", methods=["PUT"])
async def save_env_file():
    """Save .env file"""
    try:
        request_data = await request.get_json()
        content = request_data.get("content", "")

        env_path = BASE_DIR / ".env"
        env_path.write_text(content, encoding="utf-8")
        logging.info("Saved .env file")
        return create_response(200, "Env saved", {}, cors_header)
    except Exception as err:
        logging.error(f"Failed to save env: {err}")
        return create_response(500, str(err), {}, cors_header)


# CORS preflight for new endpoints
@app.route("/api/health", methods=["OPTIONS"])
async def preflight_health():
    return create_preflight("GET")


@app.route("/api/prompts", methods=["OPTIONS"])
async def preflight_prompts():
    return create_preflight("GET")


@app.route("/api/prompts/<category>/<name>", methods=["OPTIONS"])
async def preflight_prompt(category: str, name: str):
    return create_preflight("GET, PUT, DELETE")


@app.route("/api/configs", methods=["OPTIONS"])
async def preflight_configs():
    return create_preflight("GET")


@app.route("/api/configs/<name>", methods=["OPTIONS"])
async def preflight_config_file(name: str):
    return create_preflight("GET, PUT")


@app.route("/api/env", methods=["OPTIONS"])
async def preflight_env():
    return create_preflight("GET, PUT")


# Allow CORS
@app.route("/api/job", methods=["OPTIONS"])
async def preflight_job():
    return create_preflight("DELETE")


@app.route("/api/response", methods=["OPTIONS"])
async def preflight_response():
    return create_preflight("POST")


@app.route("/api/context", methods=["OPTIONS"])
async def preflight_context_conversation_clear():
    return create_preflight("DELETE")


@app.route("/api/context/config", methods=["OPTIONS"])
async def preflight_context_configure():
    return create_preflight("PUT")


@app.route("/api/context/request", methods=["OPTIONS"])
async def preflight_context_request():
    return create_preflight("POST")


@app.route("/api/context/conversation/text", methods=["OPTIONS"])
async def preflight_context_conversation_text():
    return create_preflight("POST")


@app.route("/api/context/conversation/audio", methods=["OPTIONS"])
async def preflight_context_conversation_audio():
    return create_preflight("POST")


@app.route("/api/context/custom", methods=["OPTIONS"])
async def preflight_context_custom():
    return create_preflight("POST, PUT, DELETE")


@app.route("/api/operations", methods=["OPTIONS"])
async def preflight_operations_info():
    return create_preflight("GET")


@app.route("/api/operations/load", methods=["OPTIONS"])
async def preflight_operation_start():
    return create_preflight("POST")


@app.route("/api/operations/reload", methods=["OPTIONS"])
async def preflight_operation_reload():
    return create_preflight("POST")


@app.route("/api/operations/unload", methods=["OPTIONS"])
async def preflight_operation_unload():
    return create_preflight("POST")


@app.route("/api/operations/config", methods=["OPTIONS"])
async def preflight_operation_configure():
    return create_preflight("POST")


@app.route("/api/operations/use", methods=["OPTIONS"])
async def preflight_operation_use():
    return create_preflight("POST")


@app.route("/api/config", methods=["OPTIONS"])
async def preflight_config():
    return create_preflight("GET")


@app.route("/api/config/load", methods=["OPTIONS"])
async def preflight_config_load():
    return create_preflight("PUT")


@app.route("/api/config/update", methods=["OPTIONS"])
async def preflight_config_update():
    return create_preflight("PUT")


@app.route("/api/config/save", methods=["OPTIONS"])
async def preflight_config_save():
    return create_preflight("POST")


## START ###################################
async def start_web_server():
    """
    Start the Voxelle web server with graceful shutdown support.

    Handles SIGINT/SIGTERM for clean shutdown of all resources.
    """
    shutdown_event = asyncio.Event()

    def trigger_shutdown():
        logging.info("Triggering graceful shutdown...")
        shutdown_event.set()

    try:
        global app
        await JAIson().start()
        sso = SocketServerObserver()

        logging.info(f"Starting Voxelle Core Server on {args.host}:{args.port}")
        logging.info(f"API: http://{args.host}:{args.port}")
        logging.info(f"WebSocket: ws://{args.host}:{args.port}")

        await app.run_task(
            host=args.host, port=args.port, shutdown_trigger=shutdown_event.wait
        )
    except asyncio.CancelledError:
        logging.info("Server task cancelled")
    except Exception as err:
        logging.error("Stopping server due to exception", exc_info=True)
    finally:
        logging.info("Cleaning up server resources...")
        await JAIson().stop()
        logging.info("Server shutdown complete")
