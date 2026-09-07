#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""app_board_generator.py
DESSERT(@dessrtj) 앱 게시판 표준 포맷(02_앱게시판.md) 자동 변환 엔진.

변환 원칙:
1. 제목: 30자 이내, 리듬감 있는 호기심 유발형
2. 설명: 블로그 본문 내용 충실 반영, 이모티콘 100% 제거, bold(**) 100% 제거,
         체크박스(□) 유지
3. 태그: 정확히 4개, 핵심 주제 위주, # 접두사 한 줄
4. 메타 제목: 검색 최적화 분리 각도
5. 메타 설명: 150자 내외 클릭 유도형
"""

import re
import unicodedata

def remove_emojis(s):
    """Hangul, English, 숫자, 특수문자, 체크박스(□)는 100% 보존하고 모든 이모티콘만 안전하게 제거"""
    res = []
    for ch in s:
        cp = ord(ch)
        cat = unicodedata.category(ch)
        
        # 1. 한글 음절, 자모, 호환자모 보존
        if (0xAC00 <= cp <= 0xD7AF) or (0x1100 <= cp <= 0x11FF) or (0x3130 <= cp <= 0x318F):
            res.append(ch)
            continue
            
        # 2. 기본 ASCII 영문, 숫자, 공백, 줄바꿈 보존
        if (0x20 <= cp <= 0x7E) or ch in "\n\r\t":
            res.append(ch)
            continue
            
        # 3. 체크박스(□) 보존
        if ch in "□■☑️☑":
            res.append("□")
            continue
            
        # 4. 한국어 문장부호 및 기호 보존
        if ch in "·•…※“”‘’「」『』【】（）()[]-~_!?:;.,/\\%&*+=<>":
            res.append(ch)
            continue
            
        # 5. 유니코드 이모지 제거
        if cat in ("So", "Sk", "Sm", "Cs"):
            continue
            
        # 6. 일반 문자/숫자/구두점/공백 보존
        if cat.startswith(("L", "N", "P", "Z")):
            res.append(ch)
            
    return "".join(res)

def remove_bold_formatting(text):
    """**bold** 또는 __bold__ 제거하고 내부 텍스트만 유지"""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    return text

def build_app_board(meta, blog_md=""):
    """앱 게시판 표준 포맷(02_앱게시판.md) 생성"""
    topic = meta["topic"] or meta["title"]
    keywords = meta["keywords"] or ["다이어트", "칼로리", "식단", "건강"]

    # 1. 제목 (30자 이내)
    title = f"{topic}: 다이어트 중 먹어도 될까?"
    if len(title) > 30:
        title = f"{topic} 칼로리 팩트체크"
    title = remove_emojis(title).strip()

    # 2. 본문 정제
    body_lines = []
    body_lines.append(f"{topic}에 대한 영양 팩트체크 정보입니다.")
    body_lines.append("")

    if meta.get("hypothesis"):
        cleaned_hypo = remove_bold_formatting(remove_emojis(meta["hypothesis"]))
        body_lines.append(cleaned_hypo)
        body_lines.append("")

    caption_text = meta.get("instagram_caption") or (meta.get("captions", {}).get("instagram", ""))
    if caption_text:
        cleaned_cap = remove_bold_formatting(remove_emojis(caption_text))
        for line in cleaned_cap.splitlines():
            line_s = line.strip()
            if not line_s.startswith("#") and "DM" not in line_s and "댓글" not in line_s:
                body_lines.append(line_s)
        body_lines.append("")

    rules = meta.get("rules", [])
    if rules:
        body_lines.append("[핵심 실천 수칙]")
        for r in rules:
            clean_r = remove_bold_formatting(remove_emojis(r))
            body_lines.append(f"□ {clean_r}")
        body_lines.append("")
    else:
        body_lines.append("[핵심 실천 수칙]")
        body_lines.append("□ 주 메뉴보다 곁들이(탄수화물, 당류) 섭취 조절")
        body_lines.append("□ 채소류 먼저 섭취하여 혈당 상승 완충")
        body_lines.append("□ 무설탕 표기 이면의 원재료 성분 확인")
        body_lines.append("")

    body_lines.append("본 정보는 공인 영양 데이터를 기반으로 한 참고용 가이드입니다.")
    full_description = "\n".join(body_lines).strip()

    # 3. 태그 정확히 4개
    clean_kws = [remove_emojis(k).strip() for k in keywords if k]
    clean_kws = [k for k in clean_kws if k and len(k) > 1]
    tags = clean_kws[:4]
    while len(tags) < 4:
        defaults = ["다이어트", "식단관리", "칼로리", "건강정보"]
        for d in defaults:
            if d not in tags:
                tags.append(d)
                break

    tags_str = " ".join(["#" + t for t in tags[:4]])

    # 4. 메타 제목 & 메타 설명
    meta_title = f"{topic} 영양 성분 및 다이어트 생존 가이드"
    meta_desc = f"{topic} 섭취 시 주의해야 할 숨은 칼로리와 당류 팩트를 확인하세요. 실패 없는 다이어트 식단 실천 수칙 4가지 정리."

    out = []
    out.append(f"# [앱게시판] {title}\n")
    out.append("## 1. 게시판 제목\n")
    out.append(f"{title}\n")
    out.append("## 2. 게시판 본문 설명\n")
    out.append(f"{full_description}\n")
    out.append("## 3. 앱 태그 (정확히 4개)\n")
    out.append(f"{tags_str}\n")
    out.append("## 4. 메타 정보 (검색용)\n")
    out.append(f"- **메타 제목:** {meta_title}")
    out.append(f"- **메타 설명:** {meta_desc}\n")

    return "\n".join(out)
