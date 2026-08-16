# Revision Round R{n} 报告

日期：YYYY-MM-DD ｜ 论文：<标题> ｜ 上一轮：R{n-1} ｜ 状态：进行中/已完成 ｜ 本轮成本/耗时（可选）：<API 花费 / 时长>（OpenMontage checkpoint 纪律：每轮留成本快照，长任务预算可对账）

## 1. 本轮范围

- 目标：
- 主要改动方向：
- 阻塞项：

## 2. 变更日志（相对 R{n-1}）

| 变更 ID | 文件 | 改了什么 | 为什么改 | 证据影响 | 状态 |
|---|---|---|---|---|---|
| CHG01 | paper/main.tex §3.2 | 例：更新 30 种子统计 | 数字重算不一致 | results/e1.json 重算值已同步 | done |
| CHG02 | ... | ... | ... | ... | ... |

## 3. 机器检查结果

### 3.1 数字一致性扫描
```
python scripts/scan_number_consistency.py <paper_dir> --fail-on-stale
```
结果：PASS/FAIL + 关键行

### 3.2 Claim ledger 对账
```
python scripts/verify_claim_ledger.py <paper_dir>
```
结果：PASS/FAIL + 不一致条目 ID

### 3.3 写作风格扫描
```
python scripts/check_writing_style.py <paper_dir>
```
结果：PASS/FAIL + 命中条目

### 3.4 TMLR 合规扫描
```
python scripts/check_tmlr_compliance.py <paper_dir> --names "..."
```
结果：G1-G11 逐门状态

### 3.5 验收门
```
python scripts/run_acceptance_gates.py gates_config.json
```
结果：x/x PASS，exit code

## 4. TMLR 合规状态表（G1-G11）

| 门 | 检查项 | 状态 | 备注 |
|---|---|---|---|
| G1 | tmlr 模板 | ✅/❌/⏳ | |
| G2 | US Letter + pdflatex | | |
| G3 | 全文匿名 | | |
| G4 | 匿名仓库 | | |
| G5 | 补充材料 <=100MB | | |
| G6 | 引用格式 tmlr.bst | | |
| G7 | Broader Impact | | |
| G8 | OpenReview 表单 | | |
| G9 | 交叉论文重叠 | | |
| G10 | 双盲隔离 | | |
| G11 | 验收门 + 哈希对账 | | |

## 5. 开放事项 / 阻塞项

| ID | 事项 | 阻塞类型 | 需要的输入 | 建议 |
|---|---|---|---|---|
| O01 | | | | |

## 6. 交付物清单

- [ ] manuscript（tex + pdf + 哈希）
- [ ] evidence package（JSON + scripts + protocol + 哈希）
- [ ] evidence_manifest.json（已校验）
- [ ] CLAIM_LEDGER.md（已对账）
- [ ] 本轮报告（本文件）