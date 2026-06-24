import sys
sys.path.insert(0, '.')

from app.config.db_examples import get_db_example

def format_word_roots_for_prompt(word_roots, priority):
    return "标识/编号:id:BIGINT / VARCHAR\n代码/编码:code:VARCHAR\n名称/名字:name:VARCHAR"

description = """创建一个生产运营制度执行工单表，包含字段：
工单唯一标识（主键，字符串型）
所属系统类型（字符串型，如工艺决策系统/SCADA）
制度任务名称（字符串型）
任务等级（字符串型，如厂级/作业区级/站点级）
发布部门（字符串型）
责任执行部门（字符串型）
责任人（字符串型）
任务发布时间（日期时间型）
要求完成时间（日期时间型）
实际完成时间（日期时间型）
任务状态（字符串型，如待执行/已完成/逾期/申诉中）
执行完成率（数值型，保留2位小数）
逾期等级（字符串型，如1小时内/1-12小时/12小时以上）
审核状态（字符串型，如待审核/已通过/已驳回）
审核人（字符串型）
审核时间（日期时间型）
抽查状态（字符串型，如未抽查/已抽查/抽查不合格）
申诉原因大类（字符串型，如天气原因/设备故障/其他）
申诉详情（长文本型）
数据创建时间（日期时间型，默认当前时间）
数据更新时间（日期时间型，默认当前时间，自动更新）"""

db_type = "mysql"
root_match_priority = "full"
word_roots = []
standards_content = "表名格式：{分层}_{业务}_{描述}\n主键命名：pk_xxx"

db_type_name = {'mysql': 'MySQL', 'postgresql': 'PostgreSQL', 'oracle': 'Oracle'}.get(db_type, db_type)
root_match_name = {'full': '全称', 'abbr': '缩写'}.get(root_match_priority, root_match_priority)

db_example_config = get_db_example(db_type)
db_example = f"表名格式: {db_example_config['table_format']}\n\n示例DDL:\n{db_example_config['example']}"

prompt = f"""你是一位数据仓库专家。请根据以下参考信息生成 DDL：

【建表需求】
{description}

【词根参考】
{format_word_roots_for_prompt(word_roots, root_match_priority)}

【数据库类型】
{db_type_name}
{db_example}

【开发规范】
{standards_content}

要求：
1. 严格按照建表需求创建表，确保所有字段都被正确创建。
2. 字段命名优先参考{root_match_name}词根。
3. 严格遵循开发规范（表名，字段名，主键等）。
4. 只输出 CREATE TABLE 和 COMMENT 语句，不要解释和思考过程。
5. 严格按照【数据库类型】中的格式生成DDL，包括表名格式和注释语法。
6. 表名分层前缀与 schema 映射：ods -> ods, dim -> dim, dwd -> dwd, dws -> dws, ads -> ads, input -> input
7. 【词根复用原则】优先使用已保存词根中已有的英文词根或缩写。严禁对同一中文含义创造多个不同的英文词根。
8. 【新词根扩展】如果已保存的词根中检索不到要建表的字段，请使用通用的英文单词作为新词根，并在 SQL 输出结束后，单独一行按以下格式标记：【新词根】词根全称(例如：create_time):词根缩写(例如：crt_tm):中文名称:推荐字段类型"""

print("=== 生成的提示词 ===")
print(prompt)
print("\n=== 提示词长度 ===")
print(f"总长度: {len(prompt)} 字符")
print(f"建表需求部分长度: {len(description)} 字符")