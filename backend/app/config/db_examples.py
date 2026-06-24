DB_EXAMPLES = {
    'mysql': {
        'table_format': '使用下划线前缀表示分层（如 dim_order_info）',
        'example_full': '''CREATE TABLE dim_order_info (
    order_id BIGINT COMMENT '订单ID',
    order_name VARCHAR(128) COMMENT '订单名称',
    create_time DATETIME COMMENT '创建时间',
    update_time DATETIME COMMENT '更新时间'
) COMMENT='订单表';''',
        'example_abbr': '''CREATE TABLE dim_order_info (
    ord_id BIGINT COMMENT '订单ID',
    ord_nm VARCHAR(128) COMMENT '订单名称',
    crt_tm DATETIME COMMENT '创建时间',
    upd_tm DATETIME COMMENT '更新时间'
) COMMENT='订单表';''',
        'table_comment_syntax': '在 CREATE TABLE 末尾使用 COMMENT',
        'column_comment_syntax': '在字段定义后使用 COMMENT',
        'table_name_format': '{layer}_{theme}_{table}'
    },
    'postgresql': {
        'table_format': '使用 schema.table 格式表示分层（如 dim.order_info）',
        'example_full': '''CREATE TABLE dim.order_info (
    order_id BIGINT,
    order_name VARCHAR(128),
    create_time TIMESTAMP,
    update_time TIMESTAMP
);
COMMENT ON TABLE dim.order_info IS '订单表';
COMMENT ON COLUMN dim.order_info.order_id IS '订单ID';''',
        'example_abbr': '''CREATE TABLE dim.order_info (
    ord_id BIGINT,
    ord_nm VARCHAR(128),
    crt_tm TIMESTAMP,
    upd_tm TIMESTAMP
);
COMMENT ON TABLE dim.order_info IS '订单表';
COMMENT ON COLUMN dim.order_info.ord_id IS '订单ID';''',
        'table_comment_syntax': 'COMMENT ON TABLE schema.table IS',
        'column_comment_syntax': 'COMMENT ON COLUMN schema.table.column IS',
        'table_name_format': '{layer}.{theme}_{table}'
    },
    'oracle': {
        'table_format': '使用大写 SCHEMA.TABLE 格式表示分层（如 DIM.ORDER_INFO）',
        'example_full': '''CREATE TABLE DIM.ORDER_INFO (
    ORDER_ID NUMBER(19),
    ORDER_NAME VARCHAR2(128),
    CREATE_TIME DATE,
    UPDATE_TIME DATE
);
COMMENT ON TABLE DIM.ORDER_INFO IS '订单表';''',
        'example_abbr': '''CREATE TABLE DIM.ORDER_INFO (
    ORD_ID NUMBER(19),
    ORD_NM VARCHAR2(128),
    CRT_TM DATE,
    UPD_TM DATE
);
COMMENT ON TABLE DIM.ORDER_INFO IS '订单表';''',
        'table_comment_syntax': 'COMMENT ON TABLE SCHEMA.TABLE IS',
        'column_comment_syntax': 'COMMENT ON COLUMN SCHEMA.TABLE.COLUMN IS',
        'table_name_format': '{LAYER}.{THEME}_{TABLE}'
    }
}

def get_db_example(db_type: str, priority: str = 'full') -> dict:
    """获取数据库特定的示例配置"""
    config = DB_EXAMPLES.get(db_type.lower(), DB_EXAMPLES['mysql'])
    
    if priority == 'abbr':
        config['example'] = config.get('example_abbr', config.get('example', ''))
    else:
        config['example'] = config.get('example_full', config.get('example', ''))
    
    return config
