# ⚡ DESSERT 마케팅 → 블로그 & 앱 게시판 자동 배선 파이프라인 아키텍처

> **문서 보관 경로**: `/Users/name/cursor/app/docs/PIPELINE_ARCHITECTURE.md`  
> **마케팅 소스**: `/Users/name/Desktop/Cluade/DESSERT`  
> **배선 타깃**: `/Users/name/cursor/app/output/blog/` 및 GitHub Pages 웹 대시보드

---

## 1. 파이프라인 전체 흐름도 (End-to-End Workflow)

```
[마케팅 기획 소스 (/Desktop/Cluade/DESSERT)]
 ├── card_news_svg/ (트랙 A 시리즈: 00-기획서.md + SVG/PNG 5장)
 └── 단일 카드뉴스/ (트랙 B 단일: 00-기획안.md + 실사 배경 3장)
        │
        ▼ (자동 감지: sync_marketing_to_blog.py --watch 또는 CLI)
[파이프라인 변환 엔진 (/cursor/app/scripts)]
 ├── blog_generator.py
 │    ├── 팩트체크 검증 표 및 연구 출처 (식약처/WHO/학술DB)
 │    ├── SEO 키워드 전략 (메인 키워드 + 연관 키워드 8종)
 │    ├── 제목 후보 3종 (A 후킹형 / B 질문반전형 / C 숫자정보형)
 │    ├── 카드뉴스 슬라이드 이미지 배치 및 설명 단락
 │    ├── 2,000자 이상 심층 해설 (가설 및 캡션 기반 영양 메커니즘 분석)
 │    ├── 다이어터 생존 원칙 / 실천 가이드 박스
 │    ├── 네이버 블로그 태그 30개 자동 생성
 │    └── 서비스 인바운드 CTA (팩트스위트 & 외식생존기 판독기 링크)
 │
 └── app_board_generator.py
      ├── 앱 커뮤니티용 클린 텍스트 (이모지 100% 제거, 마크다운 볼드 제거)
      ├── 핵심 요약 및 체크리스트 (□ 형태)
      ├── 순수 본문 (1,000자 내외의 가독성 높은 산문)
      └── 앱 게시판용 핵심 태그 4개
        │
        ▼ (자동 배선 및 배포 타깃)
 ├── 1. 로컬 저장소 아카이브: `app/output/blog/<folder>/`
 │    ├── 01_블로그.md (네이버/티스토리 마크다운)
 │    └── 02_앱게시판.md (앱 커뮤니티 클린 텍스트)
 ├── 2. DESSERT 원본 폴더 동기화:
 │    ├── `card_news_svg/<folder>/blog_post.md` & `blog_post_naver.html`
 │    └── `단일 카드뉴스/<folder>/blog_post.md` & `blog_post_naver.html`
 ├── 3. macOS 클립보드 원클릭 복사: `pbcopy` 연동 (`--copy-blog`, `--copy-app`, `--copy-tags`)
 ├── 4. 로컬 웹 대시보드: `preview_server.py` (`http://localhost:8766`)
 └── 5. GitHub Pages 정적 웹 배포: `index.html` (`https://jihyetwo.github.io/app_dessert/`)
```

---

## 2. 변환 규격 명세

### 1) 네이버 블로그 (`01_블로그.md`)
- **글자 수**: 2,000~2,500자 이상의 고품질 롱폼 정보성 콘텐츠
- **구조**:
  1. 사실 검증 표 (식약처 영양 DB, WHO 지침, 논문 출처)
  2. SEO 타겟 키워드 및 검색의도 분석
  3. 제목 3종 후보 (클릭률 높은 질문·반전형 기본 채택)
  4. 도입부: 다이어터들이 일상에서 겪는 착각과 공감대 형성
  5. 슬라이드별 본문 전개: 카드뉴스 이미지 + 심층 해설
  6. 실패 없는 다이어터 현실 생존 원칙 박스
  7. 신규 웹 서비스 (팩트스위트 / 외식생존기) 인바운드 CTA
  8. 네이버 블로그 태그 30개

### 2) 앱 게시판 (`02_앱게시판.md`)
- **타겟**: 인앱 커뮤니티, 식단 게시판, 노션 공유용
- **특징**:
  - 이모지 전면 제거 (순수 텍스트 가독성 확보)
  - 마크다운 볼드(`**`) 제거, 깔끔한 글머리 기호 사용
  - 1,000자 내외로 핵심만 빠르게 파악 가능하도록 압축
  - 핵심 태그 4개 부여

---

## 3. 실행 명령어 요약

```bash
# 전체 캠페인 현황 확인
python3 scripts/sync_marketing_to_blog.py --status

# 모든 캠페인 일괄 동기화 (Track A + Track B)
python3 scripts/sync_marketing_to_blog.py --sync-all

# 특정 캠페인 동기화
python3 scripts/sync_marketing_to_blog.py --sync "dining_1_samgyeopsal"

# 실시간 감시 모드 (저쪽에서 새로 만들면 자동 배선!)
python3 scripts/sync_marketing_to_blog.py --watch

# macOS 클립보드 원클릭 복사
python3 scripts/sync_marketing_to_blog.py --copy-blog "dining_1_samgyeopsal"
python3 scripts/sync_marketing_to_blog.py --copy-tags "dining_1_samgyeopsal"
python3 scripts/sync_marketing_to_blog.py --copy-app "dining_1_samgyeopsal"

# 로컬 웹 대시보드 구동
python3 scripts/preview_server.py
```
