---
title: Elastic Agent Metrics ILM 升級後遭預設策略覆蓋案例
tags:
  - elk
  - elasticsearch
  - fleet
  - ilm
  - case-study
source: self
status: active
created: 2026-08-13
updated: 2026-08-13
publish: true
---

# Elastic Agent Metrics ILM 升級後遭預設策略覆蓋案例

## 案例摘要

Elastic Stack 升級至 9.3.x 後，原本使用自訂 ILM policy `metrics-system` 的部分 Elastic Agent metrics data streams，後續建立的 backing indices 改為使用系統預設且已標示 Deprecated 的 `metrics` policy。

依 Elastic Support 說明及現場驗證結果，Fleet 管理的 index template 與 `@package` component template 會在 Integration 或 Elastic Stack 升級時更新。若自訂 ILM 沒有放在官方保留的 `@custom` component template，設定可能在升級後恢復為預設值。

第一階段先建立／調整全域 `metrics@custom` component template，將 `index.lifecycle.name` 指定為 `metrics-system`。驗證後，112 個 metrics index templates 已連結自訂 policy。

後續依客戶需求進一步縮小套用範圍：只讓 `metrics-system.*` data streams 使用 `metrics-system` policy。因此最終做法是移除 `metrics@custom` 中的全域 ILM 設定，改在各 System metrics dataset 專屬的 `metrics-system.<dataset>@custom` component template 中指定 policy。

## 背景

- 資料來源：Fleet 管理的 Elastic Agent。
- 資料類型：`metrics-*` data streams。
- 自訂 ILM policy：`metrics-system`。
- 問題發生時間：Elastic Stack 升級至 9.3.x 後。
- 影響：部分 metrics backing indices 改為使用系統預設 `metrics` policy。

Elastic Stack 9.3 起，舊的 `logs`、`metrics`、`synthetics` managed ILM policies 被對應的 `{type}@lifecycle` policies 取代，例如 `metrics@lifecycle`。不過，本案例的主要原因不是 policy 本身失效，而是自訂 ILM 未透過可持續保留的 `@custom` 擴充點套用。

## 問題現象

升級後觀察到：

- 自訂 `metrics-system` policy 原先未連結 index templates。
- 部分新建立的 metrics backing indices 使用系統預設 `metrics` policy。
- `metrics` policy 雖已標示 Deprecated，仍有既有 indices 與其連結。
- Fleet-managed index templates 會隨 Integration 或 Stack 升級更新。

## 原因判定

Elastic Support 說明：

- `@package` component templates 屬於 Fleet-managed assets。
- Fleet 或 Integration 升級、重新安裝時，managed assets 可能被覆寫，以套用新版設定與修正。
- 自訂 ILM 若直接寫入 managed index template 或 `@package` component template，升級後可能恢復為系統預設值。
- 官方支援的做法是將自訂設定寫入 `@custom` component template。

因此，本案例依原廠說明及修正後結果判定：自訂 ILM 原先沒有透過正確的 `@custom` 擴充點持續套用，導致升級後 managed template 恢復預設 ILM。

## 第一階段：全域修正與驗證

### 1. 確認自訂 ILM policy

```http
GET _ilm/policy/metrics-system
```

確認 `metrics-system` policy 存在且內容符合預期。

### 2. 建立或調整 `metrics@custom`

第一階段為快速恢復所有 Fleet metrics data streams 的自訂 ILM，因此採用全域 `metrics@custom`：

```http
PUT _component_template/metrics@custom
{
  "template": {
    "settings": {
      "index": {
        "lifecycle": {
          "name": "metrics-system"
        }
      }
    }
  }
}
```

注意：如果 `metrics@custom` 原本已存在，必須保留其中其他 settings、mappings 與 aliases，再加入 ILM 設定，不能直接用精簡內容覆蓋。

### 3. 確認 Component Template 合併關係

以 `metrics-system.cpu` index template 為例，其 component templates 包含：

```text
metrics@tsdb-settings
metrics-system.cpu@package
metrics@custom
system@custom
metrics-system.cpu@custom
ecs@mappings
.fleet_globals-1
.fleet_agent_id_verification-1
```

`metrics@custom` 排在 `metrics-system.cpu@package` 後面，因此會覆蓋 `@package` 中相同的 `index.lifecycle.name`。

`system@custom` 與 `metrics-system.cpu@custom` 查詢結果為 404。這是正常情況：它們是 Fleet 預留的可選自訂插槽，不存在時不會套用，也不會覆蓋 `metrics@custom`。

### 4. 模擬最終 Index Template

使用實際 data stream 名稱模擬最終合併結果：

```http
POST _index_template/_simulate_index/metrics-system.cpu-default
  ?filter_path=template.settings
```

確認結果包含：

```json
"index.lifecycle.name": "metrics-system"
```

此 API 只進行模擬，不會建立 index 或修改叢集。

### 5. 第一階段驗證結果

調整後 Kibana 顯示：

| ILM policy | Linked index templates | Linked indices |
|---|---:|---:|
| `metrics-system` | 112 | 708 |
| `metrics` | 0 | 70 |

此結果是全域 `metrics@custom` 生效後的階段性紀錄，代表：

- 112 個 metrics index templates 的最終 ILM 已改由 `metrics-system` 提供。
- 後續新建立的 metrics backing indices 將使用 `metrics-system`。
- 目前有 708 個 indices 顯示連結至 `metrics-system`，並由該 policy 管理。
- 仍連結 `metrics` 的 70 個 indices 是舊設定期間建立的既有 indices。

## 第二階段：依客戶需求縮小至 System Metrics

客戶最終需求不是讓所有 Fleet metrics 共用 `metrics-system`，而是只套用到 `metrics-system.*` data streams，例如 CPU、memory、filesystem 與 network。因此不再使用 `metrics@custom` 提供全域 ILM，而改用各 dataset 專屬的 `@custom` component template。

### 1. 盤點實際使用的 System metrics data streams

```http
GET _data_stream/metrics-system.*
```

並確認對應的 managed index templates 及其 `composed_of` 內容：

```http
GET _index_template/metrics-system.*
  ?filter_path=index_templates.name,index_templates.index_template.composed_of
```

畫面中下列 `@package` component templates 可用來辨識 System metrics datasets，但它們是 Fleet-managed assets，只能查看，不能直接修改：

```text
metrics-system.core@package
metrics-system.cpu@package
metrics-system.diskio@package
metrics-system.filesystem@package
metrics-system.fsstat@package
metrics-system.load@package
metrics-system.memory@package
metrics-system.network@package
metrics-system.ntp@package
metrics-system.process.summary@package
metrics-system.process@package
metrics-system.socket_summary@package
metrics-system.uptime@package
```

只需處理目前實際有 data stream、且對應 index template 的 `composed_of` 已預留 `<dataset>@custom` 的項目。

### 2. 移除 `metrics@custom` 的全域 ILM 設定

先確認既有內容：

```http
GET _component_template/metrics@custom
```

- 如果只有 `index.lifecycle.name`，可刪除整個 `metrics@custom`。
- 如果還包含其他自訂 settings、mappings 或 aliases，只移除 ILM 設定並保留其他內容。

```http
DELETE _component_template/metrics@custom
```

`metrics@custom` 是 managed index templates 預留的可選擴充點；不存在時不會造成 index template 失效。使用 `PUT _component_template` 更新時會覆蓋該 component template 的完整內容，因此修改前必須先備份並保留其他自訂設定。

### 3. 建立 dataset 專屬的 `@custom`

以 CPU dataset 為例：

```http
PUT _component_template/metrics-system.cpu@custom
{
  "template": {
    "settings": {
      "index": {
        "lifecycle": {
          "name": "metrics-system"
        }
      }
    }
  }
}
```

其他有使用的 datasets 依相同方式建立，例如：

```text
metrics-system.core@custom
metrics-system.diskio@custom
metrics-system.filesystem@custom
metrics-system.fsstat@custom
metrics-system.load@custom
metrics-system.memory@custom
metrics-system.network@custom
metrics-system.ntp@custom
metrics-system.process.summary@custom
metrics-system.process@custom
metrics-system.socket_summary@custom
metrics-system.uptime@custom
```

不需要複製 `@package` 的 mappings 或 settings。component template 不會依名稱或 wildcard 自動套用；只有被 managed index template 的 `composed_of` 明確引用且名稱完全相符的 `@custom` 才會生效。因此，單獨建立 `metrics-system@custom` 不會涵蓋所有 System metrics datasets。

### 4. 模擬 System 與非 System data streams

確認 System CPU 使用自訂 policy：

```http
POST _index_template/_simulate_index/metrics-system.cpu-default
  ?filter_path=template.settings.index.lifecycle.name
```

預期結果為：

```json
{
  "template": {
    "settings": {
      "index.lifecycle.name": "metrics-system"
    }
  }
}
```

另外選擇一個非 `metrics-system.*` 的實際 data stream 執行相同模擬，確認它不再取得 `metrics-system`，而是回到該 managed template 原本指定的預設 policy。

### 5. 套用到新的 backing index

template 變更只會套用到新建立的 backing indices。可等待自然 rollover，或先針對單一低風險 data stream 驗證：

```http
POST /metrics-system.cpu-default/_rollover
```

rollover 後再確認新 backing index：

```http
GET /.ds-metrics-system.cpu-default-*/_ilm/explain
```

預期新的 backing index 使用 `metrics-system`。完成單一 dataset 驗證後，再依需求逐一處理其他 System metrics data streams。

## 既有 `metrics` Indices 的後續行為

Component template 的修改不會回溯套用到既有 backing indices，因此：

1. 原本掛在 `metrics` policy 的既有 indices，會繼續依該 policy 執行目前及後續 ILM phases。
2. 第一階段因全域 `metrics@custom` 而取得 `metrics-system` 的非 System backing indices，不會因移除全域設定而自動切回預設 policy。
3. `metrics-system.*` data streams rollover 後的新 backing indices，會由各自的 `metrics-system.<dataset>@custom` 取得 `metrics-system`。
4. 非 `metrics-system.*` data streams rollover 後的新 backing indices，會回到各自 managed template 所指定的預設 policy。
5. Kibana 的 Linked indices 數量包含歷史 backing indices，不會在 component template 修改後立即反映成最終目標數量。

若沒有資料保存期限或法遵風險，可等待自然 rollover，不需強制處理。若希望新資料立即使用 `metrics-system`，可針對單一 data stream 執行：

```http
POST /metrics-system.cpu-default/_rollover
```

不建議直接批次切換既有 backing indices 的 ILM policy，因為 indices 可能已進入特定 phase 並快取 phase definition，需另行評估 policy 差異與切換風險。

在仍有 Linked indices 的情況下，不應刪除系統 `metrics` policy。

## 預防措施

- 不修改帶有 `Managed` 標記的 index template。
- 不修改 `@package` component template。
- 所有自訂 ILM、index settings 或 mappings 應放在對應的 `@custom` component template。
- 全部 Fleet metrics 共用設定才使用 `metrics@custom`。
- 只針對特定 dataset 時，使用例如 `metrics-system.cpu@custom`，並逐一確認 managed index template 已引用該名稱。
- 不建立未被 `composed_of` 引用的自訂 component template；名稱相似不代表會自動套用。
- 每次 Stack 或 Integration 升級後，至少執行一次 `_simulate_index` 驗證最終 ILM。
- 正式環境需要手動 rollover 時，先選單一非關鍵 data stream 驗證，再逐一執行，避免短時間增加大量 shards。

## 官方參考資料

- [Safely Updating ILM Policies for Fleet-Managed Indices](https://support.elastic.co/knowledge/04335774)
- [Elastic Agent data streams for Fleet](https://www.elastic.co/docs/reference/fleet/data-streams)
- [Apply an ILM policy to all Fleet metrics data streams](https://www.elastic.co/docs/reference/fleet/data-streams-scenario1)
- [Apply an ILM policy to specific Fleet data streams](https://www.elastic.co/docs/reference/fleet/data-streams-scenario2)
- [Customize built-in ILM policies](https://www.elastic.co/docs/manage-data/lifecycle/index-lifecycle-management/tutorial-customize-built-in-policies)
- [Simulate an index template](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-indices-simulate-index-template)
