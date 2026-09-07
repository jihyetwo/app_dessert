# 🍨 DessertApp: 인사이트 기반 프로덕트 & 마케팅-블로그 자동 배선 시스템

> **저장된 프로덕트 기획서**: [`docs/PRODUCT_SPECIFICATIONS.md`](docs/PRODUCT_SPECIFICATIONS.md)  
> **마케팅 소스 디렉터리**: `/Users/name/Desktop/Cluade/DESSERT`  
> **배선 아웃풋 디렉터리**: `output/blog/`  
> **웹 대시보드 (GitHub Pages)**: [https://jihyetwo.github.io/app_dessert/](https://jihyetwo.github.io/app_dessert/)

---

## 📌 1. 프로젝트 개요

본 프로젝트는 `/Users/name/Desktop/Cluade/DESSERT`(@dessrtj) 내에 축적된 20여 편의 팩트체크 기획서, 카드뉴스, 식약처/WHO 공인 영양 데이터, 다이어터 반응 분석 자료를 기반으로:
1. **다이어터와 소비자의 실제 결핍(Pain Points)을 해결하는 4대 신규 프로덕트 상세 설계**를 체계적으로 보관하고,
2. **마케팅 기획서가 만들어지면 네이버 블로그(2,500자 롱폼, SEO) 및 앱 게시판으로 즉시 올릴 수 있도록 자동 배선(Wiring)**하는 통합 시스템입니다.

---

## 🏛️ 2. 보관된 4대 프로덕트 상세 설계 (`docs/`)

자세한 데이터 스키마 및 사용자 흐름은 [`docs/PRODUCT_SPECIFICATIONS.md`](docs/PRODUCT_SPECIFICATIONS.md)에 저장되어 있습니다.

| 프로덕트명 | 핵심 가치 제안 (Value Proposition) | 핵심 기능 |
|---|---|---|
| **1. [FactSweet]**<br>제로·다이어트 식품 성분 판독기 | "내가 사먹은 제로 간식, 진짜 살 안 찔까? 혈당 올리는 가짜 제로를 3초 만에 판별" | • **말티톨 감지기**: 혈당 지수(GI) 유발 성분 경고<br>• **안전 신호등 (A/B/C)**: 안심(알룰로스/스테비아), 주의, 경고<br>• **클린 대체 식품 추천**: 동일 카테고리 내 안전한 제품 매칭 |
| **2. [EatSurvival]**<br>외식 시뮬레이터 & 생존 가이드 | "오늘 저녁 회식 삼겹살/치킨 약속... 살 안 찌게 먹는 최적의 주문 조합은?" | • **한 상 칼로리 시뮬레이터**: 기본 주문 2,280kcal 폭탄 시각화<br>• **생존 최적화 토글**: 곁들이(냉면, 소주, 쌈장) 변경 시 실시간 감량 계산<br>• **30초 외식 생존 카드**: 식당 입장 직전 폰으로 보는 행동 수칙 |
| **3. [GutSafe]**<br>감미료·당알코올 한도 트래커 | "오늘 마신 제로음료 2캔 + 프로틴바... 내 장은 안전할까?" | • 오늘 먹은 제로 식품/음료 간편 기록<br>• **일일 누적량 시각화**: 알룰로스 성인 24g 대비 N%<br>• **장 안전 경보**: 가스, 복부 팽만, 설사 위험선 사전 알림 |
| **4. [Dessert Fact Wiki]**<br>디저트·감미료 팩트 사전 | "시판 대체당과 다이어트 디저트의 과학적 팩트와 식약처/WHO 기준" | • 감미료별(알룰로스, 에리스리톨, 말티톨 등) GI, 칼로리, 흡수율 비교<br>• 식약처 허용 기준 및 공인 연구 브리핑 아카이브 |

---

## ⚡ 3. 마케팅 → 블로그 & 앱 게시판 자동 배선 파이프라인 (실행 방법)

마케팅 저쪽(`/Users/name/Desktop/Cluade/DESSERT`)의 `card_news_svg/`(트랙 A)나 `단일 카드뉴스/`(트랙 B)에 기획서(`00-기획서.md` 또는 `00-기획안.md`)가 작성되면, 본 시스템이 정본 규격에 맞추어 **네이버 블로그 포맷(`01_블로그.md`)**과 **앱 게시판 포맷(`02_앱게시판.md`)**으로 즉시 변환합니다.

### 1) 배선 현황 확인
```bash
python3 scripts/sync_marketing_to_blog.py --status
```
*모든 캠페인의 기획서 유무, 블로그/앱게시판 생성 상태를 표로 한눈에 확인합니다.*

### 2) 특정 캠페인 동기화 (단건 생성)
```bash
python3 scripts/sync_marketing_to_blog.py --sync "dining_1_samgyeopsal"
# 또는
python3 scripts/sync_marketing_to_blog.py --sync "20260705-WHO-감미료-체중감량"
```

### 3) 모든 캠페인 일괄 동기화 (20개 전수 생성 완료)
```bash
python3 scripts/sync_marketing_to_blog.py --sync-all
```

### 4) 실시간 감시 모드 (저쪽에서 새로 만들면 자동 생성!)
```bash
python3 scripts/sync_marketing_to_blog.py --watch
```
*마케팅 폴더를 실시간 감시하여 새 캠페인이 추가되거나 기획서가 수정되면 즉시 01_블로그.md 및 02_앱게시판.md를 자동 생성합니다.*

### 5) macOS 원클릭 클립보드 복사 (`pbcopy` 연동)
```bash
# 네이버 블로그용 마크다운 본문 클립보드 복사
python3 scripts/sync_marketing_to_blog.py --copy-blog "dining_1_samgyeopsal"

# 앱 게시판용 클린 텍스트(이모지/볼드 제거) 복사
python3 scripts/sync_marketing_to_blog.py --copy-app "dining_1_samgyeopsal"

# 네이버 블로그 태그 30개만 복사
python3 scripts/sync_marketing_to_blog.py --copy-tags "dining_1_samgyeopsal"
```
*터미널 실행 즉시 클립보드에 들어가므로, 네이버 스마트에디터 ONE 또는 관리자 화면에서 `Cmd + V`로 바로 붙여넣을 수 있습니다.*

---

## 🌐 4. 시각적 웹 대시보드 & 미리보기 서버

마케터와 운영자가 브라우저에서 네이버 블로그 스타일로 시각적 렌더링을 확인하고, 원클릭으로 복사할 수 있는 로컬 웹 대시보드를 제공합니다.

```bash
python3 scripts/preview_server.py
```
- 브라우저 접속: **`http://localhost:8766`**
- 기능:
  - 20개 전 캠페인 실시간 검색 및 전환
  - 네이버 블로그 스마트에디터 ONE 스타일 렌더링 미리보기
  - 앱 게시판(순수 텍스트) 미리보기
  - 원클릭 복사 버튼: `[📋 네이버 블로그용 복사]`, `[🏷️ 태그 30개 복사]`, `[📱 앱게시판 복사]`

---

## 📂 5. 디렉터리 구조

```
/Users/name/cursor/app/
├── docs/
│   ├── PRODUCT_SPECIFICATIONS.md      # DESSERT 인사이트 기반 4대 프로덕트 상세 기획서 (영구 보관)
│   └── PIPELINE_ARCHITECTURE.md       # 마케팅-블로그 자동 배선 아키텍처 상세 문서
├── scripts/
│   ├── sync_marketing_to_blog.py      # 마케팅 -> 블로그/앱게시판 변환, CLI, 감시기, 클립보드 복사
│   ├── blog_generator.py              # 네이버 블로그 정본(2,500자, SEO, 팩트체크, 태그 30개) 생성기
│   ├── app_board_generator.py         # 앱 게시판(이모지 0개 전면 제거, bold 제거, 태그 4개) 생성기
│   ├── build_static_site.py           # GitHub Pages 배포용 index.html 생성기
│   └── preview_server.py              # 웹 미리보기 & 원클릭 복사 로컬 서버 (localhost:8766)
├── output/
│   └── blog/                          # 생성된 20개 캠페인 아카이브 (01_블로그.md, 02_앱게시판.md)
│       ├── dining_1_samgyeopsal/
│       ├── 1_erythritol/
│       ├── 2_allulose/
│       ├── 20260705-WHO-감미료-체중감량/
│       └── ... (총 20개 폴더)
├── index.html                         # GitHub Pages 호스팅용 정적 웹 대시보드
└── README.md                          # 본 가이드 문서
```
