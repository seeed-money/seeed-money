# seeed-money

##  Celery 백그라운드 실행 및 스케줄링 확인


### 1. 서비스 실행 및 환경 구성 (Background Mode)
Docker Compose를 사용하여 서비스들을 백그라운드(데몬) 상태로 실행하였습니다.
```
# 1. 모든 서비스를 백그라운드에서 실행
docker-compose -f docker-compose.dev.yml up -d

# 2. 실행 중인 컨테이너 프로세스 목록 확인
docker-compose -f docker-compose.dev.yml ps
```

### 2. 스케줄링 및 작업 상태 검증 과정
정해진 주기마다 task가 동작 하는지 순차적으로 검증
```
# [Check 1] 현재 워커에 등록된 전체 태스크 목록 확인
docker-compose -f docker-compose.dev.yml exec worker celery -A config inspect registered

# [Check 2] 실시간으로 진행 중인 활성 태스크 모니터링
docker-compose -f docker-compose.dev.yml exec worker celery -A config inspect active

# [Check 3] 스케줄러(Beat)와 워커(Worker) 간의 연동 로그 실시간 확인
docker-compose -f docker-compose.dev.yml logs -f worker beat
```
### 3. 최종 결과 및 로그 데이터
celery beat가 정해진 시간마다 태크스 발행 -> celery worker가 받아서 일함
```
beat-1    | [2026-02-25 17:15:10,513: INFO/MainProcess] Scheduler: Sending due task analysis-every-minute (analysis.tasks.analyze_spending_habit)
worker-1  | [2026-02-25 17:15:10,514: INFO/MainProcess] Task analysis.tasks.analyze_spending_habit[1f0d1d57-d780-4962-a0be-be1c85dcce2b] received
worker-1  | [2026-02-25 17:15:10,515: INFO/ForkPoolWorker-8] 소비 패턴 분석 시작...
worker-1  | [2026-02-25 17:15:10,515: INFO/ForkPoolWorker-8] 소비 패턴 분석 완료!
worker-1  | [2026-02-25 17:15:10,523: INFO/ForkPoolWorker-8] Task analysis.tasks.analyze_spending_habit[1f0d1d57-d780-4962-a0be-be1c85dcce2b] succeeded in 0.00865062499724445s: 'Analysis Completed'
```
```
worker-1  | [2026-02-26 11:09:51,354: INFO/MainProcess] Task analysis.tasks.analyze_spending_habit[8bbafbcb-4db6-45df-a602-99beafee29b6] received
worker-1  | [2026-02-26 11:09:51,355: INFO/ForkPoolWorker-7] 🚀워렌버핏 빙의한 AI의 소비 분석 시작...
worker-1  | [2026-02-26 11:09:56,781: INFO/ForkPoolWorker-7] 😎분석 완료! 이번 달 총 지출: 8000원
worker-1  | [2026-02-26 11:09:56,781: INFO/ForkPoolWorker-7] 😁AI의 조언: 부모님 효도와 게임 한 판의 가치가 동급인 시점에서 당신의 경제적 우선순위는 이미 파산 상태입니다.
worker-1  | [2026-02-26 11:09:56,784: INFO/ForkPoolWorker-7] Task analysis.tasks.analyze_spending_habit[8bbafbcb-4db6-45df-a602-99beafee29b6] succeeded in 5.429903252000258s: '부모님 효도와 게임 한 판의 가치가 동급인 시점에서 당신의 경제적 우선순위는 이미 파산 상태입니다.'