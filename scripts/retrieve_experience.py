#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
retrieve_experience.py — 论文 agent 三因子经验检索(recency × importance × relevance) + α 任务类型加权
=====================================================================================================

来源:
- references/memory-retrieval.md(Generative Agents 2304.03442 三因子设计) — 本脚本是其落地实现;
- MemoryDecoder-at-Scale 2607.27919 α 策略(E073/lessons.md L016) — 任务类型条件加权。

评分(三因子, 权重随任务类型变化, 参照 E073 的 α 表):
    score = w_rel·relevance + w_imp·importance + w_rec·recency
  - relevance: 任务与条目情境的相似度(keyword Jaccard 确定性; ollama 可达时用嵌入)
  - importance: 条目第 11 列 importance(0-1); 缺省按 conf/status 推导(high=0.8/med=0.6/low=0.4, verified+0.1)
  - recency:   距最近确认日期的指数衰减(半衰期 30 天)
  - α 权重表: knowledge(0.75/0.15/0.10) general(0.60/0.25/0.15) reasoning(0.45/0.30/0.25)
    hallucination_sensitive(0.50/0.30/0.20) —— 知识任务重相关性(记忆), 推理/防幻觉压相关性、抬重要性/新近度。

与 retrieve_lessons.py 的分工: retrieve_lessons 是 continuous-memory 的 LESSON 检索(相似度×置信度×新近度,
已 A/B hold); 本脚本是论文 agent 的经验/FINDINGS 检索(三因子 + importance), 两者共享 lessons.md。

用法:
  python retrieve_experience.py --task "<当前任务>" [--ledger lessons.md] [--findings f.jsonl]
                                 [--top 5] [--task-type auto] [--out digest_experience.md]
                                 [--include-draft]   # 默认只检索 verified/active(证据门禁); 加此参才含 draft
  python retrieve_experience.py --selftest
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from datetime import datetime, date

OLLAMA_EMBED = "http://localhost:11434/api/embed"
EMBED_MODEL = "nomic-embed-text"
EMBED_TIMEOUT = 8.0

# lessons.md 11 列(2026-08-15 起含 importance)
F_ID, F_SIT, F_ACT, F_RES, F_EVI, F_CONF, F_STAT, F_CNT, F_DATE, F_SRC, F_IMP = range(11)
CONF_MAP = {"high": 0.8, "med": 0.6, "low": 0.4}

# α 任务类型权重表(与 retrieve_lessons.py 的 E073 表同构; 列 = relevance/importance/recency)
TASK_TYPE_CUES = {
    "knowledge": ["引用", "事实", "知识", "检索", "查询", "查找", "查证", "溯源", "文献", "论文", "综述",
                  "数据", "数据集", "citation", "fact", "reference", "lookup", "retriev"],
    "reasoning": ["证明", "推导", "推理", "逻辑", "数学", "引理", "定理", "反证", "严格", "论证", "因果",
                  "统计", "检验", "显著", "wilcoxon", "mcnemar", "friedman", "proof", "derive", "logic",
                  "reason", "lemma", "theorem", "deduc", "significan"],
    "hallucination_sensitive": ["幻觉", "核实", "核查", "校验", "严谨", "可信", "校准", "置信", "防错", "审稿",
                                "回吐", "hallucin", "fact-check", "factcheck", "verify", "claim", "reliab",
                                "calibrat"],
}
TASK_TYPE_WEIGHTS = {
    "knowledge":               {"rel": 0.75, "imp": 0.15, "rec": 0.10},
    "general":                 {"rel": 0.60, "imp": 0.25, "rec": 0.15},
    "reasoning":               {"rel": 0.45, "imp": 0.30, "rec": 0.25},
    "hallucination_sensitive": {"rel": 0.50, "imp": 0.30, "rec": 0.20},
}
ACTIVE_STATES = {"verified", "active"}


def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def task_type_of(task):
    t = task.lower()
    for tt in ("hallucination_sensitive", "knowledge", "reasoning"):
        if any(k in t for k in TASK_TYPE_CUES[tt]):
            return tt
    return "general"


def _derive_importance(conf, stat):
    imp = CONF_MAP.get(conf, 0.5)
    if stat in ("verified", "active"):
        imp = min(0.95, imp + 0.1)
    return round(imp, 2)


def parse_lessons(text):
    """解析 lessons.md(容忍缺列/注释/空行; importance 缺省推导)。"""
    entries = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4 or not re.match(r"^L\d+", parts[0]):
            continue
        p = (parts + [""] * 11)[:11]
        conf = p[F_CONF].lower()
        stat = p[F_STAT].lower()
        imp_raw = p[F_IMP]
        entries.append({
            "id": p[F_ID], "sit": p[F_SIT], "act": p[F_ACT], "res": p[F_RES],
            "evi": p[F_EVI], "conf": conf, "stat": stat,
            "cnt": p[F_CNT], "date": p[F_DATE], "src": p[F_SRC],
            "importance": float(imp_raw) if re.match(r"^\d+(\.\d+)?$", imp_raw)
                          and 0.0 <= float(imp_raw) <= 1.0 else _derive_importance(conf, stat),
        })
    return entries


def parse_findings_jsonl(path):
    """可选: 结构化 FINDINGS JSONL(每条含 id/sit[/act/importance/date]); FINDINGS.md 自由格式需手工转。"""
    out = []
    if not path or not os.path.exists(path):
        return out
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            imp = rec.get("importance")
            out.append({
                "id": rec.get("id", "F-" + str(len(out))),
                "sit": rec.get("sit", rec.get("context", "")),
                "act": rec.get("act", rec.get("action", "")),
                "res": rec.get("res", rec.get("result", "")),
                "evi": rec.get("evi", rec.get("evidence", "")),
                "conf": rec.get("conf", "med"), "stat": rec.get("stat", "verified"),
                "cnt": rec.get("cnt", "1"), "date": rec.get("date", ""),
                "src": rec.get("src", "findings"),
                "importance": float(imp) if imp is not None and 0.0 <= float(imp) <= 1.0 else 0.6,
            })
    return out


def days_ago(date_str):
    try:
        d = datetime.strptime(date_str.strip()[:10], "%Y-%m-%d").date()
        return max(0, (date.today() - d).days)
    except Exception:
        return None


def recency(date_str):
    d = days_ago(date_str)
    return round(math.exp(-(d / 30.0)), 4) if d is not None else 0.5


def keywords(text):
    return set(re.findall(r"[a-z0-9\u4e00-\u9fff]+", text.lower()))


def keyword_sim(a, b):
    ka, kb = keywords(a), keywords(b)
    if not ka or not kb:
        return 0.0
    return len(ka & kb) / len(ka | kb)


def embed_batch(texts):
    body = json.dumps({"model": EMBED_MODEL, "input": list(texts)}).encode("utf-8")
    req = __import__("urllib.request", fromlist=["Request"]).Request(
        OLLAMA_EMBED, data=body, headers={"Content-Type": "application/json"})
    with __import__("urllib.request", fromlist=["urlopen"]).urlopen(req, timeout=EMBED_TIMEOUT) as r:
        data = json.loads(r.read().decode("utf-8"))
    if isinstance(data.get("embeddings"), list) and data["embeddings"]:
        return data["embeddings"]
    if isinstance(data.get("embedding"), list):
        return [data["embedding"]]
    raise ValueError("unexpected embed response")


def cos(a, b):
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def rank(entries, task, backend, task_type):
    if backend == "ollama":
        vecs = embed_batch([task] + [e["sit"] for e in entries])
        tvec = vecs[0]
        rels = [max(0.0, (cos(tvec, v) + 1.0) / 2.0) for v in vecs[1:]]
    else:
        rels = [keyword_sim(task, e["sit"]) for e in entries]
    w = TASK_TYPE_WEIGHTS.get(task_type, TASK_TYPE_WEIGHTS["general"])
    for e, rel in zip(entries, rels):
        e["relevance"] = round(rel, 4)
        e["recency"] = recency(e["date"])
        e["score"] = round(w["rel"] * rel + w["imp"] * e["importance"] + w["rec"] * e["recency"], 4)
    return sorted(entries, key=lambda e: e["score"], reverse=True)


def main():
    ap = argparse.ArgumentParser(description="P-三因子经验检索(论文 agent)")
    ap.add_argument("--task", help="当前任务目标")
    ap.add_argument("--ledger", default=os.path.join(".agent-memory", "ledger", "lessons.md"))
    ap.add_argument("--findings", default="", help="可选结构化 FINDINGS JSONL")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--task-type", default="auto",
                    choices=["auto", "knowledge", "general", "reasoning", "hallucination_sensitive"])
    ap.add_argument("--out", default="", help="digest 输出路径(默认打印 JSON)")
    ap.add_argument("--include-draft", action="store_true",
                    help="默认只检索 verified/active(证据门禁); 加此参才含 draft 条目")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        entries = [
            {"id": "T1", "sit": "审稿发现数字不一致", "act": "重算并核对证据", "res": "通过", "evi": "demo",
             "conf": "high", "stat": "verified", "cnt": "2", "date": "2026-08-01", "src": "demo", "importance": 0.95},
            {"id": "T2", "sit": "审稿发现数字不一致", "act": "重算并核对证据", "res": "通过", "evi": "demo",
             "conf": "high", "stat": "verified", "cnt": "2", "date": "2026-08-01", "src": "demo", "importance": 0.40},
            {"id": "T3", "sit": "生成周报", "act": "列表格", "res": "ok", "evi": "demo",
             "conf": "med", "stat": "draft", "cnt": "0", "date": "2026-08-10", "src": "demo", "importance": 0.6},
        ]
        r = rank(list(entries), "审稿时核实论文里的数字", "keyword", "hallucination_sensitive")
        assert r[0]["id"] == "T1", "importance 应把同相关性高重要条目置顶"
        assert r[0]["score"] > r[1]["score"]
        # α: 同一任务强制 knowledge vs hallucination, T1(高 importance)在 hallucination 下更靠前
        rk = rank(list(entries), "审稿时核实论文里的数字", "keyword", "knowledge")
        assert r[0]["id"] == rk[0]["id"]
        print("[PASS] retrieve_experience selftest (importance 排序 + α 加权)")
        return 0

    ledger_path = os.path.abspath(args.ledger)
    if not os.path.exists(ledger_path):
        print(json.dumps({"ok": True, "count": 0, "note": "ledger 不存在: %s" % ledger_path}, ensure_ascii=False))
        return 0
    with open(ledger_path, encoding="utf-8") as f:
        entries = parse_lessons(f.read())
    entries += parse_findings_jsonl(args.findings)
    if not args.include_draft:
        entries = [e for e in entries if e["stat"] in ACTIVE_STATES]
    task = args.task or ""
    task_type = task_type_of(task) if args.task_type == "auto" else args.task_type

    backend = "keyword"
    try:
        if entries:
            embed_batch([task]) if task else None
            backend = "ollama"
    except Exception:
        pass

    ranked = rank(entries, task, backend, task_type)
    top = ranked[: args.top]
    out = {
        "ok": True, "used": backend, "count": len(ranked), "task_type": task_type,
        "weights": TASK_TYPE_WEIGHTS[task_type],
        "top": [{"id": e["id"], "score": e["score"], "rel": e["relevance"],
                 "imp": e["importance"], "rec": e["recency"], "stat": e["stat"]} for e in top],
    }
    if args.out:
        lines = ["# 论文 agent 经验摘要(三因子检索, 勿手改)", "",
                 "- 任务: %s" % task, "- 时间: %s | 条目: %d | 类型: %s | 权重: %s" % (
                     now_iso(), len(ranked), task_type, TASK_TYPE_WEIGHTS[task_type]), ""]
        for e in top:
            lines.append("- **%s** [imp=%.2f rel=%.2f rec=%.2f, %s]\n  - 情境: %s\n  - 动作: %s" % (
                e["id"], e["importance"], e["relevance"], e["recency"], e["stat"], e["sit"], e["act"]))
        with open(args.out, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        out["digest"] = args.out
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
