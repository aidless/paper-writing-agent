"""rebuttal_sim.py — rebuttal 模拟门禁(τ-bench 两阶段,E060 落地,I3)。

投稿前验证 rebuttal 草稿能否过关:三类模拟审稿人(证据追问/表述越界/机制质疑)
逐条追问,agent 回应,两阶段判定(completion 完成度 / consultation 满意度),正交报告;
未过 → 回 Phase 4 补证据/收紧表述,不进 Phase 5。

sim_reviewer_fn 可插拔(接真实 LLM):输入 (reviewer_type, rebuttal_text, evidence_dir),
输出 {"completion": 0/1, "satisfaction": 0/1, "note": str}。
默认 mock 用于 selftest 与管线验证。

--live(2026-08-15, 底座 E079): 接共享 llm_client.LlmClient(research-kit/llm-client)。
  - 无 DEEP_API_KEY 或 LLM_DRY_RUN=1 → sim 模式(关键词模拟, 与 mock 同构, 确定性), 全链路无 key 可验证;
  - 有 key → live(真实 LLM, 指数退避重试); 每次调用留溯源日志(llm_calls.jsonl);
  - 结果带 reviewer 标记(mock / live-sim / live, E078 溯源纪律)。

用法:
  python rebuttal_sim.py --rebuttal rebuttal.md --evidence ../evidence --out out/rebuttal_sim
  python rebuttal_sim.py --rebuttal rebuttal.md --live        # live; 无 key 自动 sim
  python rebuttal_sim.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import zlib
from pathlib import Path


def _stable_seed(*parts) -> int:
    """确定性种子(替代内置 hash(): PYTHONHASHSEED 进程随机化会让 mock 噪声
    每次运行不同 → selftest flaky, 实测 8 次运行 2 次失败, 2026-08)。"""
    return zlib.crc32("|".join(str(p) for p in parts).encode("utf-8"))


# 审稿人"不满"噪声: 默认 0 = 门禁确定性(好 rebuttal 恒 PASS / 坏 rebuttal 恒 FAIL)。
# >0(如 0.1)用于模拟"审稿人偶尔不满意"的场景实验; 门禁语义不应依赖随机性——
# 否则好 rebuttal 有 1-(1-noise)^n 概率随机 FAIL(实测坑: selftest 25% 失败率)。
_MOCK_NOISE = float(os.environ.get("REBUTTAL_MOCK_NOISE", "0"))

# 共享 LLM 底座(与 live_reviewer.py 同一路径); 缺失时 --live 报错而非静默
_RK_LLM = Path(os.environ.get("PWA_RESEARCH_KIT", Path.home() / "research-kit") / "llm-client")

REVIEWER_TYPES = ["evidence-doubt", "overclaim", "mechanism"]

_TYPE_PROMPTS = {
    "evidence-doubt": "你是模拟审稿人, 专长【证据追问】: 质疑 rebuttal 是否用可重跑证据"
                      "(重算/文件/ledger/附录)回应了对数字与证据的质疑, 而非空口辩解。",
    "overclaim": "你是模拟审稿人, 专长【表述越界】: 质疑 rebuttal 是否把过度声明收窄到"
                 "数据支持的范围(收紧/消融/限定), 而非坚持原泛化断言。",
    "mechanism": "你是模拟审稿人, 专长【机制质疑】: 质疑 rebuttal 是否解释了方法机制或"
                 "给出支撑机制的证据(消融/ablation/机理), 而非回避机制问题。",
}

_LIVE_CLIENT = None


def client_mode() -> str:
    """当前接入模式: live / sim(无 key 或 LLM_DRY_RUN=1)。未 import 底座时为 'mock'。"""
    global _LIVE_CLIENT
    if _LIVE_CLIENT is None:
        if not _RK_LLM.exists():
            return "mock"
        sys.path.insert(0, str(_RK_LLM))
        from llm_client import LlmClient
        _LIVE_CLIENT = LlmClient(simulate_fn=_simulate_review)
    return _LIVE_CLIENT.mode


def _simulate_review(messages, meta) -> str:
    """确定性模拟(与 mock_review_fn 同构): 关键词命中=完成, 10% 噪声不满。

    注意: rebuttal 原文从 meta['rebuttal'] 取, 不从 user 消息解析——user 消息含
    「证据目录」等包装文本, 会污染关键词检测(实测坏 rebuttal 因此误 PASS)。
    """
    rtype = str((meta or {}).get("reviewer_type", ""))
    rebuttal = str((meta or {}).get("rebuttal", ""))
    text = rebuttal.lower()
    has_evidence = any(k in text for k in ("recompute", "重算", "evidence", "证据",
                                           "file:", "ledger", "appendix", "附录", "消融",
                                           "ablation", "recover", "收紧", "scope"))
    rng = random.Random(_stable_seed(rtype, text[:80]))
    completion = 1 if has_evidence else 0
    satisfaction = 1 if completion else 0
    if completion and _MOCK_NOISE > 0 and rng.random() >= (1 - _MOCK_NOISE):
        satisfaction = 0  # 可配置噪声: 模拟审稿人不满(默认关闭, 保门禁确定性)
    return json.dumps({"completion": completion, "satisfaction": satisfaction,
                       "note": "sim: has_evidence=" + str(has_evidence)}, ensure_ascii=False)


def _parse_verdict(text: str) -> dict:
    """解析 LLM 输出 JSON(容错: 混排散文也能提 completion/satisfaction)。"""
    rec = {"completion": 0, "satisfaction": 0, "note": "parse-fallback"}
    try:
        o = json.loads(text)
        if isinstance(o, dict):
            rec.update({k: o.get(k) for k in ("completion", "satisfaction", "note") if k in o})
    except Exception:
        pass
    m = re.search(r'"completion"\s*:\s*([01])', text or "")
    if m:
        rec["completion"] = int(m.group(1))
    m = re.search(r'"satisfaction"\s*:\s*([01])', text or "")
    if m:
        rec["satisfaction"] = int(m.group(1))
    rec["completion"] = 1 if rec["completion"] in (1, "1", True) else 0
    rec["satisfaction"] = 1 if rec["satisfaction"] in (1, "1", True) else 0
    return rec


def live_review_fn(reviewer_type: str, rebuttal_text: str, evidence_dir: str | Path) -> dict:
    """真实/模拟 LLM 审稿(经 llm_client 底座; 无 key 自动 sim, 调用级溯源)。"""
    global _LIVE_CLIENT
    if _LIVE_CLIENT is None:
        if not _RK_LLM.exists():
            raise RuntimeError("共享 LLM 底座缺失: research-kit/llm-client 不存在")
        sys.path.insert(0, str(_RK_LLM))
        from llm_client import LlmClient
        _LIVE_CLIENT = LlmClient(simulate_fn=_simulate_review)
    client = _LIVE_CLIENT
    system = (_TYPE_PROMPTS.get(reviewer_type, "你是模拟审稿人。") +
              ' 严格只返回 JSON {"completion": 0/1, "satisfaction": 0/1, "note": "..."}。'
              "completion=回应是否未回避且给出证据/收紧; satisfaction=该回应是否让你满意接受。")
    user = (f"rebuttal 草稿:\n{rebuttal_text}\n\n"
            f"(证据目录: {evidence_dir}; 判断仅基于文本, 证据真伪由工具核验)")
    content, usage = client.chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        meta={"tool": "rebuttal_sim", "reviewer_type": reviewer_type, "rebuttal": rebuttal_text})
    verdict = _parse_verdict(content)
    return {**verdict, "note": f"{verdict['note']} [{client.mode}, tokens={usage['tokens_in'] + usage['tokens_out']}]"}


def mock_review_fn(reviewer_type: str, rebuttal_text: str, evidence_dir: str | Path) -> dict:
    """确定性 mock: 回应含"重算/证据/文件/收紧/消融"等关键词即视为完成/满意。"""
    text = rebuttal_text.lower()
    has_evidence = any(k in text for k in ("recompute", "重算", "evidence", "证据",
                                           "file:", "ledger", "appendix", "附录", "消融",
                                           "ablation", "recover", "收紧", "scope"))
    rng = random.Random(_stable_seed(reviewer_type, text[:80]))
    completion = 1 if has_evidence else 0
    # 满意度: 默认确定性(completion 即满意); REBUTTAL_MOCK_NOISE>0 时按噪声不满
    satisfaction = 1 if completion else 0
    if completion and _MOCK_NOISE > 0 and rng.random() >= (1 - _MOCK_NOISE):
        satisfaction = 0
    return {"completion": completion, "satisfaction": satisfaction,
            "note": "mock: has_evidence=" + str(has_evidence)}


def run_simulation(rebuttal_text: str, evidence_dir: str | Path,
                   review_fn, reviewers=None, reviewer="mock") -> dict:
    reviewers = reviewers or REVIEWER_TYPES
    rows = []
    for rtype in reviewers:
        res = review_fn(rtype, rebuttal_text, evidence_dir)
        rows.append({"reviewer": rtype, **res})
    completions = [r["completion"] for r in rows]
    satisfactions = [r["satisfaction"] for r in rows]
    return {
        "n_reviewers": len(rows),
        "completion_rate": sum(completions) / len(rows),
        "satisfaction_rate": sum(satisfactions) / len(rows),
        "rows": rows,
        "gate": {"passed": all(completions) and all(satisfactions)},
        "reviewer": reviewer,  # mock / live-sim / live(溯源, E078)
        "note": "两阶段正交: 完成度=未回避且有证据;满意度=模拟审稿人接受。任一 0 → 回 Phase 4。",
    }


def render(result: dict, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "rebuttal_sim_result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    md = ["# Rebuttal 模拟结果", "",
          f"- 门禁: **{'PASS' if result['gate']['passed'] else 'FAIL'}(未过 → 回 Phase 4)**",
          f"- 审稿源: {result.get('reviewer', 'unknown')} (mock=关键词 / live-sim=模拟 / live=真实 LLM)",
          f"- completion: {result['completion_rate']:.2f} / satisfaction: {result['satisfaction_rate']:.2f}", ""]
    for r in result["rows"]:
        md.append(f"- {r['reviewer']}: completion={r['completion']} satisfaction={r['satisfaction']} ({r['note']})")
    (out / "rebuttal_sim_report.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


def selftest() -> bool:
    good = ("We recompute the statistic from the evidence file (results/e1.json); "
            "we tighten the claim to 'on the three tested datasets'; the mechanism "
            "is supported by the ablation in the appendix.")
    bad = "The reviewers are wrong; we believe our claim is correct."
    r_good = run_simulation(good, ".", mock_review_fn)
    r_bad = run_simulation(bad, ".", mock_review_fn)
    assert r_good["gate"]["passed"], r_good
    assert not r_bad["gate"]["passed"], r_bad
    print("[good rebuttal -> gate PASS; bad rebuttal -> gate FAIL] ✓")
    assert r_good["satisfaction_rate"] >= r_bad["satisfaction_rate"]
    print("[completion/satisfaction 两阶段正交] ✓")
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        render(r_bad, Path(td))
        assert (Path(td) / "rebuttal_sim_result.json").exists()
    print("[render report] ✓")
    return True


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="rebuttal 模拟门禁(τ-bench 两阶段)")
    ap.add_argument("--rebuttal", help="rebuttal 草稿文本文件")
    ap.add_argument("--evidence", default=".")
    ap.add_argument("--out", default="out/rebuttal_sim")
    ap.add_argument("--live", action="store_true",
                    help="接 LLM 底座(real/sim 自动; 无 DEEP_API_KEY 或 LLM_DRY_RUN=1 → sim)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return 0 if selftest() else 1
    text = Path(args.rebuttal).read_text(encoding="utf-8")
    review_fn = mock_review_fn
    reviewer = "mock"
    if args.live:
        review_fn = live_review_fn
        reviewer = {"live": "live", "sim": "live-sim", "mock": "mock"}.get(client_mode(), "mock")
    result = run_simulation(text, args.evidence, review_fn, reviewer=reviewer)
    render(result, Path(args.out))
    return 0 if result["gate"]["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
