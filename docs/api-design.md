# API Endpoint Design — 다른 세계선 (Another Worldline)

## Base URL
```
Production: https://api.another-worldline.com/v1
Development: http://localhost:8000
```

## Authentication
- Bearer Token (JWT)
- Token in Authorization header: `Authorization: Bearer <token>`
- Token expires in 7 days

---

## Endpoints

### Auth

#### POST /auth/register
전화번호 인증 요청

**Request:**
```json
{
    "phone_number": "+821012345678"
}
```

**Response (200):**
```json
{
    "message": "Verification code sent",
    "phone_number": "+821012345678"
}
```

---

#### POST /auth/verify
SMS 인증 코드 확인 + 로그인

**Request:**
```json
{
    "phone_number": "+821012345678",
    "code": "123456"
}
```

**Response (200):**
```json
{
    "access_token": "eyJ...",
    "token_type": "bearer"
}
```

**Errors:**
- `400` — Invalid verification code

---

### Characters

#### POST /characters
캐릭터 생성 (이름 입력)

**Requires Auth**

**Request:**
```json
{
    "name": "아리아"
}
```

**Response (201):**
```json
{
    "id": "uuid",
    "name": "아리아",
    "race": "인간",
    "stats": {
        "hp": 100,
        "mp": 50,
        "strength": 10,
        "intelligence": 10,
        "agility": 10,
        "luck": 10,
        "charm": 10
    },
    "skills": [],
    "equipment": {},
    "pets": [],
    "relationships": [],
    "rarity_score": 0.0,
    "worldline_count": 0,
    "created_at": "2026-02-27T00:00:00Z"
}
```

---

#### GET /characters/{id}
캐릭터 스탯/정보 조회

**Requires Auth**

**Response (200):** Same as creation response with updated values

**Errors:**
- `404` — Character not found

---

### Stories

#### POST /stories/pull
스토리 뽑기 (일 3회 무료)

**Requires Auth**

**Request:**
```json
{
    "character_id": "uuid"
}
```

**Response (200):**
```json
{
    "id": "uuid",
    "genre": "판타지",
    "content": "아리아가 눈을 떴을 때, 그녀는 거대한 수정 동굴 안에 서 있었다...",
    "worldline_number": 3,
    "sequence_number": 1,
    "stat_changes": {
        "hp": 0,
        "mp": 5,
        "strength": 0,
        "intelligence": 2,
        "agility": 0,
        "luck": 1,
        "charm": 0
    },
    "items_gained": {
        "skills": ["마나 감지"],
        "equipment": {},
        "pets": []
    },
    "created_at": "2026-02-27T12:00:00Z"
}
```

**Errors:**
- `404` — Character not found
- `429` — Daily free pulls exhausted (coupon balance = 0)

**Logic:**
1. UTC+9 자정 기준 daily_free_pulls_used 리셋
2. 무료 3회 소진 시 쿠폰 1개 차감
3. 랜덤 장르 선택
4. 이전 5개 스토리 컨텍스트로 AI 생성
5. 능력치 자동 반영

---

#### GET /stories/{character_id}/history
세계선 히스토리 (페이지네이션)

**Requires Auth**

**Query Params:**
- `limit` (default: 20)
- `offset` (default: 0)

**Response (200):**
```json
{
    "stories": [...],
    "total": 42
}
```

---

### Rankings

#### GET /rankings
전체 유저 희귀도 랭킹

**Requires Auth**

**Query Params:**
- `limit` (default: 50)

**Response (200):**
```json
{
    "rankings": [
        {
            "rank": 1,
            "character_name": "아리아",
            "user_nickname": "원돌",
            "rarity_score": 95.5,
            "worldline_count": 42,
            "race": "엘프"
        }
    ],
    "total_characters": 1000,
    "my_rank": 15
}
```

---

### Utility

#### GET /health
서버 상태 확인

**Response (200):**
```json
{
    "status": "ok",
    "service": "another-worldline"
}
```

---

## Error Format

All errors follow this format:
```json
{
    "detail": "Error message here"
}
```

## Rate Limits (planned)
| Endpoint | Limit |
|----------|-------|
| POST /auth/register | 5/min per IP |
| POST /stories/pull | 3/day free + coupon |
| GET /rankings | 30/min per user |

## Status Codes
| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
