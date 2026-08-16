# 失败类反例夹具(scan_figure_claims 回归)— Voyager 自动课程式
# dirty = 失败类集合(未定义 fig label 引用 / 缺失图片文件 / 孤儿图), scanner 必须命中;
# clean = 控制组(零误报, exit 0)。
# dirty 内含排除探针(ROUND_R1.tex / reports/draft.tex / .r1_verify_backup/)——
# 扫描器必须跳过它们(族内排除约定), 只扫 1 个 tex 文件。
# 配套: scripts/scanner_regression.py(族级 manifest, ERROR 键决定退出码)
