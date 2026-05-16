import time


def test_ssh(env) -> dict:
    """Test SSH connectivity using paramiko."""
    try:
        import paramiko
    except ImportError:
        return {
            "success": False,
            "error": "paramiko 未安装。请运行: pip install paramiko",
            "connection_time": 0,
        }

    start = time.time()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        kwargs = {
            "hostname": env.ssh_host,
            "port": env.ssh_port or 22,
            "username": env.ssh_username,
            "timeout": 10,
        }

        if env.ssh_auth_method == "key":
            key_path = env.ssh_key_path
            passphrase = env.ssh_key_passphrase or None
            try:
                pkey = paramiko.RSAKey.from_private_key_file(key_path, password=passphrase)
            except paramiko.PasswordRequiredException:
                return {"success": False, "error": "私钥需要密码但未提供", "connection_time": 0}
            except FileNotFoundError:
                return {"success": False, "error": "密钥文件不存在: {}".format(key_path), "connection_time": 0}
            kwargs["pkey"] = pkey
        else:
            kwargs["password"] = env.ssh_password

        client.connect(**kwargs)
        elapsed = round(time.time() - start, 3)

        stdin, stdout, stderr = client.exec_command("echo ok", timeout=5)
        output = stdout.read().decode().strip()

        client.close()
        return {
            "success": output == "ok",
            "error": "",
            "connection_time": elapsed,
            "server_info": "{}@{}:{}".format(env.ssh_username, env.ssh_host, env.ssh_port or 22),
        }
    except Exception as ex:
        elapsed = round(time.time() - start, 3)
        try:
            client.close()
        except Exception:
            pass
        return {
            "success": False,
            "error": str(ex),
            "connection_time": elapsed,
        }
