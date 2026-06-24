# 表名Schema重复问题修复计划

## 问题分析

### 现象

生成的DDL中表名出现schema重复：

* MySQL: `dim_dim_product_info` （dim重复）

* PostgreSQL: `"dim"."dim.product_info"` （dim在schema和表名中都出现）

### 根本原因

1. `translate_table_name()` 方法将"商品维度表"翻译成 `dim_product_info`（包含"dim"前缀）
2. `generate_ddl_for_table()` 第590行又加上layer前缀：`table_name_with_layer = f"{layer}_{english_table_name}"`
3. 如果layer是"dim"，最终表名就变成了 `dim_dim_product_info`

### 代码位置

* `translate_table_name()`: [backend/app/processors/field\_processor.py#L632](file:///d:/Data/Trae/数仓AI助手-Trae1.0/backend/app/processors/field_processor.py#L632)

* `generate_ddl_for_table()`: [backend/app/processors/field\_processor.py#L541](file:///d:/Data/Trae/数仓AI助手-Trae1.0/backend/app/processors/field_processor.py#L541)

## 修复方案

### 方案一：修改 `translate_table_name()`（推荐）

在表名翻译时，检测并移除表名中可能包含的layer关键字（如dim, dwd, dws, ods, ads）

### 方案二：修改 `generate_ddl_for_table()`

在组装表名时，检测表名是否已包含layer前缀，如果已包含则不再添加

## 实施步骤

### 步骤1：修改 `translate_table_name()` 方法

* 在翻译完成后，检查表名是否以layer关键字开头

* 如果是，则移除该前缀

### 步骤2：修改调用位置

* `generate_ddl_for_table()` 调用 `translate_table_name()` 时，需要传入layer参数

### 步骤3：测试验证

* 测试MySQL表名生成

* 测试PostgreSQL表名生成

* 测试Oracle表名生成

## 文件修改

### 需要修改的文件

1. `backend/app/processors/field_processor.py`

   * 修改 `translate_table_name()` 方法签名，添加layer参数

   * 在翻译逻辑中移除layer前缀

   * 修改调用处

## 风险评估

### 风险等级：低

* 修改只影响表名生成逻辑

* 不影响字段处理和其他核心功能

* 向后兼容，已有数据不受影响

### 风险点

* 如果表名本身就应该包含layer关键字（如"维度维度表"），可能会误删

* 解决方案：只移除表名开头的layer关键字，且只移除一次

## 测试用例

### 测试1：商品维度表（layer=dim）

* 期望结果：MySQL → `dim_product_info`，PostgreSQL → `dim.product_info`

* 实际结果（修复前）：MySQL → `dim_dim_product_info`，PostgreSQL → `dim.dim_product_info`

### 测试2：订单明细表（layer=dwd）

* 期望结果：MySQL → `dwd_order_detail`，PostgreSQL → `dwd.order_detail`

### 测试3：销售汇总表（layer=dws）

* 期望结果：MySQL → `dws_sales_summary`，PostgreSQL → `dws.sales_summary`

