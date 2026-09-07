#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_static_site.py
GitHub Pages 배포용 정적 웹 대시보드(index.html) 빌드 스크립트.
모든 블로그/앱게시판 렌더링 데이터를 단일 index.html에 임베딩하여 서버 없이 브라우저나 GitHub Pages에서 완벽 구동.
"""

import os
import sys
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from preview_server import simple_markdown_to_html
from sync_marketing_to_blog import get_all_campaigns, REPO_OUTPUT, APP_ROOT

def build_static_html(output_file=None):
    if output_file is None:
        output_file = os.path.join(APP_ROOT, "index.html")

    campaigns = get_all_campaigns()
    data = []

    for c in campaigns:
        folder = c["folder_name"]
        blog_path = os.path.join(REPO_OUTPUT, folder, "01_블로그.md")
        app_path = os.path.join(REPO_OUTPUT, folder, "02_앱게시판.md")
        if os.path.exists(blog_path):
            with open(blog_path, "r", encoding="utf-8") as fp:
                blog_md = fp.read()
            app_md = ""
            if os.path.exists(app_path):
                with open(app_path, "r", encoding="utf-8") as fp:
                    app_md = fp.read()
            blog_html = simple_markdown_to_html(blog_md)
            data.append({
                "category": c["category"],
                "folder_name": folder,
                "data": {
                    "folder": folder,
                    "blog_md": blog_md,
                    "app_md": app_md,
                    "blog_html": blog_html
                }
            })

    data_json = json.dumps(data, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DESSERT 디저트 팩트체크 · 블로그 & 앱게시판 대시보드</title>
  <meta name="description" content="다이어터와 소비자를 위한 무설탕·제로 감미료 팩트체크 및 외식 칼로리 생존 가이드 블로그 대시보드">
  <meta name="keywords" content="디저트팩트체크, 말티톨, 알룰로스, 에리스리톨, 삼겹살칼로리, 회식다이어트, 외식다이어트, 제로슈거, dessrtj">
  
  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:title" content="DESSERT 디저트 팩트체크 · 블로그 & 앱게시판 대시보드">
  <meta property="og:description" content="무설탕 마케팅의 진실과 외식 칼로리 생존 5원칙 완벽 가이드">
  <meta property="og:url" content="https://jihyetwo.github.io/app_dessert/">
  <meta name="twitter:card" content="summary_large_image">

  <style>
    :root {{
      --naver-green: #03C75A;
      --naver-dark: #029f48;
      --dessert-amber: #d97706;
      --dessert-red: #ef4444;
      --bg: #F8F9FA;
      --card-bg: #FFFFFF;
      --text: #1E293B;
      --text-muted: #64748B;
      --border: #E2E8F0;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Apple SD Gothic Neo", sans-serif; }}
    body {{ background: var(--bg); color: var(--text); display: flex; height: 100vh; overflow: hidden; }}
    
    /* 사이드바 */
    .sidebar {{ width: 340px; background: #fff; border-right: 1px solid var(--border); display: flex; flex-direction: column; flex-shrink: 0; }}
    .sidebar-header {{ padding: 18px 20px; border-bottom: 1px solid var(--border); background: #fafafa; }}
    .sidebar-header h1 {{ font-size: 16px; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px; }}
    .sidebar-header p {{ font-size: 12px; color: var(--text-muted); margin-top: 4px; }}
    .search-box {{ padding: 12px 16px; border-bottom: 1px solid var(--border); }}
    .search-input {{ width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; outline: none; }}
    .search-input:focus {{ border-color: var(--dessert-amber); }}
    .campaign-list {{ flex: 1; overflow-y: auto; list-style: none; }}
    .campaign-item {{ padding: 14px 16px; border-bottom: 1px solid #f1f5f9; cursor: pointer; transition: background 0.15s; }}
    .campaign-item:hover {{ background: #f8fafc; }}
    .campaign-item.active {{ background: #fffbeb; border-left: 4px solid var(--dessert-amber); }}
    .campaign-cat {{ font-size: 11px; font-weight: 600; color: var(--text-muted); }}
    .campaign-name {{ font-size: 14px; font-weight: 600; color: #1e293b; margin-top: 2px; word-break: break-all; }}
    .campaign-badges {{ display: flex; gap: 6px; margin-top: 6px; }}
    .badge {{ font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: 600; }}
    .badge-blog {{ background: #dcfce7; color: #15803d; }}
    .badge-app {{ background: #e0f2fe; color: #0369a1; }}
    
    /* 메인 영역 */
    .main {{ flex: 1; display: flex; flex-direction: column; overflow: hidden; }}
    .top-bar {{ height: 64px; background: #fff; border-bottom: 1px solid var(--border); padding: 0 24px; display: flex; align-items: center; justify-content: space-between; }}
    .top-title {{ font-size: 16px; font-weight: 700; }}
    .top-actions {{ display: flex; gap: 8px; }}
    .btn {{ padding: 8px 14px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; border: none; transition: 0.15s; display: inline-flex; align-items: center; gap: 6px; }}
    .btn-naver {{ background: var(--naver-green); color: #fff; }}
    .btn-naver:hover {{ background: var(--naver-dark); }}
    .btn-amber {{ background: var(--dessert-amber); color: #fff; }}
    .btn-amber:hover {{ background: #b45309; }}
    .btn-secondary {{ background: #f1f5f9; color: #334155; }}
    .btn-secondary:hover {{ background: #e2e8f0; }}
    
    .tab-bar {{ display: flex; background: #fff; border-bottom: 1px solid var(--border); padding: 0 24px; gap: 20px; }}
    .tab {{ padding: 12px 0; font-size: 14px; font-weight: 600; color: var(--text-muted); cursor: pointer; border-bottom: 2px solid transparent; transition: 0.15s; }}
    .tab.active {{ color: var(--naver-green); border-bottom-color: var(--naver-green); }}
    .content-area {{ flex: 1; overflow-y: auto; padding: 32px; display: flex; justify-content: center; }}
    .viewer {{ width: 100%; max-width: 780px; background: #fff; padding: 40px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid var(--border); }}
    
    /* 네이버 블로그 스마트에디터 스타일 */
    .blog-view h1 {{ font-size: 26px; font-weight: 800; margin-bottom: 20px; line-height: 1.4; color: #111; border-bottom: 2px solid #111; padding-bottom: 12px; }}
    .blog-view h2 {{ font-size: 20px; font-weight: 700; margin-top: 32px; margin-bottom: 14px; color: #d97706; border-left: 4px solid #d97706; padding-left: 10px; }}
    .blog-view h3 {{ font-size: 17px; font-weight: 700; margin-top: 20px; margin-bottom: 10px; color: #1e293b; }}
    .blog-view p {{ font-size: 15px; line-height: 1.8; margin-bottom: 14px; color: #222; word-break: keep-all; }}
    .blog-view table {{ width: 100%; border-collapse: collapse; margin: 18px 0; font-size: 14px; }}
    .blog-view th, .blog-view td {{ border: 1px solid #e2e8f0; padding: 10px 14px; text-align: left; }}
    .blog-view th {{ background: #f8fafc; font-weight: 600; }}
    .blog-view blockquote {{ background: #fffbeb; border-left: 4px solid #d97706; padding: 14px 18px; margin: 18px 0; border-radius: 6px; font-size: 14px; }}
    .blog-view .img-placeholder {{ background: #f1f5f9; border: 2px dashed #cbd5e1; border-radius: 8px; padding: 24px; text-align: center; color: #64748b; font-size: 14px; margin: 20px 0; }}
    
    /* 앱 게시판 스타일 */
    .app-view {{ white-space: pre-wrap; font-family: monospace; font-size: 13px; line-height: 1.7; color: #334155; }}
    .raw-view {{ white-space: pre-wrap; font-family: monospace; font-size: 13px; line-height: 1.6; color: #1e293b; }}
    
    .toast {{ position: fixed; bottom: 24px; right: 24px; background: #0f172a; color: #fff; padding: 12px 20px; border-radius: 8px; font-size: 13px; opacity: 0; transition: opacity 0.2s; pointer-events: none; z-index: 100; }}
    .toast.show {{ opacity: 1; }}
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
      <!-- 정적 임베딩 -->
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
    const EMBEDDED_DATA = {data_json};
    let allCampaigns = EMBEDDED_DATA.map(d => ({{ category: d.category, folder_name: d.folder_name }}));
    let currentCampaign = null;
    let currentContent = null;
    let currentTab = 'blog';

    function init() {{
      renderList(allCampaigns);
      if (allCampaigns.length > 0) {{
        selectCampaign(allCampaigns[0].folder_name);
      }}
    }}

    function renderList(list) {{
      const ul = document.getElementById('campaign-list');
      ul.innerHTML = '';
      list.forEach(c => {{
        const li = document.createElement('li');
        li.className = 'campaign-item' + (currentCampaign === c.folder_name ? ' active' : '');
        li.onclick = () => selectCampaign(c.folder_name);
        li.innerHTML = `
          <div class="campaign-cat">${{c.category}}</div>
          <div class="campaign-name">${{c.folder_name}}</div>
          <div class="campaign-badges">
            <span class="badge badge-blog">블로그 2,500자</span>
            <span class="badge badge-app">앱게시판</span>
          </div>
        `;
        ul.appendChild(li);
      }});
    }}

    function filterCampaigns() {{
      const q = document.getElementById('search').value.toLowerCase();
      const filtered = allCampaigns.filter(c => c.folder_name.toLowerCase().includes(q) || c.category.toLowerCase().includes(q));
      renderList(filtered);
    }}

    function selectCampaign(folder) {{
      currentCampaign = folder;
      document.querySelectorAll('.campaign-item').forEach(el => {{
        el.classList.toggle('active', el.querySelector('.campaign-name').innerText === folder);
      }});
      document.getElementById('current-title').innerText = folder;
      
      const found = EMBEDDED_DATA.find(d => d.folder_name === folder);
      if (found) {{
        currentContent = found.data;
        renderViewer();
      }}
    }}

    function setTab(tab) {{
      currentTab = tab;
      document.querySelectorAll('.tab').forEach((el, idx) => {{
        el.classList.toggle('active', (tab === 'blog' && idx === 0) || (tab === 'app' && idx === 1) || (tab === 'raw' && idx === 2));
      }});
      renderViewer();
    }}

    function renderViewer() {{
      if (!currentContent) return;
      const v = document.getElementById('viewer');
      if (currentTab === 'blog') {{
        v.className = 'viewer blog-view';
        v.innerHTML = currentContent.blog_html || '<p>내용이 없습니다.</p>';
      }} else if (currentTab === 'app') {{
        v.className = 'viewer app-view';
        v.innerText = currentContent.app_md || '내용이 없습니다.';
      }} else {{
        v.className = 'viewer raw-view';
        v.innerText = currentContent.blog_md || '내용이 없습니다.';
      }}
    }}

    function copyToClipboard(text, msg) {{
      navigator.clipboard.writeText(text).then(() => {{
        const toast = document.getElementById('toast');
        toast.innerText = msg;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 2000);
      }}).catch(err => {{
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        const toast = document.getElementById('toast');
        toast.innerText = msg;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 2000);
      }});
    }}

    function copyCurrentBlog() {{
      if (currentContent && currentContent.blog_md) {{
        copyToClipboard(currentContent.blog_md, '📋 네이버 블로그 원고가 복사되었습니다!');
      }}
    }}

    function copyCurrentTags() {{
      if (currentContent && currentContent.blog_md) {{
        const m = currentContent.blog_md.match(/🏷️\s*네이버\s*블로그\s*태그[^\n]*\n+([^\n]+)/);
        if (m) {{
          copyToClipboard(m[1].trim(), '🏷️ 네이버 블로그 태그 30개가 복사되었습니다!');
        }} else {{
          alert('태그를 찾을 수 없습니다.');
        }}
      }}
    }}

    function copyCurrentApp() {{
      if (currentContent && currentContent.app_md) {{
        copyToClipboard(currentContent.app_md, '📱 앱 게시판 텍스트가 복사되었습니다!');
      }}
    }}

    window.onload = init;
  </script>
</body>
</html>
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ 정적 웹 대시보드 빌드 완료: {output_file} ({len(data)}개 캠페인 데이터 임베딩)")

if __name__ == "__main__":
    build_static_html()
