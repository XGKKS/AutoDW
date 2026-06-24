import re
from typing import Dict, List, Tuple


DISALLOWED_SQL_PATTERN = re.compile(
    r"\b(DROP|DELETE|UPDATE|INSERT|TRUNCATE|ALTER|MERGE|GRANT|REVOKE|CREATE\s+USER)\b",
    re.IGNORECASE,
)


def split_sql_statements(sql: str) -> List[str]:
    statements = []
    current = []
    quote = None
    i = 0

    while i < len(sql):
        ch = sql[i]
        nxt = sql[i + 1] if i + 1 < len(sql) else ""

        if quote:
            current.append(ch)
            if ch == quote:
                if i + 1 < len(sql) and sql[i + 1] == quote:
                    current.append(sql[i + 1])
                    i += 1
                else:
                    quote = None
            i += 1
            continue

        if ch in ("'", '"', "`"):
            quote = ch
            current.append(ch)
            i += 1
            continue

        if ch == "-" and nxt == "-":
            while i < len(sql) and sql[i] not in ("\r", "\n"):
                current.append(sql[i])
                i += 1
            continue

        if ch == "/" and nxt == "*":
            current.append(ch)
            current.append(nxt)
            i += 2
            while i < len(sql):
                current.append(sql[i])
                if sql[i] == "*" and i + 1 < len(sql) and sql[i + 1] == "/":
                    current.append("/")
                    i += 2
                    break
                i += 1
            continue

        if ch == ";":
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
            i += 1
            continue

        current.append(ch)
        i += 1

    statement = "".join(current).strip()
    if statement:
        statements.append(statement)

    return statements


def _strip_sql_comments(statement: str) -> str:
    statement = re.sub(r"--.*?$", "", statement, flags=re.MULTILINE)
    statement = re.sub(r"/\*.*?\*/", "", statement, flags=re.DOTALL)
    return statement.strip()


def validate_ddl_statements(statements: List[str]) -> Tuple[bool, str]:
    if not statements:
        return False, "SQL内容为空"

    for index, statement in enumerate(statements, 1):
        cleaned = _strip_sql_comments(statement)
        if DISALLOWED_SQL_PATTERN.search(cleaned):
            return False, f"第 {index} 条SQL包含禁止执行的高风险语句"

        normalized = re.sub(r"\s+", " ", cleaned).strip().upper()
        allowed = (
            normalized.startswith("CREATE TABLE ")
            or normalized.startswith("COMMENT ON TABLE ")
            or normalized.startswith("COMMENT ON COLUMN ")
        )
        if not allowed:
            return False, f"第 {index} 条SQL不是允许的一键建表语句"

    return True, ""


def _require_connection_fields(connection: Dict) -> Tuple[bool, str]:
    missing = [
        field for field in ("host", "port", "database")
        if connection.get(field) in (None, "")
    ]
    if missing:
        return False, f"连接配置缺少字段: {', '.join(missing)}"
    return True, ""


def _connect(connection: Dict):
    ok, message = _require_connection_fields(connection)
    if not ok:
        raise RuntimeError(message)

    db_type = connection.get("db_type")
    host = connection.get("host")
    port = int(connection.get("port"))
    database = connection.get("database")
    username = connection.get("username", "")
    password = connection.get("password", "")

    if db_type == "mysql":
        try:
            import pymysql
        except ImportError as exc:
            raise RuntimeError("缺少MySQL驱动依赖，请安装 pymysql") from exc
        return pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database,
            charset="utf8mb4",
            autocommit=False,
        )

    if db_type == "postgresql":
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("缺少PostgreSQL驱动依赖，请安装 psycopg[binary]") from exc
        return psycopg.connect(
            host=host,
            port=port,
            dbname=database,
            user=username,
            password=password,
            autocommit=False,
        )

    if db_type == "oracle":
        try:
            import oracledb
        except ImportError as exc:
            raise RuntimeError("缺少Oracle驱动依赖，请安装 oracledb") from exc
        dsn = f"{host}:{port}/{database}"
        return oracledb.connect(user=username, password=password, dsn=dsn)

    raise RuntimeError(f"不支持的数据库类型: {db_type}")


def test_native_connection(connection: Dict) -> Dict:
    conn = None
    try:
        conn = _connect(connection)
        return {"success": True, "message": "数据库连接成功"}
    except Exception as exc:
        return {"success": False, "message": str(exc)}
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def execute_native_ddl(connection: Dict, ddl: str) -> Dict:
    statements = split_sql_statements(ddl)
    is_valid, message = validate_ddl_statements(statements)
    if not is_valid:
        return {
            "success": False,
            "executed_count": 0,
            "failed_index": 0,
            "message": message,
        }

    conn = None
    cursor = None
    executed_count = 0
    try:
        conn = _connect(connection)
        cursor = conn.cursor()

        for index, statement in enumerate(statements, 1):
            try:
                cursor.execute(statement)
                executed_count += 1
            except Exception as exc:
                try:
                    conn.rollback()
                except Exception:
                    pass
                return {
                    "success": False,
                    "executed_count": executed_count,
                    "failed_index": index,
                    "message": str(exc),
                }

        try:
            conn.commit()
        except Exception:
            pass

        return {
            "success": True,
            "executed_count": executed_count,
            "failed_index": None,
            "message": f"成功执行 {executed_count} 条建表SQL",
        }
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass
