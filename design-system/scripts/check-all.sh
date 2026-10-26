#!/usr/bin/env bash
# 合规一键校验 —— 把"可靠性三层"的第三层(确定性校验)落到"自动执行"。
# skill 完整性自检(validate.py) + 生成页面合规校验(check-page.py)。
# 用法:
#   bash scripts/check-all.sh [页面.html | 页面目录 ...]
#   - 不给参数:递归扫当前目录所有 .html(自动跳过 skill 自身与 node_modules)
#   - 由 CI / pre-commit 调用;**P0>0 或自检失败即退出 1**,用于阻断交付/提交。
set -uo pipefail
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_BASE="$(basename "$SKILL_DIR")"
fail=0

echo "[1/2] skill 完整性自检 (validate.py)"
python3 "$SKILL_DIR/scripts/validate.py" "$SKILL_DIR" || fail=1

echo ""
echo "[2/2] 页面合规校验 (check-page.py)"
targets=()
if [ "$#" -gt 0 ]; then
  for a in "$@"; do
    if [ -d "$a" ]; then
      while IFS= read -r f; do targets+=("$f"); done \
        < <(find "$a" -name '*.html' -not -path '*/node_modules/*' -not -path "*/$SKILL_BASE/*")
    elif [ -f "$a" ]; then
      targets+=("$a")
    fi
  done
else
  while IFS= read -r f; do targets+=("$f"); done \
    < <(find . -name '*.html' -not -path '*/node_modules/*' -not -path "*/$SKILL_BASE/*")
fi

if [ "${#targets[@]}" -eq 0 ]; then
  echo "  (无 .html 页面可校验,跳过)"
else
  python3 "$SKILL_DIR/scripts/check-page.py" "${targets[@]}" || fail=1
fi

echo ""
if [ "$fail" -ne 0 ]; then
  echo "✗ 合规校验未通过(有 P0 或 skill 自检失败)——已阻断。修完再试。"
  exit 1
fi
echo "✓ 合规校验通过。"
