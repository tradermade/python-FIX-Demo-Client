import subprocess
import sys
import os
from dotenv import dotenv_values

DOCKER_COMPOSE_FILE = "docker-compose.yml"
SERVICE_NAME = "python-fix-client"
SRC_DIR = os.path.join(os.path.dirname(__file__), "src")
CONFIG_FILE = os.path.join(SRC_DIR, "clientLocal.cfg")  # ✅ output filename for the FIX config

# -------------------------------
# ✅ Generate FIX Config from .env
# -------------------------------
def generate_fix_cfg(output_path=CONFIG_FILE):
    print(f"⚙️  Generating FIX config at {output_path} from .env ...")

    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        print(f"❌ No .env file found at {env_path}")
        return

    # read only from .env file; ignore OS environment
    env = dotenv_values(env_path)

    cfg = f"""[DEFAULT]
ApplicationID={env.get('APPLICATION_ID')}
ConnectionType={env.get('CONNECTION_TYPE')}
ReconnectInterval={env.get('RECONNECT_INTERVAL')}
FileStorePath={env.get('FILE_STORE_PATH')}
FileLogPath={env.get('FILE_LOG_PATH')}
StartTime={env.get('START_TIME')}
EndTime={env.get('END_TIME')}
HeartBtInt={env.get('HEART_BT_INT')}
UseDataDictionary={env.get('USE_DATA_DICTIONARY')}
DataDictionary={env.get('DATA_DICTIONARY')}
Username={env.get('USERNAME')}
Password={env.get('PASSWORD')}
symbols={env.get('SYMBOLS')}

[SESSION]
ResetOnLogon={env.get('RESET_ON_LOGON')}
BeginString={env.get('BEGIN_STRING')}
SocketConnectPort={env.get('SOCKET_CONNECT_PORT')}
SocketConnectHost={env.get('SOCKET_CONNECT_HOST')}
SenderCompID={env.get('SENDER_COMP_ID')}
TargetCompID={env.get('TARGET_COMP_ID')}

[LOGGING]
LogFilePath={env.get('LOG_FILE_PATH')}
LogLevel={env.get('LOG_LEVEL')}
"""

    os.makedirs(SRC_DIR, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cfg)

    print(f"✅ FIX config written to {output_path}\n")

# -------------------------------
# 🐳 Docker Compose Utilities
# -------------------------------
def run_compose_up():
    print("🔄 Starting server with docker-compose...")
    result = subprocess.run(["docker-compose", "-f", DOCKER_COMPOSE_FILE, "up", "-d"])
    if result.returncode == 0:
        print("✅ Server started.")
    else:
        print("❌ Failed to start the server.")

def exec_into_container():
    print("🔍 Getting container ID for service:", SERVICE_NAME)
    try:
        result = subprocess.run(
            ["docker-compose", "-f", DOCKER_COMPOSE_FILE, "ps", "-q", SERVICE_NAME],
            capture_output=True,
            text=True,
            check=True
        )
        container_id = result.stdout.strip()
        if not container_id:
            print("⚠️ Could not find running container for service:", SERVICE_NAME)
            return

        print(f"🔗 Connecting to container {container_id} using bash (fallback to sh if needed)...")
        try:
            subprocess.run(["docker", "exec", "-it", container_id, "bash"])
        except Exception:
            print("⚠️ bash failed, trying sh...")
            subprocess.run(["docker", "exec", "-it", container_id, "sh"])

    except subprocess.CalledProcessError as e:
        print("❌ Error getting container ID:", e)

def stop_and_remove():
    print("🛑 Stopping and removing containers...")
    result = subprocess.run(["docker-compose", "-f", DOCKER_COMPOSE_FILE, "down"])
    if result.returncode == 0:
        print("✅ Containers stopped and removed.")
    else:
        print("❌ Failed to stop/remove containers.")

# -------------------------------
# 🧭 Menu UI
# -------------------------------
def show_menu():
    print("\n📦 Docker Compose Manager")
    print("1. Generate FIX Config from .env")
    print("2. Start server")
    print("3. Connect to container shell")
    print("4. Stop and remove server")
    print("5. Exit")

def main():
    while True:
        show_menu()
        choice = input("Choose an option (1–5): ").strip()
        if choice == "1":
            generate_fix_cfg()
        elif choice == "2":
            # Auto-generate config before starting
            print("🧩 Regenerating FIX config before launch...")
            generate_fix_cfg()
            run_compose_up()
        elif choice == "3":
            exec_into_container()
        elif choice == "4":
            stop_and_remove()
        elif choice == "5":
            print("👋 Exiting.")
            sys.exit(0)
        else:
            print("⚠️ Invalid choice. Please select 1–5.")

if __name__ == "__main__":
    main()

