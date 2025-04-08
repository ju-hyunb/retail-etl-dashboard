# 🛒 Online Retail ETL & Dashboard

**PySpark + Django 기반 이커머스 데이터 분석 및 시각화 프로젝트**

---

## 🔧 기술 스택

- Python 3.12
- PySpark
- Pandas / Parquet
- Django 4.x
- MySQL (or CSV)
- HTML Template (Jinja2)

---

## 📁 프로젝트 구조

```
retail-etl-django/
├── config/               # Spark & DB 설정 (JSON)
├── data/                 # 원본 CSV
├── jars/                 # JDBC 드라이버
├── logs/                 # 실행 로그
├── output/               # 분석 결과 (Parquet 저장)
├── scripts/              # 유틸 스크립트
├── spark_jobs/           # Spark ETL 실행 코드
├── django-retail/        # Django 웹 대시보드
│   ├── analysis/         # 분석 결과 뷰
│   ├── templates/        # 테이블 시각화 템플릿
│   └── ...
├── requirements.txt
└── README.md
```

---

## 🚀 실행 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

---

### 2. JDBC 드라이버 다운로드

```bash
python scripts/download_jdbc_driver.py
```

---

### 3. Spark ETL 실행

```bash
python spark_jobs/process_transaction.py
```

✅ `output/` 폴더에 분석 결과가 `.parquet`으로 저장.

---

### 4. Django 웹서버 실행

```bash
cd django-retail
python manage.py runserver
```

- 접속 URL:
  - http://127.0.0.1:8000/analysis/monthly/
  - http://127.0.0.1:8000/analysis/country/
  - http://127.0.0.1:8000/analysis/customer/
  - http://127.0.0.1:8000/analysis/top10/
  - http://127.0.0.1:8000/analysis/timeslot/

---

## 📊 분석 항목

| 분석 항목            | 설명                          |
|----------------------|-------------------------------|
| 📅 월별 매출         | 연도/월별 총 매출             |
| 🌍 국가별 매출       | 국가 기준 총 매출             |
| 🧑 고객별 평균 구매   | CustomerID 기준 평균 구매     |
| 📦 인기 상품          | 판매량 Top 10 상품             |
| 🕒 시간대별 매출     | 아침/오후/저녁/밤 구간별 매출 |

---
