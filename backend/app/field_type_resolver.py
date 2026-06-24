import re
from typing import Any, Dict


TYPE_COLUMN_ALIASES = (
    "推荐字段类型",
    "推荐类型",
    "字段类型",
    "recommended_type",
)

DEFAULT_TEXT_TYPE = "VARCHAR(255)"


def normalize_field_type(raw_type: Any) -> str:
    """Normalize a field type from Excel while preserving explicit precision."""
    if raw_type is None:
        return ""

    field_type = str(raw_type).strip()
    if not field_type:
        return ""

    field_type = (
        field_type.replace("（", "(")
        .replace("）", ")")
        .replace("，", ",")
        .replace("；", ";")
    )
    field_type = re.sub(r"\s+", "", field_type)
    field_type = field_type.rstrip(";")

    match = re.match(r"^([a-zA-Z][a-zA-Z0-9_]*)(\(.*\))?$", field_type)
    if not match:
        return field_type.upper()

    base_type = match.group(1).upper()
    params = match.group(2) or ""

    aliases = {
        "VARCHAR2": "VARCHAR",
        "CHARACTER": "VARCHAR",
        "STRING": "VARCHAR",
        "INTEGER": "INT",
        "NUMBER": "DECIMAL" if params and "," in params else "INT",
        "NUMERIC": "DECIMAL",
        "DOUBLE": "DECIMAL",
        "FLOAT": "DECIMAL",
        "BOOL": "TINYINT",
        "BOOLEAN": "TINYINT",
        "TIMESTAMP": "DATETIME",
    }
    base_type = aliases.get(base_type, base_type)
    return f"{base_type}{params}"


def get_excel_field_type(row_data: Dict[str, Any]) -> str:
    for column_name in TYPE_COLUMN_ALIASES:
        if column_name in row_data:
            normalized = normalize_field_type(row_data.get(column_name))
            if normalized:
                return normalized
    return ""


def recommend_field_type(field_name: Any) -> str:
    name = str(field_name or "").strip().lower()
    if not name:
        return DEFAULT_TEXT_TYPE

    compact_name = re.sub(r"\s+", "", name)

    if _contains_any(compact_name, (
        "创建人", "更新人", "修改人", "操作员", "处理人", "审核人", "上报人",
        "申请人", "负责人", "经办人", "联系人", "人员", "员工", "用户",
        "createdby", "updatedby", "modifiedby", "creator", "updater",
        "modifier", "operator", "handler", "reviewer", "auditor", "reporter",
        "owner", "user", "staff", "employee", "person",
    )):
        if _contains_any(compact_name, ("id", "编号", "编码", "代码", "code", "no")):
            return "VARCHAR(64)"
        return "VARCHAR(128)"

    if _contains_any(compact_name, (
        "时间", "日期", "年月日", "创建", "更新", "修改", "开始", "结束",
        "完成", "下单", "支付时间", "生效", "失效", "过期", "到期",
        "time", "date", "datetime", "timestamp", "created", "updated",
        "modified", "start", "end", "expire",
    )):
        return "DATETIME"

    if _contains_any(compact_name, (
        "金额", "价格", "单价", "成本", "费用", "余额", "收入", "支出",
        "税", "率", "比例", "占比", "折扣", "面积", "重量", "长度",
        "宽度", "高度", "体积", "均价", "客单价", "amount", "amt",
        "price", "cost", "fee", "balance", "rate", "ratio", "percent",
        "area", "weight", "length", "volume",
    )):
        return "DECIMAL(18,6)"

    if _contains_any(compact_name, (
        "数量", "次数", "人数", "件数", "天数", "月数", "年数", "库存",
        "余量", "总数", "序号", "排序", "等级", "状态码", "年龄",
        "count", "num", "qty", "quantity", "stock", "total", "sort",
        "rank", "level", "age",
    )):
        return "INT"

    if _contains_any(compact_name, ("描述", "备注", "说明", "内容", "地址", "desc", "remark", "memo", "content", "address")):
        return "VARCHAR(512)"

    if _contains_any(compact_name, ("名称", "姓名", "标题", "name", "title")):
        return "VARCHAR(128)"

    if _contains_any(compact_name, ("id", "编码", "编号", "代码", "单号", "账号", "手机号", "电话", "邮箱", "code", "no", "phone", "email")):
        return "VARCHAR(64)"

    return DEFAULT_TEXT_TYPE


def resolve_field_type(field_name: Any, raw_type: Any = None) -> str:
    normalized = normalize_field_type(raw_type)
    if normalized:
        return normalized
    return recommend_field_type(field_name)


def _contains_any(value: str, keywords) -> bool:
    return any(keyword in value for keyword in keywords)
