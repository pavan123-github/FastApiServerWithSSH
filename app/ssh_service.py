import paramiko
import socket

BLOCKED_COMMANDS = [
    "rm -rf",
    "shutdown",
    "reboot",
    "mkfs",
    ":(){"
]

def is_safe_command(command: str):
    for bad in BLOCKED_COMMANDS:
        if bad in command:
            return False
    return True

def execute_ssh_command(host, username, port, password, command):
    # 🔒 Dangerous command check
    if not is_safe_command(command):
        return {
            "status": "blocked",
            "error": "Dangerous command blocked"
        }

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(
            hostname=host,
            username=username,
            password=password,
            port=port,
            timeout=10
        )

        stdin, stdout, stderr = ssh.exec_command(command)

        output = stdout.read().decode()
        error = stderr.read().decode()

        return {
            "status": "success" if not error else "failed",
            "output": output,
            "error": error
        }

    except socket.timeout:
        return {
            "status": "failed",
            "error": "Connection timed out"
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }

    finally:
        ssh.close()