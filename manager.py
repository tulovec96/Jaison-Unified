#!/usr/bin/env python3
"""
Voxelle Unified System Manager
Manage running the core server, applications, and dependencies
"""

import argparse
import subprocess
import os
import sys
import json
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Optional


# ANSI colors for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def colored(text: str, color: str) -> str:
    """Apply color to text if terminal supports it"""
    if sys.platform == "win32":
        os.system("")  # Enable ANSI on Windows
    return f"{color}{text}{Colors.ENDC}"


def get_base_dir():
    """Get the base directory of this project"""
    return Path(__file__).parent.absolute()


def find_python_deps() -> List[Path]:
    """Find all directories with requirements.txt"""
    base_dir = get_base_dir()
    return list(base_dir.rglob("requirements.txt"))


def find_node_deps() -> List[Path]:
    """Find all directories with package.json (excluding node_modules)"""
    base_dir = get_base_dir()
    results = []
    for p in base_dir.rglob("package.json"):
        if "node_modules" not in str(p):
            results.append(p)
    return results


def get_pip_command() -> List[str]:
    """Get the correct pip command for the current environment"""
    return [sys.executable, "-m", "pip"]


def get_npm_command() -> str:
    """Get npm or pnpm if available"""
    if shutil.which("pnpm"):
        return "pnpm"
    return "npm"


def install_python_deps(
    req_path: Path, upgrade: bool = False
) -> Tuple[Path, bool, str]:
    """Install Python dependencies from a requirements.txt file"""
    try:
        cmd = get_pip_command() + ["install", "-r", str(req_path)]
        if upgrade:
            cmd.insert(-2, "--upgrade")

        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=req_path.parent
        )

        success = result.returncode == 0
        message = result.stdout if success else result.stderr
        return (req_path, success, message)
    except Exception as e:
        return (req_path, False, str(e))


def install_node_deps(pkg_path: Path, upgrade: bool = False) -> Tuple[Path, bool, str]:
    """Install Node.js dependencies from a package.json file"""
    try:
        npm = get_npm_command()
        cmd = [npm, "update" if upgrade else "install"]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=pkg_path.parent,
            shell=True if sys.platform == "win32" else False,
        )

        success = result.returncode == 0
        message = result.stdout if success else result.stderr
        return (pkg_path, success, message)
    except Exception as e:
        return (pkg_path, False, str(e))


def check_outdated_python(req_path: Path) -> Tuple[Path, List[dict]]:
    """Check for outdated Python packages"""
    try:
        cmd = get_pip_command() + ["list", "--outdated", "--format=json"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            outdated = json.loads(result.stdout) if result.stdout else []
            return (req_path, outdated)
        return (req_path, [])
    except:
        return (req_path, [])


def check_outdated_node(pkg_path: Path) -> Tuple[Path, str]:
    """Check for outdated Node.js packages"""
    try:
        npm = get_npm_command()
        cmd = [npm, "outdated"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=pkg_path.parent,
            shell=True if sys.platform == "win32" else False,
        )
        return (pkg_path, result.stdout)
    except Exception as e:
        return (pkg_path, str(e))


def start_core(args):
    """Start the core Voxelle server"""
    base_dir = get_base_dir()
    os.chdir(base_dir)

    cmd = [sys.executable, "src/main.py"]
    if args.debug:
        cmd.append("--debug")

    print(colored("🚀 Starting Voxelle Core Server...", Colors.GREEN))
    print(f"   Command: {' '.join(cmd)}")
    print(f"   API: http://localhost:7272")
    print(f"   WebSocket: ws://localhost:7272")

    subprocess.run(cmd)


def start_discord(args):
    """Start the Discord bot integration"""
    base_dir = get_base_dir()
    os.chdir(base_dir / "apps" / "discord")

    # Check for .env file
    if not Path(".env").exists():
        print("❌ Discord bot requires .env file")
        print("   Copy .env-template to .env and add your Discord bot token")
        return

    cmd = [sys.executable, "src/main.py"]
    if args.debug:
        cmd.append("--debug")

    print("🤖 Starting Discord Bot Integration...")
    print(f"   Make sure the core server is running on ws://127.0.0.1:7272")

    subprocess.run(cmd)


def start_twitch(args):
    """Start the Twitch integration"""
    base_dir = get_base_dir()
    app_dir = base_dir / "apps" / "twitch"
    os.chdir(app_dir)

    # Check for .env file
    if not Path(".env").exists():
        print("❌ Twitch integration requires .env file")
        print("   Copy .env-template to .env with your Twitch credentials")
        return

    # Check if tokens exist, if not authenticate
    if not Path("tokens").exists():
        print("🔑 Running Twitch authentication...")
        subprocess.run([sys.executable, "src/auth.py"])

    cmd = [sys.executable, "src/main.py"]
    if args.debug:
        cmd.append("--debug")

    print("🎮 Starting Twitch Integration...")
    print(f"   Make sure the core server is running on ws://127.0.0.1:7272")

    subprocess.run(cmd)


def start_vts(args):
    """Start the VTube Studio integration"""
    base_dir = get_base_dir()
    os.chdir(base_dir / "apps" / "vts")

    cmd = [sys.executable, "src/main.py"]
    if args.debug:
        cmd.append("--debug")

    print("🎭 Starting VTube Studio Integration...")
    print(f"   Make sure VTube Studio API is enabled on ws://localhost:8001")
    print(f"   Make sure the core server is running on ws://localhost:7272")

    subprocess.run(cmd)


def show_status(args):
    """Show status of the system"""
    base_dir = get_base_dir()

    print("📊 Voxelle Unified System Status")
    print("=" * 50)

    # Check core config
    config_path = base_dir / "config.yaml"
    env_path = base_dir / ".env"
    print(f"\n✓ Core Configuration:")
    print(
        f"  - config.yaml: {'✅ exists' if config_path.exists() else '❌ missing (run: python manager.py setup)'}"
    )
    print(
        f"  - .env: {'✅ exists' if env_path.exists() else '❌ missing (run: python manager.py setup)'}"
    )

    # Check apps
    apps = ["discord", "twitch", "vts"]
    for app in apps:
        app_dir = base_dir / "apps" / app
        env_file = app_dir / ".env"
        config_file = app_dir / "config.yaml"

        print(f"\n✓ {app.upper()} Integration:")
        print(f"  - Directory: {'✅' if app_dir.exists() else '❌'}")
        print(f"  - Config: {'✅' if config_file.exists() else '❌'}")
        print(f"  - .env file: {'✅' if env_file.exists() else '⚠️ optional'}")

    print("\n" + "=" * 50)


def setup_project(args):
    """Setup the project by copying template files"""
    base_dir = get_base_dir()

    print(colored("\n🔧 Voxelle Project Setup", Colors.HEADER + Colors.BOLD))
    print("=" * 50)

    # Template mappings: (source_template, destination, description)
    templates = [
        (base_dir / ".env-template", base_dir / ".env", "Root .env file"),
        (
            base_dir / "config.yaml.template",
            base_dir / "config.yaml",
            "Core config.yaml",
        ),
    ]

    # Check for app-specific templates
    apps = ["discord", "twitch", "vts"]
    for app in apps:
        app_dir = base_dir / "apps" / app
        if app_dir.exists():
            # Check for .env-template in app
            env_template = app_dir / ".env-template"
            if env_template.exists():
                templates.append(
                    (env_template, app_dir / ".env", f"{app.upper()} .env")
                )

            # Check for config.yaml.template in app
            config_template = app_dir / "config.yaml.template"
            if config_template.exists():
                templates.append(
                    (
                        config_template,
                        app_dir / "config.yaml",
                        f"{app.upper()} config.yaml",
                    )
                )

    created = []
    skipped = []
    failed = []

    print(colored("\n📋 Processing Templates", Colors.CYAN))
    print("-" * 40)

    for src, dst, description in templates:
        if not src.exists():
            print(f"  ⚠️  {description}: template not found ({src.name})")
            continue

        if dst.exists():
            if args.force:
                print(f"  🔄 {description}: overwriting (--force)")
                try:
                    shutil.copy2(src, dst)
                    created.append(description)
                except Exception as e:
                    print(f"     ❌ Error: {e}")
                    failed.append(description)
            else:
                print(f"  ⏭️  {description}: already exists (use --force to overwrite)")
                skipped.append(description)
        else:
            try:
                # Ensure parent directory exists
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"  ✅ {description}: created")
                created.append(description)
            except Exception as e:
                print(f"  ❌ {description}: failed - {e}")
                failed.append(description)

    # Create required directories
    print(colored("\n📁 Creating Directories", Colors.CYAN))
    print("-" * 40)

    directories = [
        base_dir / "logs",
        base_dir / "output" / "temp",
        base_dir / "models",
        base_dir / "apps" / "discord" / "tokens",
        base_dir / "apps" / "twitch" / "tokens",
        base_dir / "apps" / "vts" / "tokens",
    ]

    for dir_path in directories:
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"  ✅ Created: {dir_path.relative_to(base_dir)}")
            except Exception as e:
                print(f"  ❌ Failed to create {dir_path.relative_to(base_dir)}: {e}")
        else:
            print(f"  ⏭️  Exists: {dir_path.relative_to(base_dir)}")

    # Summary
    print("\n" + "=" * 50)
    print(colored("📊 Setup Summary", Colors.HEADER))
    print(f"  ✅ Created: {len(created)}")
    print(f"  ⏭️  Skipped: {len(skipped)}")
    if failed:
        print(colored(f"  ❌ Failed: {len(failed)}", Colors.RED))

    # Next steps
    print(colored("\n📝 Next Steps", Colors.YELLOW))
    print("-" * 40)
    print("  1. Edit .env and add your API keys (OpenAI, Azure, Fish, etc.)")
    print("  2. Edit config.yaml to customize your AI settings")
    print("  3. Run: python manager.py install")
    print("  4. Run: python manager.py core")
    print("=" * 50)


def install_deps(args):
    """Install all dependencies (Python and Node.js)"""
    base_dir = get_base_dir()

    print(colored("\n📦 Voxelle Dependency Installer", Colors.HEADER + Colors.BOLD))
    print("=" * 50)

    # Find all dependency files
    python_deps = find_python_deps()
    node_deps = find_node_deps()

    total = len(python_deps) + len(node_deps)
    success_count = 0
    failed = []

    # Install Python dependencies
    if python_deps:
        print(
            colored(f"\n🐍 Python Dependencies ({len(python_deps)} found)", Colors.CYAN)
        )
        print("-" * 40)

        for req_path in python_deps:
            rel_path = req_path.relative_to(base_dir)
            print(f"  📂 {rel_path.parent}...", end=" ", flush=True)

            path, success, message = install_python_deps(req_path, upgrade=args.upgrade)

            if success:
                print(colored("✓", Colors.GREEN))
                success_count += 1
            else:
                print(colored("✗", Colors.RED))
                failed.append((rel_path, message[:200]))

    # Install Node.js dependencies
    if node_deps:
        print(
            colored(f"\n📦 Node.js Dependencies ({len(node_deps)} found)", Colors.CYAN)
        )
        print("-" * 40)

        for pkg_path in node_deps:
            rel_path = pkg_path.relative_to(base_dir)
            print(f"  📂 {rel_path.parent}...", end=" ", flush=True)

            path, success, message = install_node_deps(pkg_path, upgrade=args.upgrade)

            if success:
                print(colored("✓", Colors.GREEN))
                success_count += 1
            else:
                print(colored("✗", Colors.RED))
                failed.append((rel_path, message[:200]))

    # Summary
    print("\n" + "=" * 50)
    print(colored(f"✅ Installed: {success_count}/{total}", Colors.GREEN))

    if failed:
        print(colored(f"❌ Failed: {len(failed)}", Colors.RED))
        if args.verbose:
            for path, error in failed:
                print(f"   • {path}: {error}")

    print("=" * 50)


def update_deps(args):
    """Update all dependencies to latest versions"""
    args.upgrade = True
    print(colored("\n🔄 Updating dependencies to latest versions...", Colors.YELLOW))
    install_deps(args)


def check_deps(args):
    """Check for outdated dependencies"""
    base_dir = get_base_dir()

    print(
        colored("\n🔍 Checking for Outdated Dependencies", Colors.HEADER + Colors.BOLD)
    )
    print("=" * 50)

    # Check Python
    python_deps = find_python_deps()
    if python_deps:
        print(colored("\n🐍 Python Packages", Colors.CYAN))
        print("-" * 40)

        # Check global outdated
        req_path, outdated = check_outdated_python(python_deps[0])

        if outdated:
            print(f"  {'Package':<25} {'Current':<12} {'Latest':<12}")
            print("  " + "-" * 49)
            for pkg in outdated[:15]:  # Limit to 15
                name = pkg.get("name", "unknown")
                current = pkg.get("version", "?")
                latest = pkg.get("latest_version", "?")
                print(f"  {name:<25} {current:<12} {latest:<12}")
            if len(outdated) > 15:
                print(f"  ... and {len(outdated) - 15} more")
        else:
            print(colored("  ✓ All packages up to date!", Colors.GREEN))

    # Check Node.js
    node_deps = find_node_deps()
    if node_deps:
        print(colored("\n📦 Node.js Packages", Colors.CYAN))
        print("-" * 40)

        for pkg_path in node_deps:
            rel_path = pkg_path.relative_to(base_dir)
            print(f"  📂 {rel_path.parent}:")

            path, output = check_outdated_node(pkg_path)
            if output.strip():
                for line in output.strip().split("\n")[:10]:
                    print(f"     {line}")
            else:
                print(colored("     ✓ All packages up to date!", Colors.GREEN))

    print("\n" + "=" * 50)


def install_deps_parallel(args):
    """Install dependencies in parallel for faster execution"""
    base_dir = get_base_dir()

    print(colored("\n⚡ Parallel Dependency Installer", Colors.HEADER + Colors.BOLD))
    print("=" * 50)

    python_deps = find_python_deps()
    node_deps = find_node_deps()

    results = []

    # Use ThreadPoolExecutor for parallel installation
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []

        # Submit Python installs
        for req_path in python_deps:
            future = executor.submit(install_python_deps, req_path, args.upgrade)
            futures.append(("python", future))

        # Submit Node.js installs
        for pkg_path in node_deps:
            future = executor.submit(install_node_deps, pkg_path, args.upgrade)
            futures.append(("node", future))

        # Collect results
        for dep_type, future in futures:
            try:
                path, success, message = future.result(timeout=300)
                rel_path = path.relative_to(base_dir)
                status = (
                    colored("✓", Colors.GREEN) if success else colored("✗", Colors.RED)
                )
                print(f"  {status} [{dep_type}] {rel_path.parent}")
                results.append((path, success))
            except Exception as e:
                print(f"  {colored('✗', Colors.RED)} Error: {e}")

    success_count = sum(1 for _, s in results if s)
    print(f"\n✅ Completed: {success_count}/{len(results)}")


def clean_deps(args):
    """Clean dependency caches and temporary files"""
    base_dir = get_base_dir()

    print(colored("\n🧹 Cleaning Dependency Caches", Colors.HEADER + Colors.BOLD))
    print("=" * 50)

    cleaned = []

    # Clean Python caches
    for cache_dir in base_dir.rglob("__pycache__"):
        try:
            shutil.rmtree(cache_dir)
            cleaned.append(cache_dir)
        except:
            pass

    for cache_dir in base_dir.rglob(".pytest_cache"):
        try:
            shutil.rmtree(cache_dir)
            cleaned.append(cache_dir)
        except:
            pass

    # Clean pip cache
    if args.deep:
        print("  Cleaning pip cache...")
        subprocess.run(get_pip_command() + ["cache", "purge"], capture_output=True)

    # Clean Node.js
    for node_modules in base_dir.rglob("node_modules"):
        if args.deep:
            print(f"  Removing {node_modules.relative_to(base_dir)}...")
            try:
                shutil.rmtree(node_modules)
                cleaned.append(node_modules)
            except Exception as e:
                print(f"    Error: {e}")

    # Clean npm cache
    if args.deep:
        print("  Cleaning npm cache...")
        npm = get_npm_command()
        subprocess.run(
            [npm, "cache", "clean", "--force"],
            capture_output=True,
            shell=True if sys.platform == "win32" else False,
        )

    print(colored(f"\n✅ Cleaned {len(cleaned)} directories", Colors.GREEN))


def deps_status(args):
    """Show dependency status overview"""
    base_dir = get_base_dir()

    print(colored("\n📊 Dependency Status Overview", Colors.HEADER + Colors.BOLD))
    print("=" * 50)

    python_deps = find_python_deps()
    node_deps = find_node_deps()

    print(colored("\n🐍 Python Environments", Colors.CYAN))
    print("-" * 40)
    for req_path in python_deps:
        rel_path = req_path.relative_to(base_dir)

        # Count packages
        with open(req_path, "r") as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
            pkg_count = len(lines)

        # Check for venv
        venv_exists = (req_path.parent / "venv").exists() or (
            req_path.parent / ".venv"
        ).exists()
        venv_status = (
            colored("✓ venv", Colors.GREEN)
            if venv_exists
            else colored("○ no venv", Colors.YELLOW)
        )

        print(f"  📂 {rel_path.parent}")
        print(f"     Packages: {pkg_count} | {venv_status}")

    print(colored("\n📦 Node.js Projects", Colors.CYAN))
    print("-" * 40)
    for pkg_path in node_deps:
        rel_path = pkg_path.relative_to(base_dir)

        # Read package.json
        with open(pkg_path, "r") as f:
            pkg_data = json.load(f)

        deps = len(pkg_data.get("dependencies", {}))
        dev_deps = len(pkg_data.get("devDependencies", {}))

        # Check for node_modules
        nm_exists = (pkg_path.parent / "node_modules").exists()
        nm_status = (
            colored("✓ installed", Colors.GREEN)
            if nm_exists
            else colored("○ not installed", Colors.YELLOW)
        )

        print(f"  📂 {rel_path.parent}")
        print(f"     Dependencies: {deps} | DevDeps: {dev_deps} | {nm_status}")

    print("\n" + "=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="Voxelle Unified System Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manager.py setup             # Initial project setup (copy templates)
  python manager.py setup --force     # Overwrite existing config files
  python manager.py core              # Start core server
  python manager.py discord           # Start Discord bot
  python manager.py twitch            # Start Twitch integration
  python manager.py vts               # Start VTube Studio integration
  python manager.py frontend          # Start frontend dev server
  python manager.py status            # Show system status
  
  python manager.py install           # Install all dependencies
  python manager.py install --upgrade # Install and upgrade all
  python manager.py update            # Update all dependencies
  python manager.py check             # Check for outdated packages
  python manager.py clean             # Clean caches
  python manager.py clean --deep      # Deep clean (removes node_modules)
  python manager.py deps              # Show dependency status
        """,
    )

    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Setup command
    setup_parser = subparsers.add_parser(
        "setup", help="Initial project setup (copy templates)"
    )
    setup_parser.add_argument(
        "--force", "-f", action="store_true", help="Overwrite existing config files"
    )

    # Service commands
    subparsers.add_parser("core", help="Start the core Voxelle server")
    subparsers.add_parser("discord", help="Start Discord bot integration")
    subparsers.add_parser("twitch", help="Start Twitch integration")
    subparsers.add_parser("vts", help="Start VTube Studio integration")
    subparsers.add_parser("frontend", help="Start frontend development server")
    subparsers.add_parser("status", help="Show system status")

    # Dependency commands
    install_parser = subparsers.add_parser("install", help="Install all dependencies")
    install_parser.add_argument(
        "--upgrade", "-u", action="store_true", help="Upgrade packages"
    )
    install_parser.add_argument(
        "--parallel", "-p", action="store_true", help="Install in parallel"
    )

    subparsers.add_parser("update", help="Update all dependencies to latest")
    subparsers.add_parser("check", help="Check for outdated dependencies")

    clean_parser = subparsers.add_parser("clean", help="Clean dependency caches")
    clean_parser.add_argument(
        "--deep", action="store_true", help="Deep clean (removes node_modules)"
    )

    subparsers.add_parser("deps", help="Show dependency status overview")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "setup":
        if not hasattr(args, "force"):
            args.force = False
        setup_project(args)
    elif args.command == "core":
        start_core(args)
    elif args.command == "discord":
        start_discord(args)
    elif args.command == "twitch":
        start_twitch(args)
    elif args.command == "vts":
        start_vts(args)
    elif args.command == "frontend":
        start_frontend(args)
    elif args.command == "status":
        show_status(args)
    elif args.command == "install":
        if hasattr(args, "parallel") and args.parallel:
            install_deps_parallel(args)
        else:
            if not hasattr(args, "upgrade"):
                args.upgrade = False
            install_deps(args)
    elif args.command == "update":
        args.upgrade = True
        args.verbose = getattr(args, "verbose", False)
        install_deps(args)
    elif args.command == "check":
        check_deps(args)
    elif args.command == "clean":
        if not hasattr(args, "deep"):
            args.deep = False
        clean_deps(args)
    elif args.command == "deps":
        deps_status(args)


def start_frontend(args):
    """Start the frontend development server"""
    base_dir = get_base_dir()
    frontend_dir = base_dir / "apps" / "frontend"
    os.chdir(frontend_dir)

    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        print(colored("📦 Installing frontend dependencies...", Colors.YELLOW))
        npm = get_npm_command()
        subprocess.run(
            [npm, "install"], shell=True if sys.platform == "win32" else False
        )

    npm = get_npm_command()
    print(colored("🖥️  Starting Frontend Development Server...", Colors.GREEN))
    print(f"   URL: http://localhost:5173")
    print(f"   Using: {npm}")

    subprocess.run(
        [npm, "run", "dev"], shell=True if sys.platform == "win32" else False
    )


if __name__ == "__main__":
    main()
