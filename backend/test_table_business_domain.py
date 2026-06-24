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
"""


class FixedTableNameProcessor(FieldProcessor):
    def __init__(self, fixed_name: str):
        super().__init__("", "", "", standards=STANDARDS)
        self.fixed_name = fixed_name

    def generate_table_name(self, chinese_table_name, db_type, standards_content="", layer=""):
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


if __name__ == "__main__":
    test_unknown_theme_does_not_default_to_pub()
    test_multiple_business_domains_are_collapsed()
    test_validator_rejects_multiple_business_domain_prefixes()
    test_ddl_generation_normalizes_llm_table_name()
    print("table business-domain tests passed")
