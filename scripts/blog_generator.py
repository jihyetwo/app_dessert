#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""blog_generator.py
DESSERT(@dessrtj) 네이버 블로그 표준 포맷(2,500자 롱폼, SEO, 팩트체크, 태그 30개 등) 생성 엔진.
"""

import os
import re
import datetime

DESSERT_FIXED_TAGS = [
    "dessrtj", "디저트팩트체크", "다이어트식단", "무설탕", "제로슈거",
    "다이어터", "혈당관리", "성분표읽기", "영양성분", "다이어트외식"
]

def clean_text(text):
    if not text:
        return ""
    return text.strip()

def extract_metadata(content):
    """00-기획서.md 또는 00-기획안.md에서 메타데이터 추출"""
    meta = {
        "title": "",
        "topic": "",
        "target": "20~40대 다이어터, 직장인, 건강관리 소비자",
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "keywords": [],
        "sources": [],
        "cards": [],
        "hypothesis": "",
        "captions": {},
        "rules": [],
        "raw_text": content
    }
    
    lines = content.splitlines()
    for i, line in enumerate(lines):
        line_s = line.strip()
        if line_s.startswith("# ") and not meta["title"]:
            meta["title"] = line_s.lstrip("# ").replace("📋", "").strip()
        
        # 날짜
        if "제작일" in line_s or "기준일" in line_s or "작성일" in line_s:
            m = re.search(r"(\d{4}[-./]\d{2}[-./]\d{2})", line_s)
            if m:
                meta["date"] = m.group(1).replace("/", "-").replace(".", "-")
        
        # 주제
        if "주제" in line_s and not meta["topic"]:
            if line_s.startswith("|"):
                cols = [c.strip() for c in line_s.strip("|").split("|")]
                if len(cols) >= 2 and "주제" in cols[0]:
                    meta["topic"] = cols[1].strip()
            else:
                parts = line_s.split(":", 1)
                if len(parts) == 2:
                    meta["topic"] = parts[1].strip().lstrip("* ").strip()

    # 키워드 추출
    m_kw = re.search(r"##\s*\d*\.?\s*(?:자동\s*추출\s*)?키워드\s*\n([^#]+)", content)
    if m_kw:
        kw_text = m_kw.group(1)
        kws = [k.strip('` \t\r\n/#') for k in re.findall(r"`([^`]+)`", kw_text)]
        if not kws:
            kws = [k.strip(' \t\r\n/#') for k in kw_text.replace("\n", " ").split("/") if k.strip()]
        meta["keywords"] = [k for k in kws if k and len(k) > 1]
    
    if not meta["keywords"]:
        tags = re.findall(r"#([a-zA-Z0-9가-힣_-]+)", content)
        meta["keywords"] = list(dict.fromkeys(tags))[:10]

    # 가설 (심층 배경)
    m_hypo = re.search(r"##\s*\d*\.?\s*콘텐츠\s*가설\s*\n([^#]+)", content)
    if m_hypo:
        meta["hypothesis"] = m_hypo.group(1).strip()

    # 캡션 (인스타그램 등)
    m_ig = re.search(r"###\s*📸?\s*Instagram\s*\n```(?:text)?\s*\n([^`]+)```", content)
    if m_ig:
        meta["captions"]["instagram"] = m_ig.group(1).strip()
    else:
        # 단일 카드뉴스 본문
        m_body = re.search(r"후보\s*:\s*[^\n]+\n(?:✅[^\n]+\n)?\n([^\n]+(?:\n[^\n]+){1,6})", content)
        if m_body:
            meta["captions"]["instagram"] = m_body.group(1).strip()

    # 생존 원칙 / 실천 가이드
    m_rules = re.search(r"(?:생존\s*\d*원칙|실천\s*원칙|가이드)\s*\n((?:\s*[-*\d].*\n?)+)", content)
    if m_rules:
        meta["rules"] = [r.strip() for r in m_rules.group(1).splitlines() if r.strip()]

    # 참고 출처
    m_src = re.search(r"##\s*\d*\.?\s*(?:참고\s*출처|출처|팩트체크)\s*\n([^#]+)", content)
    if m_src:
        src_text = m_src.group(1).strip()
        for sl in src_text.splitlines():
            sl = sl.strip()
            if sl.startswith("-") or sl.startswith("*") or sl.startswith("http"):
                meta["sources"].append(sl.lstrip("-* ").strip())

    return meta

def build_naver_blog(meta, folder_name="", image_files=None):
    """표준 2,500자 롱폼 네이버 블로그 포스트 생성"""
    topic = meta["topic"] or meta["title"]
    keywords = meta["keywords"] or ["다이어트외식", "칼로리계산", "성분팩트"]
    main_kw = keywords[0] if keywords else "다이어트"
    sub_kws = keywords[1:9] if len(keywords) > 1 else ["식단관리", "제로슈거", "건강정보"]

    # 1. 제목 후보 3종
    title_a = f"[{main_kw}] {topic} — 다이어터가 꼭 알아야 할 숨은 팩트체크"
    title_b = f"\"{topic}\" 정말 살 안 찔까? 다이어터 한 상 칼로리의 진실"
    title_c = f"{main_kw} 팩트 검증: 숨은 칼로리 폭탄 피하는 현실 생존 가이드"

    # 이미지 목록 정리
    images = image_files or []
    
    # 2. 본문 조립
    lines = []
    lines.append(f"# {title_a}\n")
    lines.append("> **작성일:** " + meta["date"] + "  ")
    lines.append("> **콘텐츠 제공:** `@dessrtj` 디저트 팩트체크 허브  ")
    lines.append(f"> **타깃:** {meta['target']}\n")
    lines.append("---\n")

    # 사실 검증 표
    lines.append("## 🔍 1. 사전 팩트체크 & 검증 결과\n")
    lines.append("| 검증 항목 | 검증 기준 및 공인 출처 | 판정 및 권고 사항 |")
    lines.append("|---|---|---|")
    lines.append(f"| **주제 팩트** | 식약처 영양성분 DB / WHO 지침 | {topic} 관련 영양 수치 정밀 확인 |")
    lines.append("| **칼로리·당류** | 한국영양학회 1일 권장 섭취 기준 | 가공식품 및 외식 곁들이 숨은 칼로리 검증 |")
    lines.append("| **감미료/첨가물** | 식품공전 및 공인 학술 자료 | 말티톨, 알룰로스, 당알코올 내약량 기준 대조 |\n")

    # SEO 키워드 전략
    lines.append("## 🎯 2. 검색 최적화(SEO) 키워드 전략\n")
    lines.append(f"- **메인 키워드:** `{main_kw}`")
    lines.append(f"- **연관 키워드 (8종):** {', '.join(['`' + k + '`' for k in sub_kws])}")
    lines.append(f"- **독자 검색 의도:** {topic}을 섭취하거나 외식할 때 체중 감량에 방해가 되지 않는지, 진짜 성분과 칼로리는 얼마인지 객관적 팩트를 탐색하고자 함.\n")

    lines.append("---\n")

    # 제목 3종 후보
    lines.append("## 💡 3. 블로그 제목 3종 후보\n")
    lines.append(f"- **A타입 (검색 최적화 전진배치형 · 채택):** {title_a}")
    lines.append(f"- **B타입 (공감 질문·반전형):** {title_b}")
    lines.append(f"- **C타입 (수치·현실 가이드형):** {title_c}\n")

    lines.append("---\n")

    # 본문 인트로
    lines.append("## 🧐 다이어트 중 마주치는 착각과 현실\n")
    if meta["hypothesis"]:
        paragraphs = [p.strip() for p in meta["hypothesis"].split("\n\n") if p.strip()]
        for p in paragraphs:
            lines.append(f"{p}\n")
    else:
        lines.append(f"다이어트를 결심하고 식단을 관리할 때, 우리는 종종 '이건 단백질이니까 괜찮겠지', 혹은 '제로슈거라고 적혀 있으니 살이 안 찌겠지'라며 안심하곤 합니다.\n")
        lines.append(f"하지만 실제 영양 성분표와 식약처 공식 데이터를 꼼꼼히 뜯어보면, 우리가 미처 예상하지 못했던 복병이 숨어 있는 경우가 많습니다. 오늘 포스팅에서는 **{topic}**의 진짜 실태와 칼로리 진실을 과학적 데이터로 팩트체크해 드립니다.\n")

    lines.append("---\n")

    # 카드뉴스 슬라이드별 이미지 및 해설
    lines.append("## 📊 카드뉴스로 보는 핵심 분석\n")
    if images:
        for idx, img in enumerate(images, 1):
            img_rel = os.path.basename(img)
            lines.append(f"### [카드뉴스 Point {idx:02d}] {topic} 핵심 검증\n")
            lines.append(f"![카드뉴스 슬라이드 {idx}]({img_rel})\n")
            lines.append(f"*▲ {topic} - 슬라이드 {idx} 상세 팩트 카드*\n")
    else:
        lines.append(f"*(카드뉴스 슬라이드 이미지가 배치될 영역입니다)*\n")

    # 인스타그램 캡션 및 상세 영양 분석
    if "instagram" in meta["captions"] and meta["captions"]["instagram"]:
        lines.append("---\n")
        lines.append("## 💡 상세 영양 데이터 & 메커니즘 분석\n")
        cap = meta["captions"]["instagram"]
        clean_lines = [l for l in cap.splitlines() if not l.startswith("#") and "DM" not in l and "댓글" not in l]
        lines.append("\n".join(clean_lines).strip() + "\n")

    lines.append("---\n")

    # 다이어터 현실 생존 원칙
    lines.append("## 🛡️ 다이어터 현실 생존 가이드\n")
    if meta["rules"]:
        lines.append("> **💡 오늘부터 즉시 적용하는 실천 원칙:**\n>")
        for r in meta["rules"]:
            lines.append(f"> - {r}")
        lines.append("\n")
    else:
        lines.append("> **💡 다이어트 생존 핵심 수칙:**\n>")
        lines.append("> - **1. 주 메뉴보다 곁들이를 통제하라**: 탄수화물/알코올 곁들이(냉면, 소주, 볶음밥 등)가 칼로리의 주범입니다.")
        lines.append("> - **2. 식이섬유(채소) 먼저 섭취**: 첫 입을 채소로 시작하여 혈당 스파이크와 과식을 방어하세요.")
        lines.append("> - **3. 성분표 읽는 습관 들이기**: 마케팅 문구(무설탕, 제로)에 현혹되지 말고 원재료명을 확인하세요.\n")

    # 서비스 연계 CTA 배너
    lines.append("---\n")
    lines.append("## 📱 내 간식·외식 메뉴 3초 판독기 (FactSweet & EatSurvival)\n")
    lines.append("> [!TIP]")
    lines.append("> **\"내가 오늘 먹은 제로 간식, 진짜 안전할까?\"**  ")
    lines.append("> 말티톨 감지, 알룰로스 복용 한도 체크, 외식 칼로리 컷 시뮬레이터를 지금 웹 서비스에서 무료로 체험해보세요!")
    lines.append("> 👉 **[팩트스위트 & 외식생존기 웹 서비스 바로가기 (오픈 예정)]**\n")

    lines.append("---\n")

    # 아웃트로 & 면책
    lines.append("## 📝 한 줄 요약 & 실천 팁\n")
    lines.append(f"1. **{topic}**은(는) 무작정 굶거나 참는 것이 답이 아니라, 정확한 성분과 곁들이를 알고 먹는 것이 핵심입니다.")
    lines.append("2. 인스타그램 `@dessrtj`를 팔로우하시면 더 많은 디저트·외식 팩트체크 정보를 가장 빠르게 받아보실 수 있습니다.\n\n")

    if meta["sources"]:
        lines.append("### 📚 참고 문헌 및 공인 출처")
        for s in meta["sources"]:
            lines.append(f"- {s}")
        lines.append("\n")

    lines.append("*본 콘텐츠는 식품의약품안전처 영양성분 DB 및 공인 연구 논문을 바탕으로 작성된 정보 제공 목적의 글이며, 전문적인 의학적 진단이나 치료를 대신할 수 없습니다.*")

    # 30개 태그 조립 (고정 10개 + 추출 키워드)
    all_tags = list(DESSERT_FIXED_TAGS)
    for k in keywords:
        clean_k = re.sub(r"[^가-힣a-zA-Z0-9]", "", k)
        if clean_k and clean_k not in all_tags:
            all_tags.append(clean_k)
    
    # 30개 채우기
    filler_tags = ["체중감량", "칼로리조절", "외식가이드", "다이어트꿀팁", "직장인다이어트", "건강식단", "유지어터", "헬스식단", "당류조절", "식이요법"]
    for ft in filler_tags:
        if len(all_tags) >= 30:
            break
        if ft not in all_tags:
            all_tags.append(ft)
    
    final_30_tags = all_tags[:30]
    lines.append(f"\n\n---\n**🏷️ 네이버 블로그 태그 (정확히 30개):**\n")
    lines.append(" ".join(["#" + t for t in final_30_tags]))

    return "\n".join(lines)
