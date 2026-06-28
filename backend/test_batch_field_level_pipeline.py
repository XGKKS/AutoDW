from unittest.mock import patch

from app import main


class FakeFieldProcessor:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    def build_field_mapping(self, file_content=None, tables_data=None):
        assert file_content is None
        assert tables_data == {
            "test_table": {
                "layer": "dim",
                "fields": [{"name": "test_field", "type": "VARCHAR(255)"}],
            }
        }
        field_mapping = {"test_field": ("work_area", "VARCHAR(255)")}
        field_stats = {"matched_count": 1, "unmatched_count": 0, "total_fields": 1}
        root_translations = {"test_field": "work_area"}
        return tables_data, field_mapping, field_stats, root_translations

    def generate_all_ddl(self, tables_data, field_mapping, db_type, root_match_priority, standards_content):
        return {
            "test_table": "CREATE TABLE `dim_plan` (\n    `work_area` VARCHAR(255) COMMENT 'test_field'\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='test_table';"
        }


class FailingFieldProcessor:
    def __init__(self, *args, **kwargs):
        pass

    def build_field_mapping(self, file_content=None, tables_data=None):
        raise RuntimeError("mock field-level failure")


def _reset_state(task_id):
    main.task_results.pop(task_id, None)
    main.batch_cache.pop(task_id, None)
    main.progress_store.pop(task_id, None)
    main.task_cancel_flags.pop(task_id, None)
    main.task_validation_flags.pop(task_id, None)


def test_process_batch_task_uses_field_level_pipeline_without_table_fallback():
    task_id = "field_level_success"
    _reset_state(task_id)

    tables = {
        "test_table": {
            "layer": "dim",
            "fields": [{"name": "test_field", "type": "VARCHAR(255)"}],
        }
    }

    with patch("app.main.parse_batch_table_excel", return_value=tables),          patch("app.main.filter_and_prepare_roots", return_value=([], "")),          patch("app.main.generate_table_semantic_description", return_value=""),          patch("app.main.load_word_roots", return_value=[]),          patch("app.main.load_standards", return_value={"content": ""}),          patch("app.processors.field_processor.FieldProcessor", FakeFieldProcessor),          patch("app.main.process_single_table_for_batch", side_effect=AssertionError("table fallback should not run")):
        main.process_batch_task(
            task_id,
            b"excel-bytes",
            "key",
            "https://example.com",
            "test-model",
            "mysql",
            "full",
            enable_validation=False,
        )

    result = main.task_results[task_id]
    assert result["code"] == 0
    assert "work_area" in result["data"]["full_ddl"]


def test_process_batch_task_fails_fast_when_field_level_pipeline_errors():
    task_id = "field_level_failure"
    _reset_state(task_id)

    tables = {
        "test_table": {
            "layer": "dim",
            "fields": [{"name": "test_field", "type": "VARCHAR(255)"}],
        }
    }

    with patch("app.main.parse_batch_table_excel", return_value=tables),          patch("app.main.filter_and_prepare_roots", return_value=([], "")),          patch("app.main.generate_table_semantic_description", return_value=""),          patch("app.main.load_word_roots", return_value=[]),          patch("app.main.load_standards", return_value={"content": ""}),          patch("app.processors.field_processor.FieldProcessor", FailingFieldProcessor),          patch("app.main.process_single_table_for_batch", side_effect=AssertionError("table fallback should not run")):
        main.process_batch_task(
            task_id,
            b"excel-bytes",
            "key",
            "https://example.com",
            "test-model",
            "mysql",
            "full",
            enable_validation=False,
        )

    result = main.task_results[task_id]
    assert result["code"] == 1
    assert "字段级主流程失败" in result["message"]
