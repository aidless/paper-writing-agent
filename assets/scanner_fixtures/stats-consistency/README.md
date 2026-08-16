# 失败类反例夹具(scan_stats_consistency 回归)— Voyager 自动课程式
# 每个子目录 = 一个失败类: scanner 必须命中它;clean 是控制组(不得误报,
# 且 ERROR 段全零时退出码必须为 0)。
# 失败类: impossible-p / out-of-range / p-stat-mismatch / p-ineq-contradiction /
#          same-line-n-conflict / sign-mismatch(WARN) / p-zero(WARN) /
#          mcp-no-correction(WARN)
# 配套: scripts/scanner_regression.py(族级 manifest,ERROR 键决定退出码)
