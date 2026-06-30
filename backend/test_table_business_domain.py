#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regression tests for table business-domain normalization.
"""

from app.processors.field_processor import FieldProcessor
from app.root_policy import (
    infer_theme_prefix,
    normalize_table_business_domain,
)
from app.validators.ddl_validator import DDLValidator


STANDARDS = """## 表命名规范
| 主题域 | 缩写 |
| 公共 | pub |
| 生产 | prod |
| 供应链 | scm |
| 营销 | mkt |
| 填报 | fill |
"""

EMPTY_STANDARDS = ""


class FixedTableNameProcessor(FieldProcessor):
    def __init__(self, fixed_name: str):
        super().__init__("", "", "", standards=STANDARDS)
        self.fixed_name = fixed_name

    def generate_table_name(self, chinese_table_name, db_type, standards_content="", layer="", theme_prefix=""):
        return self.fixed_name


class FixedFallbackTableNameProcessor(FixedTableNameProcessor):
    def translate_table_name(self, chinese_table_name, layer="", theme_prefix=""):
        return self.fixed_name


def test_unknown_theme_does_not_default_to_pub():
    assert infer_theme_prefix("未知业务表", standards_content=STANDARDS) == ""


def test_multiple_business_domains_are_collapsed():
    assert (
        normalize_table_business_domain(
            "dwd_pub_scm_prod_weld_plan_line",
            standards_content=STANDARDS,
            layer="dwd",
        )
        == "prod_weld_plan_line"
    )
    assert (
        normalize_table_business_domain(
            "dwd_pub_prod_weld_run",
            standards_content=STANDARDS,
            layer="dwd",
        )
        == "prod_weld_run"
    )
    assert (
        normalize_table_business_domain(
            "fill_pub_mth_plan_ctrl_tgt",
            theme_prefix="fill",
            standards_content=STANDARDS,
        )
        == "fill_mth_plan_ctrl_tgt"
    )


def test_validator_rejects_multiple_business_domain_prefixes():
    validator = DDLValidator([], standards={"content": STANDARDS}, root_match_priority="abbr")

    assert validator.validate_table_name("dwd_pub_scm_prod_weld_out")
    assert validator.validate_table_name("dwd_pub_prod_weld_run")
    assert not validator.validate_table_name("dwd_prod_weld_run")


def test_ddl_generation_normalizes_llm_table_name():
    processor = FixedTableNameProcessor("dwd_pub_scm_prod_weld_plan_line")
    table_info = {
        "layer": "dwd",
        "fields": [{"name": "焊装计划下线时间", "type": "DATETIME"}],
    }
    field_mapping = {"焊装计划下线时间": ("weld_plan_offl_time", "DATETIME")}

    ddl = processor.generate_ddl_for_table(
        "生产焊装计划表(下线)",
        table_info,
        field_mapping,
        db_type="mysql",
        standards_content=STANDARDS,
    )

    assert "CREATE TABLE `dwd_prod_weld_plan_line`" in ddl
    assert "dwd_pub_scm_prod_weld_plan_line" not in ddl


def test_ddl_generation_removes_pub_after_user_subject_domain():
    processor = FixedTableNameProcessor("fill_pub_mth_plan_ctrl_tgt")
    table_info = {
        "layer": "",
        "user_specified_subject_domain": "fill",
        "fields": [{"name": "计划月份", "type": "VARCHAR(16)"}],
    }
    field_mapping = {"计划月份": ("plan_mth", "VARCHAR(16)")}

    ddl = processor.generate_ddl_for_table(
        "月度计划与控制目标表",
        table_info,
        field_mapping,
        db_type="mysql",
        standards_content=STANDARDS,
    )

    assert "CREATE TABLE `fill_mth_plan_ctrl_tgt`" in ddl
    assert "fill_pub_mth_plan_ctrl_tgt" not in ddl


def test_mysql_layer_theme_removes_pub_from_table_body():
    processor = FixedTableNameProcessor("fill_pub_mth_plan_ctrl_tgt")
    table_info = {
        "layer": "fill",
        "fields": [{"name": "计划月份", "type": "VARCHAR(16)"}],
    }
    field_mapping = {"计划月份": ("plan_mth", "VARCHAR(16)")}

    ddl = processor.generate_ddl_for_table(
        "月度计划与控制目标表",
        table_info,
        field_mapping,
        db_type="mysql",
        standards_content=STANDARDS,
    )

    assert "CREATE TABLE `fill_mth_plan_ctrl_tgt`" in ddl
    assert "fill_pub_mth_plan_ctrl_tgt" not in ddl
    assert "fill_fill_mth_plan_ctrl_tgt" not in ddl


def test_postgresql_schema_layer_removes_pub_from_table_body():
    processor = FixedTableNameProcessor("fill_pub_mth_plan_ctrl_tgt")
    table_info = {
        "layer": "fill",
        "fields": [{"name": "计划月份", "type": "VARCHAR(16)"}],
    }
    field_mapping = {"计划月份": ("plan_mth", "VARCHAR(16)")}

    ddl = processor.generate_ddl_for_table(
        "月度计划与控制目标表",
        table_info,
        field_mapping,
        db_type="postgresql",
        standards_content=STANDARDS,
    )

    assert 'CREATE TABLE "fill"."mth_plan_ctrl_tgt"' in ddl
    assert 'COMMENT ON TABLE "fill"."mth_plan_ctrl_tgt"' in ddl
    assert '"fill"."pub_mth_plan_ctrl_tgt"' not in ddl


def test_postgresql_schema_layer_removes_pub_without_standards_mapping():
    processor = FixedFallbackTableNameProcessor("fill_pub_mth_plan_ctrl_tgt")
    processor.standards = EMPTY_STANDARDS
    table_info = {
        "layer": "fill",
        "fields": [{"name": "计划月份", "type": "VARCHAR(16)"}],
    }
    field_mapping = {"计划月份": ("plan_mth", "VARCHAR(16)")}

    ddl = processor.generate_ddl_for_table(
        "月度计划与控制目标表",
        table_info,
        field_mapping,
        db_type="postgresql",
        standards_content=EMPTY_STANDARDS,
    )

    assert 'CREATE TABLE "fill"."mth_plan_ctrl_tgt"' in ddl
    assert 'COMMENT ON TABLE "fill"."mth_plan_ctrl_tgt"' in ddl
    assert '"fill"."pub_mth_plan_ctrl_tgt"' not in ddl


def test_oracle_schema_layer_removes_pub_from_table_body():
    processor = FixedTableNameProcessor("fill_pub_mth_plan_ctrl_tgt")
    table_info = {
        "layer": "fill",
        "fields": [{"name": "计划月份", "type": "VARCHAR(16)"}],
    }
    field_mapping = {"计划月份": ("plan_mth", "VARCHAR(16)")}

    ddl = processor.generate_ddl_for_table(
        "月度计划与控制目标表",
        table_info,
        field_mapping,
        db_type="oracle",
        standards_content=STANDARDS,
    )

    assert 'CREATE TABLE "FILL"."MTH_PLAN_CTRL_TGT"' in ddl
    assert '"FILL"."PUB_MTH_PLAN_CTRL_TGT"' not in ddl
    assert '"FILL"."FILL_MTH_PLAN_CTRL_TGT"' not in ddl


if __name__ == "__main__":
    test_unknown_theme_does_not_default_to_pub()
    test_multiple_business_domains_are_collapsed()
    test_validator_rejects_multiple_business_domain_prefixes()
    test_ddl_generation_normalizes_llm_table_name()
    test_ddl_generation_removes_pub_after_user_subject_domain()
    test_mysql_layer_theme_removes_pub_from_table_body()
    test_postgresql_schema_layer_removes_pub_from_table_body()
    test_postgresql_schema_layer_removes_pub_without_standards_mapping()
    test_oracle_schema_layer_removes_pub_from_table_body()
    print("table business-domain tests passed")
