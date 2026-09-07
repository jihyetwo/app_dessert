#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""preview_server.py
DESSERT 네이버 블로그 및 앱 게시판 시각적 미리보기 & 원클릭 클립보드 복사 로컬 웹 서버.
실행: python3 scripts/preview_server.py [--port 8766]
"""

import os
import re
import json
import http.server
import socketserver
import urllib.parse
from sync_marketing_to_blog import get_all_campaigns, REPO_OUTPUT

PORT = 8766

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DESSERT 디저트 팩트체크 · 블로그 & 앱게시판 배선 대시보드</title>
  <style>
    :root {
      --naver-green: #03C75A;
      --naver-dark: #029f48;
      --dessert-amber: #d97706;
      --dessert-red: #ef4444;
      --bg: #F8F9FA;
      --card-bg: #FFFFFF;
      --text: #1E293B;
      --text-muted: #64748B;
      --border: #E2E8F0;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Apple SD Gothic Neo", sans-serif; }
    body { background: var(--bg); color: var(--text); display: flex; height: 100vh; overflow: hidden; }
    
    /* 사이드바 */
    .sidebar { width: 340px; background: #fff; border-right: 1px solid var(--border); display: flex; flex-direction: column; flex-shrink: 0; }
    .sidebar-header { padding: 18px 20px; border-bottom: 1px solid var(--border); background: #fafafa; }
    .sidebar-header h1 { font-size: 16px; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px; }
    .sidebar-header p { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
    .search-box { padding: 12px 16px; border-bottom: 1px solid var(--border); }
    .search-input { width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; outline: none; }
    .search-input:focus { border-color: var(--dessert-amber); }
    .campaign-list { flex: 1; overflow-y: auto; list-style: none; }
    .campaign-item { padding: 14px 16px; border-bottom: 1px solid #f1f5f9; cursor: pointer; transition: background 0.15s; }
    .campaign-item:hover { background: #f8fafc; }
    .campaign-item.active { background: #fffbeb; border-left: 4px solid var(--dessert-amber); }
    .campaign-cat { font-size: 11px; font-weight: 600; color: var(--text-muted); }
    .campaign-name { font-size: 14px; font-weight: 600; color: #1e293b; margin-top: 2px; word-break: break-all; }
    .campaign-badges { display: flex; gap: 6px; margin-top: 6px; }
    .badge { font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: 600; }
    .badge-blog { background: #dcfce7; color: #15803d; }
    .badge-app { background: #e0f2fe; color: #0369a1; }
    
    /* 메인 영역 */
    .main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
    .top-bar { height: 64px; background: #fff; border-bottom: 1px solid var(--border); padding: 0 24px; display: flex; align-items: center; justify-content: space-between; }
    .top-title { font-size: 16px; font-weight: 700; }
    .top-actions { display: flex; gap: 8px; }
    .btn { padding: 8px 14px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; border: none; transition: 0.15s; display: inline-flex; align-items: center; gap: 6px; }
    .btn-naver { background: var(--naver-green); color: #fff; }
    .btn-naver:hover { background: var(--naver-dark); }
    .btn-amber { background: var(--dessert-amber); color: #fff; }
    .btn-amber:hover { background: #b45309; }
    .btn-secondary { background: #f1f5f9; color: #334155; }
    .btn-secondary:hover { background: #e2e8f0; }
    
    .tab-bar { display: flex; background: #fff; border-bottom: 1px solid var(--border); padding: 0 24px; gap: 20px; }
    .tab { padding: 12px 0; font-size: 14px; font-weight: 600; color: var(--text-muted); cursor: pointer; border-bottom: 2px solid transparent; transition: 0.15s; }
    .tab.active { color: var(--naver-green); border-bottom-color: var(--naver-green); }
    .content-area { flex: 1; overflow-y: auto; padding: 32px; display: flex; justify-content: center; }
    .viewer { width: 100%; max-width: 780px; background: #fff; padding: 40px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid var(--border); }
    
    /* 네이버 블로그 스마트에디터 스타일 */
    .blog-view h1 { font-size: 26px; font-weight: 800; margin-bottom: 20px; line-height: 1.4; color: #111; border-bottom: 2px solid #111; padding-bottom: 12px; }
    .blog-view h2 { font-size: 20px; font-weight: 700; margin-top: 32px; margin-bottom: 14px; color: #d97706; border-left: 4px solid #d97706; padding-left: 10px; }
    .blog-view h3 { font-size: 17px; font-weight: 700; margin-top: 20px; margin-bottom: 10px; color: #1e293b; }
    .blog-view p { font-size: 15px; line-height: 1.8; margin-bottom: 14px; color: #222; word-break: keep-all; }
    .blog-view table { width: 100%; border-collapse: collapse; margin: 18px 0; font-size: 14px; }
    .blog-view th, .blog-view td { border: 1px solid #e2e8f0; padding: 10px 14px; text-align: left; }
    .blog-view th { background: #f8fafc; font-weight: 600; }
    .blog-view blockquote { background: #fffbeb; border-left: 4px solid #d97706; padding: 14px 18px; margin: 18px 0; border-radius: 6px; font-size: 14px; }
    .blog-view .img-placeholder { background: #f1f5f9; border: 2px dashed #cbd5e1; border-radius: 8px; padding: 24px; text-align: center; color: #64748b; font-size: 14px; margin: 20px 0; }
    
    /* 앱 게시판 스타일 */
    .app-view { white-space: pre-wrap; font-family: monospace; font-size: 13px; line-height: 1.7; color: #334155; }
    .raw-view { white-space: pre-wrap; font-family: monospace; font-size: 13px; line-height: 1.6; color: #1e293b; }
    
    .toast { position: fixed; bottom: 24px; right: 24px; background: #0f172a; color: #fff; padding: 12px 20px; border-radius: 8px; font-size: 13px; opacity: 0; transition: opacity 0.2s; pointer-events: none; z-index: 100; }
    .toast.show { opacity: 1; }
  </style>
</head>
<body>
  <div class="sidebar">
    <div class="sidebar-header">
      <h1>🍨 DESSERT 배선 허브</h1>
      <p>마케팅 기획서 → 네이버 블로그 & 앱게시판</p>
    </div>
    <div class="search-box">
      <input type="text" id="search" class="search-input" placeholder="캠페인 검색 (예: 삼겹살, WHO, 알룰로스)..." oninput="filterCampaigns()">
    </div>
    <ul class="campaign-list" id="campaign-list">
      <!-- 동적 로드 -->
    </ul>
  </div>

  <div class="main">
    <div class="top-bar">
      <div class="top-title" id="current-title">캠페인을 선택하세요</div>
      <div class="top-actions">
        <button class="btn btn-naver" onclick="copyCurrentBlog()">📋 네이버 블로그용 복사</button>
        <button class="btn btn-amber" onclick="copyCurrentTags()">🏷️ 태그 30개 복사</button>
        <button class="btn btn-secondary" onclick="copyCurrentApp()">📱 앱게시판 복사</button>
      </div>
    </div>
    <div class="tab-bar">
      <div class="tab active" onclick="setTab('blog')">네이버 블로그 미리보기</div>
      <div class="tab" onclick="setTab('app')">앱 게시판 텍스트</div>
      <div class="tab" onclick="setTab('raw')">마크다운 원문</div>
    </div>
    <div class="content-area">
      <div class="viewer" id="viewer">
        <div style="text-align: center; color: #94a3b8; padding-top: 100px;">
          좌측 목록에서 캠페인을 선택하시면 렌더링 결과와 복사 옵션이 표시됩니다.
        </div>
      </div>
    </div>
  </div>

  <div id="toast" class="toast">클립보드에 복사되었습니다!</div>

  <script>
    let allCampaigns = [];
    let currentCampaign = null;
    let currentContent = null;
    let currentTab = 'blog';

    async function loadCampaigns() {
      try {
        const res = await fetch('/api/campaigns');
        allCampaigns = await res.json();
        renderList(allCampaigns);
        if (allCampaigns.length > 0) {
          selectCampaign(allCampaigns[0].folder_name);
        }
      } catch (e) {
        console.error(e);
      }
    }

    function renderList(list) {
      const ul = document.getElementById('campaign-list');
      ul.innerHTML = '';
      list.forEach(c => {
        const li = document.createElement('li');
        li.className = 'campaign-item' + (currentCampaign === c.folder_name ? ' active' : '');
        li.onclick = () => selectCampaign(c.folder_name);
        li.innerHTML = `
          <div class="campaign-cat">${c.category}</div>
          <div class="campaign-name">${c.folder_name}</div>
          <div class="campaign-badges">
            <span class="badge badge-blog">블로그 2,500자</span>
            <span class="badge badge-app">앱게시판</span>
          </div>
        `;
        ul.appendChild(li);
      });
    }

    function filterCampaigns() {
      const q = document.getElementById('search').value.toLowerCase();
      const filtered = allCampaigns.filter(c => c.folder_name.toLowerCase().includes(q) || c.category.toLowerCase().includes(q));
      renderList(filtered);
    }

    async function selectCampaign(folder) {
      currentCampaign = folder;
      document.querySelectorAll('.campaign-item').forEach(el => {
        el.classList.toggle('active', el.querySelector('.campaign-name').innerText === folder);
      });
      document.getElementById('current-title').innerText = folder;
      
      const res = await fetch(`/api/content?folder=${encodeURIComponent(folder)}`);
      currentContent = await res.json();
      renderViewer();
    }

    function setTab(tab) {
      currentTab = tab;
      document.querySelectorAll('.tab').forEach((el, idx) => {
        el.classList.toggle('active', (tab === 'blog' && idx === 0) || (tab === 'app' && idx === 1) || (tab === 'raw' && idx === 2));
      });
      renderViewer();
    }

    function renderViewer() {
      if (!currentContent) return;
      const v = document.getElementById('viewer');
      if (currentTab === 'blog') {
        v.className = 'viewer blog-view';
        v.innerHTML = currentContent.blog_html || '<p>내용이 없습니다.</p>';
      } else if (currentTab === 'app') {
        v.className = 'viewer app-view';
        v.innerText = currentContent.app_md || '내용이 없습니다.';
      } else {
        v.className = 'viewer raw-view';
        v.innerText = currentContent.blog_md || '내용이 없습니다.';
      }
    }

    function copyToClipboard(text, msg) {
      navigator.clipboard.writeText(text).then(() => {
        const toast = document.getElementById('toast');
        toast.innerText = msg;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 2000);
      });
    }

    function copyCurrentBlog() {
      if (currentContent && currentContent.blog_md) {
        copyToClipboard(currentContent.blog_md, '📋 네이버 블로그 원고가 복사되었습니다!');
      }
    }

    function copyCurrentTags() {
      if (currentContent && currentContent.blog_md) {
        const m = currentContent.blog_md.match(/🏷️\s*네이버\s*블로그\s*태그[^\n]*\n+([^\n]+)/);
        if (m) {
          copyToClipboard(m[1].trim(), '🏷️ 네이버 블로그 태그 30개가 복사되었습니다!');
        } else {
          alert('태그를 찾을 수 없습니다.');
        }
      }
    }

    function copyCurrentApp() {
      if (currentContent && currentContent.app_md) {
        copyToClipboard(currentContent.app_md, '📱 앱 게시판 텍스트가 복사되었습니다!');
      }
    }

    window.onload = loadCampaigns;
  </script>
</body>
</html>
"""

def simple_markdown_to_html(md_text):
    """마크다운을 보기 좋은 블로그 HTML로 변환"""
    if not md_text:
        return ""
    
    html = []
    lines = md_text.splitlines()
    in_table = False
    table_rows = []

    for line in lines:
        line_s = line.strip()

        # 테이블 처리
        if line_s.startswith("|") and line_s.endswith("|"):
            if "---" in line_s:
                continue
            cols = [c.strip() for c in line_s.strip("|").split("|")]
            table_rows.append(cols)
            in_table = True
            continue
        else:
            if in_table:
                html.append("<table>")
                for r_idx, row in enumerate(table_rows):
                    tag = "th" if r_idx == 0 else "td"
                    html.append("<tr>" + "".join([f"<{tag}>{c}</{tag}>" for c in row]) + "</tr>")
                html.append("</table>")
                in_table = False
                table_rows = []

        if not line_s:
            continue

        if line_s.startswith("# "):
            html.append(f"<h1>{line_s[2:]}</h1>")
        elif line_s.startswith("## "):
            html.append(f"<h2>{line_s[3:]}</h2>")
        elif line_s.startswith("### "):
            html.append(f"<h3>{line_s[4:]}</h3>")
        elif line_s.startswith(">"):
            html.append(f"<blockquote>{line_s.lstrip('> ')}</blockquote>")
        elif line_s.startswith("!["):
            m = re.search(r"!\[(.*?)\]\((.*?)\)", line_s)
            desc = m.group(1) if m else "이미지"
            html.append(f"<div class='img-placeholder'>🖼️ <b>{desc}</b> (카드뉴스 이미지 업로드 위치)</div>")
        elif line_s.startswith("- ") or line_s.startswith("* "):
            html.append(f"<p style='margin-left: 16px;'>• {line_s[2:]}</p>")
        else:
            formatted = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line_s)
            html.append(f"<p>{formatted}</p>")

    if in_table:
        html.append("<table>")
        for r_idx, row in enumerate(table_rows):
            tag = "th" if r_idx == 0 else "td"
            html.append("<tr>" + "".join([f"<{tag}>{c}</{tag}>" for c in row]) + "</tr>")
        html.append("</table>")

    return "\n".join(html)

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
            return

        if parsed.path == "/api/campaigns":
            all_c = get_all_campaigns()
            data = []
            for c in all_c:
                data.append({
                    "category": c["category"],
                    "folder_name": c["folder_name"]
                })
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            return

        if parsed.path == "/api/content":
            qs = urllib.parse.parse_qs(parsed.query)
            folder = qs.get("folder", [""])[0]
            
            blog_path = os.path.join(REPO_OUTPUT, folder, "01_블로그.md")
            app_path = os.path.join(REPO_OUTPUT, folder, "02_앱게시판.md")

            blog_md = ""
            app_md = ""
            if os.path.exists(blog_path):
                with open(blog_path, "r", encoding="utf-8") as fp:
                    blog_md = fp.read()
            if os.path.exists(app_path):
                with open(app_path, "r", encoding="utf-8") as fp:
                    app_md = fp.read()

            blog_html = simple_markdown_to_html(blog_md)

            res = {
                "folder": folder,
                "blog_md": blog_md,
                "app_md": app_md,
                "blog_html": blog_html
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            return

        self.send_error(404, "Not Found")

def run_server(port=PORT):
    server = socketserver.TCPServer(("", port), DashboardHandler)
    print(f"🌐 [대시보드 실행 완료] http://localhost:{port}")
    print("   브라우저에서 접속하여 블로그 및 앱 게시판을 확인하고 원클릭 복사할 수 있습니다.")
    server.serve_forever()

if __name__ == "__main__":
    import sys
    p = PORT
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        p = int(sys.argv[1])
    run_server(p)
