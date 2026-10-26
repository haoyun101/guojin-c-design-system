#!/usr/bin/env bash
# 国金证券客户端设计系统 skill · 升级自检
# ------------------------------------------------------------------
# source of truth:Design 站「下载区」托管的 skill 包文件名所含版本号
#   站点:https://gjzqdesign.netlify.app/index.html
#   包名:assets/guojin-ds-skill-vX.Y.Z.zip(下载按钮 href)
# 逻辑:抓 index.html → 解析远端版本 → 比对本地 VERSION
#   落后 → 下载该 zip、自动定位含 SKILL.md 的顶层目录、覆盖安装
# 设计原则:失败永不阻断 skill 本体(任何异常都 exit 0 让本体继续)。
# ------------------------------------------------------------------
set -uo pipefail

# ===== 配置(可用环境变量覆盖)=====
SITE_BASE="${GJDS_UPDATE_BASE:-https://gjzqdesign.netlify.app}"
INDEX_URL="$SITE_BASE/index.html"
PROXY="${GJDS_UPDATE_PROXY-}"          # 站点为公网 CDN,默认无需代理;需要时传入,如 http://127.0.0.1:7897

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_VERSION_FILE="$SKILL_DIR/VERSION"

local_ver="$(tr -d '[:space:]' < "$LOCAL_VERSION_FILE" 2>/dev/null || echo 0)"
[ -z "$local_ver" ] && local_ver=0

curl_opts=(-fsSL --max-time 15)
[ -n "$PROXY" ] && curl_opts+=(--proxy "$PROXY")

# ----- 1. 抓站点首页 -----
html="$(curl "${curl_opts[@]}" "$INDEX_URL" 2>/dev/null || true)"
if [ -z "$html" ]; then
  echo "SKILL-UPDATE: 检查失败(网络/站点不可达),用本地版本 ${local_ver} 继续"
  exit 0
fi

# ----- 2. 解析远端版本(从下载区 zip 文件名)-----
zip_path="$(printf '%s' "$html" | grep -oE '[^"'"'"' ]*guojin-ds-skill-v[0-9.]+\.zip' | head -n1 || true)"
remote_ver="$(printf '%s' "$zip_path" | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' | head -n1 | tr -d 'v' || true)"
if [ -z "${remote_ver}" ]; then
  echo "SKILL-UPDATE: 未能在站点解析到版本号,用本地 ${local_ver} 继续"
  exit 0
fi

# ----- 3. 版本比对(sort -V,semver 正确比大小)-----
newest="$(printf '%s\n%s\n' "${local_ver}" "${remote_ver}" | sort -V | tail -n1)"
if [ "${remote_ver}" = "${local_ver}" ] || [ "${newest}" = "${local_ver}" ]; then
  exit 0   # 已最新或本地更新,静默继续
fi

echo "SKILL-UPDATE: 发现新版本 ${remote_ver}(本地 ${local_ver}),开始更新…"

# ----- 4. 下载 zip(相对路径补全为绝对 URL)-----
case "${zip_path}" in
  http*) dl_url="${zip_path}" ;;
  /*)    dl_url="${SITE_BASE}${zip_path}" ;;
  *)     dl_url="${SITE_BASE}/${zip_path#./}" ;;
esac

tmp="$(mktemp -d)"; trap 'rm -rf "${tmp}"' EXIT
curl "${curl_opts[@]}" "${dl_url}" -o "${tmp}/pkg.zip" 2>/dev/null \
  || { echo "SKILL-UPDATE: 下载失败,保留本地继续"; exit 0; }
unzip -q -o "${tmp}/pkg.zip" -d "${tmp}/x" 2>/dev/null \
  || { echo "SKILL-UPDATE: 解压失败,保留本地继续"; exit 0; }

# ----- 5. 自动定位含 SKILL.md 的顶层目录(包名/目录名可能与本地不同)-----
skillmd="$(find "${tmp}/x" -maxdepth 3 -name SKILL.md -print -quit 2>/dev/null || true)"
src="$(dirname "${skillmd}" 2>/dev/null || true)"
if [ -z "${skillmd}" ] || [ ! -d "${src}" ]; then
  echo "SKILL-UPDATE: 包结构异常(未找到 SKILL.md),放弃本次更新"
  exit 0
fi

# ----- 6. 覆盖安装(rsync 临时文件+rename,自覆盖也安全;无 rsync 回退 cp)-----
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete "${src}/" "${SKILL_DIR}/" 2>/dev/null \
    || { echo "SKILL-UPDATE: 写入失败,保留本地继续"; exit 0; }
else
  cp -rf "${src}/." "${SKILL_DIR}/" 2>/dev/null \
    || { echo "SKILL-UPDATE: 写入失败,保留本地继续"; exit 0; }
fi

chmod +x "${SKILL_DIR}/scripts/"*.sh 2>/dev/null || true
echo "${remote_ver}" > "${LOCAL_VERSION_FILE}"
echo "SKILL-UPDATE: 已更新到 ${remote_ver} ✅  请重新触发本 skill 以加载新版"
exit 0
