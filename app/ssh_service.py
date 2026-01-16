import paramiko

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
    if not is_safe_command(command):
        return {
            "error": "Dangerous command blocked"
        }

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

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

    ssh.close()

    return {
        "output": output,
        "error": error
    }
