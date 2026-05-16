import time

ORA_ERRORS = {
    "ORA-12154": "TNS 配置错误，请检查 service_name 或 SID",
    "ORA-01017": "用户名或密码错误",
    "ORA-12541": "无监听程序，请确认数据库监听已启动",
    "ORA-12514": "服务名不存在，请检查 service_name",
    "ORA-12505": "SID 不存在，请检查 SID 配置",
    "ORA-28000": "账户已被锁定",
    "ORA-28001": "密码已过期",
}


def test_oracle(host: str, port: int, service_name: str, sid: str,
                connect_type: str, username: str, password: str) -> dict:
    try:
        import oracledb
    except ImportError:
        return {"success": False, "error": "oracledb 未安装。请运行: pip install oracledb",
                "response_time": 0, "instance_name": "", "status": "", "version": ""}

    start = time.time()
    try:
        if connect_type == "sid":
            dsn = oracledb.makedsn(host, port, sid=sid or "orcl")
        else:
            dsn = oracledb.makedsn(host, port, service=service_name or "orcl")

        conn = oracledb.connect(user=username, password=password, dsn=dsn)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT INSTANCE_NAME, STATUS, VERSION_FULL FROM V$INSTANCE")
            row = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
        elapsed = round(time.time() - start, 3)

        return {
            "success": True, "error": "", "response_time": elapsed,
            "instance_name": row[0] if row else "",
            "status": row[1] if row else "",
            "version": row[2] if row else "",
        }
    except Exception as ex:
        elapsed = round(time.time() - start, 3)
        err = str(ex)
        for code, msg in ORA_ERRORS.items():
            if code in err:
                err = "{}: {}".format(code, msg)
                break
        else:
            low = err.lower()
            if "timed out" in low or "timeout" in low:
                err = "连接超时，请检查主机地址和端口是否可达"
        return {"success": False, "error": err, "response_time": elapsed,
                "instance_name": "", "status": "", "version": ""}
