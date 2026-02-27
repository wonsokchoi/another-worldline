# DB Schema Design — 다른 세계선 (Another Worldline)

## Overview
PostgreSQL을 사용하며, SQLAlchemy ORM + Alembic으로 마이그레이션을 관리한다.

---

## Tables

### 1. users
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | 유저 고유 ID |
| phone_number | VARCHAR(20) | UNIQUE, INDEX | 전화번호 |
| phone_verified | BOOLEAN | default FALSE | 인증 여부 |
| nickname | VARCHAR(50) | NULLABLE | 닉네임 |
| daily_free_pulls_used | INTEGER | default 0 | 오늘 사용한 무료 뽑기 수 |
| last_pull_reset_date | TIMESTAMPTZ | NULLABLE | 마지막 뽑기 리셋 시각 |
| coupon_balance | INTEGER | default 0 | 유료 쿠폰 잔액 |
| created_at | TIMESTAMPTZ | default NOW() | 가입일 |
| updated_at | TIMESTAMPTZ | auto-update | 수정일 |

### 2. characters
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | 캐릭터 고유 ID |
| user_id | UUID | FK → users.id, INDEX | 소유자 |
| name | VARCHAR(100) | NOT NULL | 캐릭터 이름 |
| race | VARCHAR(50) | default '인간' | 종족 |
| hp | INTEGER | default 100 | 체력 |
| mp | INTEGER | default 50 | 마나 |
| strength | INTEGER | default 10 | 힘 |
| intelligence | INTEGER | default 10 | 지능 |
| agility | INTEGER | default 10 | 민첩 |
| luck | INTEGER | default 10 | 행운 |
| charm | INTEGER | default 10 | 매력 |
| skills | JSONB | default [] | 스킬 목록 |
| equipment | JSONB | default {} | 장비 |
| pets | JSONB | default [] | 펫 |
| relationships | JSONB | default [] | 관계 (연인 등) |
| rarity_score | FLOAT | default 0.0 | 희귀도 점수 (0~100) |
| worldline_count | INTEGER | default 0 | 경험한 세계선 수 |
| created_at | TIMESTAMPTZ | default NOW() | 생성일 |
| updated_at | TIMESTAMPTZ | auto-update | 수정일 |

### 3. worldlines
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | 세계선 고유 ID |
| character_id | UUID | FK → characters.id, INDEX | 캐릭터 |
| worldline_number | INTEGER | NOT NULL | 제N세계선 |
| genre | VARCHAR(50) | NOT NULL | 첫 장르 |
| is_active | BOOLEAN | default TRUE | 현재 활성 여부 |
| story_count | INTEGER | default 0 | 포함된 스토리 수 |
| created_at | TIMESTAMPTZ | default NOW() | 생성일 |

### 4. stories
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | 스토리 고유 ID |
| character_id | UUID | FK → characters.id, INDEX | 캐릭터 |
| worldline_id | UUID | FK → worldlines.id, INDEX | 소속 세계선 |
| genre | VARCHAR(50) | NOT NULL | 장르 |
| content | TEXT | NOT NULL | 스토리 본문 (200-400자) |
| stat_changes | JSONB | NULLABLE | 능력치 변동 |
| items_gained | JSONB | NULLABLE | 획득 아이템 |
| sequence_number | INTEGER | default 1 | 세계선 내 순서 |
| created_at | TIMESTAMPTZ | default NOW() | 생성일 |

---

## Entity Relationships

```
users 1:N characters
characters 1:N worldlines
characters 1:N stories
worldlines 1:N stories
```

```
┌─────────┐     1:N     ┌────────────┐     1:N     ┌────────────┐
│  users   │────────────▶│ characters  │────────────▶│ worldlines │
└─────────┘             └────────────┘             └────────────┘
                              │                         │
                              │ 1:N                     │ 1:N
                              ▼                         ▼
                        ┌────────────┐           ┌────────────┐
                        │  stories   │◀──────────│  stories   │
                        │(by char)   │  (by WL)  │(by worldline)│
                        └────────────┘           └────────────┘
```

## Indexes
- `users.phone_number` — UNIQUE INDEX (로그인 조회)
- `characters.user_id` — INDEX (유저별 캐릭터 조회)
- `stories.character_id` — INDEX (캐릭터별 스토리 조회)
- `stories.worldline_id` — INDEX (세계선별 스토리 조회)
- `worldlines.character_id` — INDEX (캐릭터별 세계선 조회)
- `characters.rarity_score` — INDEX (랭킹 조회) — *추후 추가*

## 장르 목록
| 코드 | 한국어 |
|------|--------|
| fantasy | 판타지 |
| romance | 로맨스 |
| thriller | 스릴러 |
| hero | 히어로 |
| sf | SF |
| essay | 수필 |
| scenario | 시나리오 |

## Migration Strategy
- Alembic으로 마이그레이션 관리
- 초기 마이그레이션: `alembic revision --autogenerate -m "initial"`
- 적용: `alembic upgrade head`
