from app.processors.field_processor import FieldInfo, FieldProcessor
from app.root_policy import build_root_sets, validate_identifier_mode
from app.validators.ddl_validator import DDLValidator
from app.validators.unified_validator import UnifiedValidator


WORD_ROOTS = [
    {"chinese_name": "仓库", "full_root": "warehouse", "abbr_root": "wh", "recommended_type": "VARCHAR(64)"},
    {"chinese_name": "库位", "full_root": "location", "abbr_root": "loc", "recommended_type": "VARCHAR(64)"},
    {"chinese_name": "商品", "full_root": "product", "abbr_root": "prod", "recommended_type": "VARCHAR(64)"},
    {"chinese_name": "标识", "full_root": "id", "abbr_root": "id", "recommended_type": "VARCHAR(64)"},
    {"chinese_name": "ID", "full_root": "id", "abbr_root": "id", "recommended_type": "VARCHAR(64)"},
    {"chinese_name": "入库", "full_root": "inbound", "abbr_root": "inb", "recommended_type": "VARCHAR(64)"},
    {"chinese_name": "明细", "full_root": "detail", "abbr_root": "dtl", "recommended_type": "VARCHAR(64)"},
    {"chinese_name": "修改", "full_root": "modify", "abbr_root": "mod", "recommended_type": "DATETIME"},
    {"chinese_name": "更新", "full_root": "modify", "abbr_root": "mod", "recommended_type": "DATETIME"},
    {"chinese_name": "计划", "full_root": "plan", "abbr_root": "pln", "recommended_type": "VARCHAR(64)"},
    {"chinese_name": "时间", "full_root": "time", "abbr_root": "time", "recommended_type": "DATETIME"},
    {"chinese_name": "单价", "full_root": "unit_price", "abbr_root": "unit", "recommended_type": "DECIMAL(18,2)"},
]


def error_messages(violations):
    return [v["message"] for v in violations if v.get("level") == "error"]


def test_full_mode_rejects_known_abbr_roots():
    ddl = """CREATE TABLE `dwd_inbound_detail` (
    `wh_id` VARCHAR(64) COMMENT '仓库ID',
    `loc_id` VARCHAR(64) COMMENT '库位ID',
    `prod_id` VARCHAR(64) COMMENT '商品ID'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='入库明细表';"""

    violations = DDLValidator(WORD_ROOTS, root_match_priority="full").validate(ddl)
    messages = "\n".join(error_messages(violations))

    assert "缩写词根 'wh'" in messages
    assert "缩写词根 'loc'" in messages
    assert "缩写词根 'prod'" in messages
    assert "缩写词根 'id'" not in messages


def test_full_mode_allows_complete_words_from_phrase_roots():
    full_roots, abbr_roots, abbr_to_full = build_root_sets(WORD_ROOTS)

    assert validate_identifier_mode("unit", "full", full_roots, abbr_roots, abbr_to_full) == []
    assert validate_identifier_mode("labor_hour_unit_price", "full", full_roots, abbr_roots, abbr_to_full) == []


def test_abbr_mode_rejects_long_roots():
    ddl = """CREATE TABLE `dwd_inb_dtl` (
    `warehouse_id` VARCHAR(64) COMMENT '仓库ID'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='入库明细表';"""

    violations = DDLValidator(WORD_ROOTS, root_match_priority="abbr").validate(ddl)
    messages = "\n".join(error_messages(violations))

    assert "warehouse" in messages
    assert "超过 4 个字母" in messages


def test_abbr_mode_accepts_custom_max_len():
    ddl = """CREATE TABLE `dwd_inb_dtl` (
    `warehouse_id` VARCHAR(64) COMMENT '仓库ID'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='入库明细表';"""

    violations = DDLValidator(WORD_ROOTS, root_match_priority="abbr", abbr_max_len=10).validate(ddl)
    messages = "\n".join(error_messages(violations))

    assert "warehouse" not in messages


def test_field_processor_uses_custom_abbr_max_len():
    processor = FieldProcessor("", "", "", word_roots=WORD_ROOTS, root_match_priority="abbr", abbr_max_len=6)

    assert processor._abbr_from_english("customer") == "cstmr"
    assert processor._filter_translation_by_priority("仓库", "whouse") == "whouse"


def test_layer1_uses_selected_root_mode():
    full_processor = FieldProcessor("", "", "", word_roots=WORD_ROOTS, root_match_priority="full")
    abbr_processor = FieldProcessor("", "", "", word_roots=WORD_ROOTS, root_match_priority="abbr")

    fields = {
        "仓库ID": ["仓库", "ID"],
        "库位ID": ["库位", "ID"],
        "商品ID": ["商品", "ID"],
    }

    assert full_processor.process_layer1_fields(fields, full_processor.existing_root_map) == {
        "仓库ID": "warehouse_id",
        "库位ID": "location_id",
        "商品ID": "product_id",
    }
    assert abbr_processor.process_layer1_fields(fields, abbr_processor.existing_root_map) == {
        "仓库ID": "wh_id",
        "库位ID": "loc_id",
        "商品ID": "prod_id",
    }


def test_llm_translation_filter_obeys_mode():
    full_processor = FieldProcessor("", "", "", word_roots=WORD_ROOTS, root_match_priority="full")
    abbr_processor = FieldProcessor("", "", "", word_roots=WORD_ROOTS, root_match_priority="abbr")

    assert full_processor._filter_translation_by_priority("仓库", "wh") is None
    assert full_processor._filter_translation_by_priority("仓库", "warehouse") == "warehouse"
    assert abbr_processor._filter_translation_by_priority("仓库", "warehouse") is None
    assert abbr_processor._filter_translation_by_priority("仓库", "wh") == "wh"


def test_fix_prompt_contains_mode_constraints():
    validator = DDLValidator(WORD_ROOTS, root_match_priority="full")
    ddl = """CREATE TABLE `dwd_inbound_detail` (
    `wh_id` VARCHAR(64) COMMENT '仓库ID'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='入库明细表';"""
    violations = validator.validate(ddl)
    prompt = validator.generate_fix_prompt(ddl, violations)

    assert "当前为全称模式" in prompt
    assert "不得保留已经违反词根模式" in prompt


def test_table_fields_are_structured_errors_and_extractable():
    ddl = """CREATE TABLE `dim_base_product` (
    `table` VARCHAR(64) COMMENT '商品ID',
    `table` VARCHAR(64) COMMENT 'SKU编码',
    `table` DATETIME COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品维度表';"""
    validator = UnifiedValidator(WORD_ROOTS, root_match_priority="full")
    result = validator.validate_batch({"dim_base_product": ddl})
    assert result["error_count"] >= 3

    parsed = validator.parse_all_ddl({"dim_base_product": ddl})
    error_fields = validator.extract_error_fields(result["single_violations"], parsed)
    assert "dim_base_product" in error_fields
    assert len(error_fields["dim_base_product"]) == 3
    assert error_fields["dim_base_product"]["1"]["current_name"] == "table"
    assert error_fields["dim_base_product"]["2"]["field_index"] == 2


def test_reassemble_ddl_replaces_duplicate_fields_by_index():
    ddl = """CREATE TABLE `dim_base_product` (
    `table` VARCHAR(64) COMMENT '商品ID',
    `table` VARCHAR(64) COMMENT 'SKU编码',
    `table` DATETIME COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品维度表';"""
    validator = UnifiedValidator(WORD_ROOTS, root_match_priority="full")
    fixed = validator.reassemble_ddl(
        {"dim_base_product": ddl},
        {"dim_base_product": {1: "product_id", 2: "sku_code", 3: "create_time"}},
        validator.parse_all_ddl({"dim_base_product": ddl})
    )["dim_base_product"]
    assert "`product_id` VARCHAR(64)" in fixed
    assert "`sku_code` VARCHAR(64)" in fixed
    assert "`create_time` DATETIME" in fixed
    assert "`table`" not in fixed


def test_missing_field_mapping_uses_tokenized_roots_not_table_fallback():
    processor = FieldProcessor("", "", "", word_roots=WORD_ROOTS, root_match_priority="full")
    processor.field_tokenization = {
        "修改计划": ["修改", "计划"],
        "更新计划": ["更新", "计划"],
        "修改时间": ["修改", "时间"],
    }
    processor.root_translations = {
        "修改": "modify",
        "更新": "modify",
        "计划": "plan",
        "时间": "time",
    }
    ddl = processor.generate_ddl_for_table(
        "测试表",
        {"layer": "dwd", "fields": [
            {"name": "修改计划", "type": "VARCHAR(64)"},
            {"name": "更新计划", "type": "VARCHAR(64)"},
            {"name": "修改时间", "type": "DATETIME"},
        ]},
        {},
        db_type="mysql",
        standards_content=""
    )
    assert "`modify_plan` VARCHAR(64)" in ddl
    assert ddl.count("`modify_plan` VARCHAR(64)") == 2
    assert "`modify_time` DATETIME" in ddl
    assert "`table`" not in ddl


def test_missing_field_mapping_reuses_root_translations_for_new_roots():
    processor = FieldProcessor("", "", "", word_roots=WORD_ROOTS, root_match_priority="full")
    processor.field_tokenization = {
        "工时单价": ["工时", "单价"],
    }
    processor.root_translations = {
        "工时": "labor_hour",
    }
    ddl = processor.generate_ddl_for_table(
        "测试表",
        {"layer": "dwd", "fields": [
            {"name": "工时单价", "type": "DECIMAL(18,2)"},
        ]},
        {},
        db_type="mysql",
        standards_content=""
    )

    assert "`labor_hour_unit_price` DECIMAL(18,2)" in ddl


def test_abbr_mode_falls_back_when_abbr_roots_are_missing():
    word_roots = [
        {"chinese_name": "商品", "full_root": "product", "abbr_root": "prod", "recommended_type": "VARCHAR(64)"},
        {"chinese_name": "单价", "full_root": "unit_price", "abbr_root": "", "recommended_type": "DECIMAL(18,2)"},
        {"chinese_name": "品牌", "full_root": "brand", "abbr_root": "", "recommended_type": "VARCHAR(64)"},
        {"chinese_name": "名称", "full_root": "name", "abbr_root": "", "recommended_type": "VARCHAR(128)"},
    ]
    processor = FieldProcessor("", "", "", word_roots=word_roots, root_match_priority="abbr")
    processor.field_tokenization = {
        "商品单价": ["商品", "单价"],
        "品牌名称": ["品牌", "名称"],
    }

    ddl = processor.generate_ddl_for_table(
        "商品价格表",
        {"layer": "dwd", "fields": [
            {"name": "商品单价", "type": "DECIMAL(18,2)"},
            {"name": "品牌名称", "type": "VARCHAR(128)"},
        ]},
        {},
        db_type="mysql",
        standards_content=""
    )

    assert "-- 生成失败" not in ddl
    assert "COMMENT '商品单价'" in ddl
    assert "COMMENT '品牌名称'" in ddl
    field_names = [line.strip().split("`")[1] for line in ddl.splitlines() if line.strip().startswith("`")]
    assert field_names
    assert all(len(part) <= 4 for name in field_names for part in name.split("_"))


def test_full_mode_falls_back_when_roots_are_missing_and_reuses_tokens():
    processor = FieldProcessor("", "", "", word_roots=[], root_match_priority="full")
    processor.field_tokenization = {
        "商品单价": ["商品", "单价"],
        "商品成本": ["商品", "成本"],
    }

    ddl = processor.generate_ddl_for_table(
        "商品价格表",
        {"layer": "dwd", "fields": [
            {"name": "商品单价", "type": "DECIMAL(18,2)"},
            {"name": "商品成本", "type": "DECIMAL(18,2)"},
        ]},
        {},
        db_type="mysql",
        standards_content=""
    )

    assert "-- 生成失败" not in ddl
    assert "COMMENT '商品单价'" in ddl
    assert "COMMENT '商品成本'" in ddl
    first_field = [line for line in ddl.splitlines() if "商品单价" in line][0].split("`")[1]
    second_field = [line for line in ddl.splitlines() if "商品成本" in line][0].split("`")[1]
    assert first_field.split("_")[0] == second_field.split("_")[0]


def test_tokenization_discards_bracket_notes():
    processor = FieldProcessor("", "", "", word_roots=WORD_ROOTS, root_match_priority="full")
    field_name = "被分配人（分配给的人）"
    tokenization, unique_roots = processor.tokenize_all_fields_root_level({
        field_name: [FieldInfo("测试表", field_name, "VARCHAR(64)", field_index=1)]
    })

    tokens = tokenization[field_name]
    joined_tokens = "".join(tokens)
    assert "分配给的人" not in joined_tokens
    assert "给" not in tokens
    assert "的" not in tokens
    assert all("paren" not in token.lower() for token in tokens)
    assert unique_roots == tokens


def test_semantic_root_normalization_reuses_llm_synonym_map():
    processor = FieldProcessor("", "", "", word_roots=WORD_ROOTS, root_match_priority="full")

    def fake_tokenize(groups):
        return (
            {
                "预计开工时间": ["预计", "开工", "时间"],
                "预估开工时间": ["预估", "开工", "时间"],
            },
            ["预计", "开工", "时间", "预估"],
        )

    semantic_map = {
        "预计": "estimated",
        "预估": "estimated",
        "开工": "start",
    }
    processor.tokenize_all_fields_root_level = fake_tokenize
    processor.normalize_unmatched_roots_semantically = lambda roots: {
        root: semantic_map[root] for root in roots if root in semantic_map
    }
    processor._translate_roots_batch = lambda batch: {}

    field_mapping, _, _ = processor.process_fields_root_level({
        "预计开工时间": [FieldInfo("测试表", "预计开工时间", "DATETIME", field_index=1)],
        "预估开工时间": [FieldInfo("测试表", "预估开工时间", "DATETIME", field_index=2)],
    })

    assert processor.root_translations["预计"] == "estimated"
    assert processor.root_translations["预估"] == "estimated"
    assert field_mapping["预计开工时间"][0] == "estimated_start_time"
    assert field_mapping["预估开工时间"][0] == "estimated_start_time"


def test_field_generation_progress_is_reported_during_layer2():
    progress_events = []

    def capture_progress(task_id, current, total, **kwargs):
        progress_events.append(kwargs)

    processor = FieldProcessor(
        "",
        "",
        "",
        word_roots=WORD_ROOTS,
        root_match_priority="full",
        progress_callback=capture_progress,
        task_id="task_progress",
        max_workers=3
    )
    processor._translate_roots_batch = lambda batch: {root: f"new{idx}" for idx, root in enumerate(batch, start=1)}

    groups = {
        "新增计划": [FieldInfo("测试表", "新增计划", "VARCHAR(64)", field_index=1)]
    }
    processor.process_fields_root_level(groups)

    field_progress_events = [event.get("field_progress") for event in progress_events if event.get("field_progress")]
    assert any(event["phase"] == "history_matched" for event in field_progress_events)
    assert any(event["phase"] == "layer2_generating" for event in field_progress_events)
    layer2_events = [event for event in field_progress_events if event["phase"] == "layer2_generating"]
    assert layer2_events[-1]["completed_batches"] == layer2_events[-1]["batch_count"]
    assert layer2_events[-1]["thread_count"] >= 1


if __name__ == "__main__":
    test_full_mode_rejects_known_abbr_roots()
    test_full_mode_allows_complete_words_from_phrase_roots()
    test_abbr_mode_rejects_long_roots()
    test_layer1_uses_selected_root_mode()
    test_llm_translation_filter_obeys_mode()
    test_fix_prompt_contains_mode_constraints()
    test_table_fields_are_structured_errors_and_extractable()
    test_reassemble_ddl_replaces_duplicate_fields_by_index()
    test_missing_field_mapping_uses_tokenized_roots_not_table_fallback()
    test_missing_field_mapping_reuses_root_translations_for_new_roots()
    test_tokenization_discards_bracket_notes()
    test_semantic_root_normalization_reuses_llm_synonym_map()
    test_field_generation_progress_is_reported_during_layer2()
    print("root priority policy tests passed")
