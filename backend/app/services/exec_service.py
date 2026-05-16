import time
import threading
import uuid
from dataclasses import dataclass, field


@dataclass
class ExecutionTask:
    id: str
    command: str
    status: str = "pending"  # pending / running / success / failed
    output: str = ""
    exit_code: int | None = None
    started_at: str = ""
    finished_at: str = ""
    user_id: int = 0
    env_id: int = 0


# In-memory store (for MVP; replace with DB for production)
_tasks: dict[str, ExecutionTask] = {}
_lock = threading.Lock()


def submit_task(user_id: int, env_id: int, command: str) -> ExecutionTask:
    task_id = uuid.uuid4().hex[:12]
    task = ExecutionTask(id=task_id, command=command, user_id=user_id, env_id=env_id)
    with _lock:
        _tasks[task_id] = task
    return task


def run_task(task_id: str, env) -> None:
    """Execute command via SSH in a background thread."""
    import paramiko
    from datetime import datetime

    with _lock:
        task = _tasks.get(task_id)
        if not task:
            return
        task.status = "running"
        task.started_at = datetime.now().isoformat()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())

    try:
        kwargs = {
            "hostname": env.ssh_host,
            "port": env.ssh_port or 22,
            "username": env.ssh_username,
            "timeout": 30,
        }
        if env.ssh_auth_method == "key":
            passphrase = env.ssh_key_passphrase or None
            pkey = paramiko.RSAKey.from_private_key_file(env.ssh_key_path, password=passphrase)
            kwargs["pkey"] = pkey
        else:
            kwargs["password"] = env.ssh_password

        client.connect(**kwargs)

        stdin, stdout, stderr = client.exec_command(task.command, timeout=300)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        exit_code = stdout.channel.recv_exit_status()

        with _lock:
            task.output = out + ("\n--- STDERR ---\n" + err if err else "")
            task.exit_code = exit_code
            task.status = "success" if exit_code == 0 else "failed"
            task.finished_at = datetime.now().isoformat()

    except Exception as ex:
        with _lock:
            task.output = str(ex)
            task.exit_code = -1
            task.status = "failed"
            task.finished_at = datetime.now().isoformat()
    finally:
        try:
            client.close()
        except Exception:
            pass


def get_task(task_id: str) -> ExecutionTask | None:
    with _lock:
        return _tasks.get(task_id)


def list_tasks(user_id: int, limit: int = 50) -> list[ExecutionTask]:
    with _lock:
        user_tasks = [t for t in _tasks.values() if t.user_id == user_id]
        user_tasks.sort(key=lambda t: t.started_at, reverse=True)
        return user_tasks[:limit]
