"""Server management commands for liveapi CLI."""

import sys
import subprocess
import signal
import os
import time
from pathlib import Path


def cmd_run(args):
    """Run the FastAPI application with uvicorn."""
    # Determine PID file path
    pid_file = args.pid_file
    if not pid_file:
        metadata_dir = Path.cwd() / ".liveapi"
        metadata_dir.mkdir(exist_ok=True)
        pid_file = metadata_dir / "uvicorn.pid"
    else:
        pid_file = Path(pid_file)

    # Check if already running
    if pid_file.exists():
        try:
            with open(pid_file, "r") as f:
                old_pid = int(f.read().strip())
            # Check if process is still running
            os.kill(old_pid, 0)  # Doesn't actually kill, just checks if process exists
            print(f"❌ FastAPI server already running (PID: {old_pid})")
            print(f"   Port {args.port} is in use by existing server")
            print("   Run 'liveapi kill' to stop it first, then try again")
            return
        except (OSError, ProcessLookupError, ValueError):
            # Process doesn't exist or PID file is invalid, remove stale PID file
            pid_file.unlink(missing_ok=True)

    # Build uvicorn command
    cmd = ["uvicorn", args.app, "--host", args.host, "--port", str(args.port)]

    if not args.no_reload:
        cmd.append("--reload")

    if args.background:
        # Run in background
        print("🚀 Starting FastAPI server in background...")
        print(f"   App: {args.app}")
        print(f"   Host: {args.host}:{args.port}")
        print(f"   PID file: {pid_file}")

        # Start process in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,  # Detach from parent process
        )

        # Save PID to file
        with open(pid_file, "w") as f:
            f.write(str(process.pid))

        print(f"✅ Server started (PID: {process.pid})")
        print("   Use 'liveapi kill' to stop the server")
    else:
        # Run in foreground
        print("🚀 Starting FastAPI server...")
        print(f"   App: {args.app}")
        print(f"   Host: {args.host}:{args.port}")
        print("   Press Ctrl+C to stop")

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start server: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n⚠️  Server stopped by user")


def cmd_kill(args):
    """Stop the background FastAPI application."""
    # Determine PID file path
    pid_file = args.pid_file
    if not pid_file:
        metadata_dir = Path.cwd() / ".liveapi"
        pid_file = metadata_dir / "uvicorn.pid"
    else:
        pid_file = Path(pid_file)

    if not pid_file.exists():
        print("❌ No running server found (PID file not found)")
        print(f"   Expected PID file: {pid_file}")
        return

    try:
        with open(pid_file, "r") as f:
            pid = int(f.read().strip())

        # Try to terminate the process gracefully
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"✅ Sent termination signal to server (PID: {pid})")

            # Wait a bit and check if process is still running
            time.sleep(2)

            try:
                os.kill(pid, 0)  # Check if still running
                print("⚠️  Process still running, sending SIGKILL...")
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass  # Process already terminated

        except ProcessLookupError:
            print(f"⚠️  Process {pid} not found (already stopped)")

        # Remove PID file
        pid_file.unlink(missing_ok=True)
        print("🔹 Cleaned up PID file")

    except (ValueError, OSError) as e:
        print(f"❌ Error stopping server: {e}")
        # Clean up invalid PID file
        pid_file.unlink(missing_ok=True)
        sys.exit(1)


def cmd_ping(args):
    """Check health of local development server."""
    import requests

    # Determine PID file path
    pid_file = args.pid_file
    if not pid_file:
        metadata_dir = Path.cwd() / ".liveapi"
        pid_file = metadata_dir / "uvicorn.pid"
    else:
        pid_file = Path(pid_file)

    # Check if server is running
    if not pid_file.exists():
        print("❌ No development server running")
        print("   Start with 'liveapi run' first")
        sys.exit(1)

    try:
        with open(pid_file, "r") as f:
            pid = int(f.read().strip())

        # Check if process is still running
        try:
            os.kill(pid, 0)  # Check if process exists
        except ProcessLookupError:
            print("❌ Development server not running (stale PID file)")
            print("   PID file exists but process is dead")
            print("   Run 'liveapi kill' to clean up, then 'liveapi run'")
            sys.exit(1)

        print(f"🔍 Checking health of local server (PID: {pid})")

        # Try to determine server URL from running processes
        # For now, assume default localhost:8000 and try /health endpoint
        health_url = "http://localhost:8000/health"

        try:
            start_time = time.time()
            response = requests.get(health_url, timeout=5)
            end_time = time.time()

            response_time = round((end_time - start_time) * 1000, 2)

            if response.status_code == 200:
                print("✅ Server healthy!")
                print(f"   Health endpoint: {health_url}")
                print(f"   Response time: {response_time}ms")
                print(f"   Process ID: {pid}")
            elif response.status_code == 404:
                # Try root endpoint if /health doesn't exist
                root_url = "http://localhost:8000/"
                try:
                    root_response = requests.get(root_url, timeout=5)
                    if root_response.status_code < 400:
                        print("✅ Server running!")
                        print(f"   Root endpoint: {root_url}")
                        print("   No /health endpoint found")
                        print(f"   Process ID: {pid}")
                    else:
                        print("⚠️  Server responding with errors")
                        print(f"   Status: {root_response.status_code}")
                except Exception:
                    print("❌ Server not responding on localhost:8000")
            else:
                print("⚠️  Health check failed")
                print(f"   Status: {response.status_code}")
                print(f"   Response time: {response_time}ms")

        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server on localhost:8000")
            print(f"   Process {pid} is running but not accepting connections")
            print("   Server may be starting up or on different port")
        except requests.exceptions.Timeout:
            print("❌ Health check timeout")
            print("   Server may be overloaded or hanging")

    except (ValueError, OSError) as e:
        print(f"❌ Error reading PID file: {e}")
        sys.exit(1)
