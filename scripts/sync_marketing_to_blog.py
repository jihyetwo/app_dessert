#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync_marketing_to_blog.py
DESSERT 마케팅 기획 소스(/Desktop/Cluade/DESSERT)에서
네이버 블로그(01_블로그.md) 및 앱게시판(02_앱게시판.md)으로 자동 변환·동기화하는 CLI 및 배선 도구.

사용법:
    python3 scripts/sync_marketing_to_blog.py --status
    python3 scripts/sync_marketing_to_blog.py --sync "dining_1_samgyeopsal"
    python3 scripts/sync_marketing_to_blog.py --sync-all
    python3 scripts/sync_marketing_to_blog.py --watch
    python3 scripts/sync_marketing_to_blog.py --copy-blog "dining_1_samgyeopsal"
    python3 scripts/sync_marketing_to_blog.py --copy-app "dining_1_samgyeopsal"
    python3 scripts/sync_marketing_to_blog.py --copy-tags "dining_1_samgyeopsal"
"""

import os
import sys
import glob
import time
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.dirname(SCRIPT_DIR)
DESSERT_ROOT = "/Users/name/Desktop/Cluade/DESSERT"
REPO_OUTPUT = os.path.join(APP_ROOT, "output", "blog")

sys.path.append(SCRIPT_DIR)
from blog_generator import extract_metadata, build_naver_blog
from app_board_generator import build_app_board
from build_static_site import build_static_html

def get_all_campaigns():
    """DESSERT 내의 모든 캠페인 폴더(트랙 A + 트랙 B) 스캔"""
    campaigns = []
    
    # 1. 트랙 A: card_news_svg
    svg_dir = os.path.join(DESSERT_ROOT, "card_news_svg")
    if os.path.exists(svg_dir):
        for entry in sorted(os.listdir(svg_dir)):
            full_p = os.path.join(svg_dir, entry)
            if os.path.isdir(full_p) and not entry.startswith("_") and not entry.startswith("."):
                campaigns.append({
                    "category": "시리즈_SVG(트랙A)",
                    "folder_name": entry,
                    "full_path": full_p
                })

    # 2. 트랙 B: 단일 카드뉴스 (하위 배치 폴더 포함 재귀 탐색)
    single_dir = os.path.join(DESSERT_ROOT, "단일 카드뉴스")
    if os.path.exists(single_dir):
        for root, dirs, files in os.walk(single_dir):
            if any(f in files for f in ["00-기획서.md", "00-기획안.md", "기획서.md"]):
                entry = os.path.basename(root)
                if not entry.startswith("_") and not entry.startswith("."):
                    campaigns.append({
                        "category": "단일_카드뉴스(트랙B)",
                        "folder_name": entry,
                        "full_path": root
                    })

    return campaigns

def find_plan_file(campaign_path):
    for cand in ["00-기획서.md", "00-기획안.md", "기획서.md"]:
        p = os.path.join(campaign_path, cand)
        if os.path.exists(p):
            return p
    return None

def find_images(campaign_path):
    png_dir = os.path.join(campaign_path, "png")
    if os.path.exists(png_dir):
        imgs = sorted(glob.glob(os.path.join(png_dir, "*.png")))
        if imgs:
            return imgs
    imgs = sorted(glob.glob(os.path.join(campaign_path, "*.png")))
    if imgs:
        return imgs
    return sorted(glob.glob(os.path.join(campaign_path, "slide_*.svg")))

def sync_single_campaign(campaign_info):
    folder = campaign_info["folder_name"]
    src_path = campaign_info["full_path"]
    
    plan_file = find_plan_file(src_path)
    if not plan_file:
        return False, "기획서 파일(00-기획서.md) 없음"

    with open(plan_file, "r", encoding="utf-8") as f:
        content = f.read()

    images = find_images(src_path)
    meta = extract_metadata(content)
    
    # 1. 블로그 포스트 생성
    blog_md = build_naver_blog(meta, folder_name=folder, image_files=images)
    
    # 2. 앱 게시판 텍스트 생성
    app_md = build_app_board(meta, blog_md=blog_md)

    # 3. 저장 (output/blog/<folder>/)
    out_dir = os.path.join(REPO_OUTPUT, folder)
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "01_블로그.md"), "w", encoding="utf-8") as f:
        f.write(blog_md)

    with open(os.path.join(out_dir, "02_앱게시판.md"), "w", encoding="utf-8") as f:
        f.write(app_md)

    return True, f"생성 완료 (이미지 {len(images)}개 연동)"

def show_status():
    campaigns = get_all_campaigns()
    print("\n" + "=" * 80)
    print(f"📊 DESSERT 마케팅 → 블로그 배선 현황 (총 {len(campaigns)}개 캠페인)")
    print("=" * 80)
    print(f"{'분류':<18} {'캠페인 폴더':<36} {'기획서':<8} {'블로그':<8} {'앱게시판':<8}")
    print("-" * 80)

    for c in campaigns:
        folder = c["folder_name"]
        plan_exists = "✅" if find_plan_file(c["full_path"]) else "❌"
        blog_exists = "✅" if os.path.exists(os.path.join(REPO_OUTPUT, folder, "01_블로그.md")) else "❌"
        app_exists = "✅" if os.path.exists(os.path.join(REPO_OUTPUT, folder, "02_앱게시판.md")) else "❌"
        print(f"{c['category']:<18} {folder:<36} {plan_exists:<8} {blog_exists:<8} {app_exists:<8}")

    print("=" * 80 + "\n")

def sync_all():
    campaigns = get_all_campaigns()
    print(f"🚀 총 {len(campaigns)}개 캠페인 일괄 동기화 시작...")
    success = 0
    for c in campaigns:
        ok, msg = sync_single_campaign(c)
        if ok:
            print(f"  ✅ {c['folder_name']}: {msg}")
            success += 1
        else:
            print(f"  ⚠️  {c['folder_name']}: {msg}")
    print(f"\n🎉 완료: {success}/{len(campaigns)}개 캠페인 동기화 완료!")
    build_static_html()

def sync_by_name(name_query):
    campaigns = get_all_campaigns()
    matched = [c for c in campaigns if name_query.lower() in c["folder_name"].lower()]
    if not matched:
        print(f"❌ '{name_query}'에 일치하는 캠페인을 찾을 수 없습니다.")
        return
    for c in matched:
        ok, msg = sync_single_campaign(c)
        status = "✅ 성공" if ok else "❌ 실패"
        print(f"{status}: {c['folder_name']} ({msg})")
    build_static_html()

def copy_to_clipboard(text):
    try:
        p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        p.communicate(text.encode("utf-8"))
        return True
    except Exception as e:
        print(f"클립보드 복사 실패: {e}")
        return False

def handle_copy(name_query, target_type):
    campaigns = get_all_campaigns()
    matched = [c for c in campaigns if name_query.lower() in c["folder_name"].lower()]
    if not matched:
        print(f"❌ '{name_query}'에 일치하는 캠페인을 찾을 수 없습니다.")
        return
    c = matched[0]
    folder = c["folder_name"]
    out_dir = os.path.join(REPO_OUTPUT, folder)
    
    if target_type == "blog":
        file_p = os.path.join(out_dir, "01_블로그.md")
        if not os.path.exists(file_p):
            sync_single_campaign(c)
        with open(file_p, "r", encoding="utf-8") as f:
            content = f.read()
        copy_to_clipboard(content)
        print(f"📋 '{folder}' 네이버 블로그 원고가 클립보드에 복사되었습니다! (Cmd + V로 붙여넣기)")

    elif target_type == "app":
        file_p = os.path.join(out_dir, "02_앱게시판.md")
        if not os.path.exists(file_p):
            sync_single_campaign(c)
        with open(file_p, "r", encoding="utf-8") as f:
            content = f.read()
        copy_to_clipboard(content)
        print(f"📋 '{folder}' 앱 게시판 텍스트가 클립보드에 복사되었습니다! (Cmd + V로 붙여넣기)")

    elif target_type == "tags":
        file_p = os.path.join(out_dir, "01_블로그.md")
        if not os.path.exists(file_p):
            sync_single_campaign(c)
        with open(file_p, "r", encoding="utf-8") as f:
            content = f.read()
        m = re.search(r"🏷️\s*네이버\s*블로그\s*태그[^\n]*\n+([^\n]+)", content)
        if m:
            tags = m.group(1).strip()
            copy_to_clipboard(tags)
            print(f"🏷️ '{folder}' 태그 30개가 클립보드에 복사되었습니다:\n{tags}")
        else:
            print("태그를 찾을 수 없습니다.")

def watch_mode():
    print(f"👀 실시간 감시 시작: {DESSERT_ROOT}")
    print("새로운 카드뉴스나 기획서 수정 시 자동으로 01_블로그.md 및 02_앱게시판.md를 생성합니다. (Ctrl+C로 종료)\n")
    last_mtimes = {}
    try:
        while True:
            for c in get_all_campaigns():
                plan_file = find_plan_file(c["full_path"])
                if plan_file:
                    mtime = os.path.getmtime(plan_file)
                    if plan_file not in last_mtimes:
                        last_mtimes[plan_file] = mtime
                    elif mtime > last_mtimes[plan_file]:
                        last_mtimes[plan_file] = mtime
                        print(f"🔔 변경 감지: {c['folder_name']}")
                        sync_single_campaign(c)
            time.sleep(3)
    except KeyboardInterrupt:
        print("\n감시 모드를 종료합니다.")

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or "--status" in args:
        show_status()
    elif "--sync-all" in args:
        sync_all()
    elif "--sync" in args and len(args) > 1:
        sync_by_name(args[args.index("--sync") + 1])
    elif "--copy-blog" in args and len(args) > 1:
        handle_copy(args[args.index("--copy-blog") + 1], "blog")
    elif "--copy-app" in args and len(args) > 1:
        handle_copy(args[args.index("--copy-app") + 1], "app")
    elif "--copy-tags" in args and len(args) > 1:
        handle_copy(args[args.index("--copy-tags") + 1], "tags")
    elif "--watch" in args:
        watch_mode()
    else:
        print(__doc__)
