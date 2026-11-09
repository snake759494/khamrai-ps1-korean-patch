# 카무라이 (PS1) 비공식 한글패치

PS1 일본판 **神来 -KHAMRAI- (카무라이, SLPS-02640)** 비공식 한국어 패치입니다. 이 저장소에는 제작 도구와 기술 문서만 있고, 패치 파일(xdelta)은 [Releases](../../releases)에서 받을 수 있습니다. 게임 원본·일본어 원문·번역 대본은 포함하지 않습니다.

## 적용 방법
1. 아래 해시와 일치하는 **원본 `.bin`/`.cue`** (Redump 형식, 트랙 1개)를 준비합니다. (CHD·PBP·ECM 등으로 변환한 이미지에는 적용할 수 없습니다.)
   - PowerShell: `Get-FileHash -Algorithm MD5 -LiteralPath '.\Khamrai (Japan).bin'`
2. xdeltaUI 같은 도구로 원본 `.bin` 에 `Khamrai_KO_v1.1.xdelta` 를 적용합니다. (Patch = xdelta, Source File = 원본 BIN, Output File = 새 파일명)
   - 명령줄: `xdelta3 -d -s "Khamrai (Japan).bin" Khamrai_KO_v1.1.xdelta "Khamrai (Korean).bin"`
3. 원본 `.cue` 를 복사해 이름을 바꾸고, 안의 `FILE "..."` 줄을 새 `.bin` 파일명으로 고칩니다.
4. 만들어진 `.cue` 를 DuckStation 등 PS1 에뮬레이터나 ODE 장치에서 실행합니다.

| 항목 | 값 |
| --- | --- |
| 원본 BIN 크기 | 497,927,808 바이트 |
| 원본 BIN MD5 | `82e83717581cfd3be10daee0a816e3d4` |
| 원본 BIN SHA-256 | `e99772014d8090aedc849121d9fa120498978682484ce922262e9063a695013c` |
| xdelta SHA-256 | `e41707a49e872655ed5387236e586af72a903ff15089640a0e75192ea5e8b9a3` |
| 결과 BIN 크기 | 497,927,808 바이트 |
| 결과 BIN SHA-256 | `dbb79d7adc3dee029a7a202634374784a3c9faff55b0772a367d9ccc71432b59` |

## 주의
- 원본에서 만든 **상태저장(세이브 스테이트)** 은 불러오지 마세요. 글꼴 배치가 달라 글자가 깨집니다. 메모리 카드 세이브는 그대로 쓸 수 있습니다.
- xdelta는 압축하지 않은 형식(`-0`)입니다(약 1.7MB).

## 한글화 내용
- 대사 13,933줄 전수 직접 번역 — 대사창 한 줄 17자 제한에 맞춰 줄 재배치, 넘치는 대사는 뜻을 살려 줄여 씀
- 메뉴·설정·세이브/로드·상점·장비·상태·전투 메시지 등 실행 파일 문자열, 아이템·신위·적 이름과 설명 직접 번역
- 그림 글자 — 지역명 배너 70종, 상태 이상 팝업 11종, 나침반, 능력치·진형 아이콘, 전투 배너(획득 경험치·전리품·레벨 업·전투 승리·전투 결과), WILL 화면(호감·혐오·신뢰·불신), 월드맵 지명, MIND 화면 라벨, 타이틀 로고 아래 게임 이름 「카무라이」
- 게임 글꼴(12×12)에 한글 1,050자 추가, 실행 파일을 고쳐 반각 띄어쓰기 지원
- 글꼴: 본문 갈무리11, 작은 그림 글자 갈무리7·9, 지역명·배너 서울한강체

## 그대로 둔 것
- 음성, 영상, 「神来 KHAMRAI」 로고, 저작권 표기, 메모리 카드 관리 화면에 보이는 세이브 제목

## 검증 범위
DuckStation에서 타이틀, 로드 메뉴, 프롤로그 대사, 첫 지역(어둠의 숲)의 지역명 배너와 나침반을 확인했습니다. 모든 대사·문자열 파일을 전수 검사해 번역이 빠진 줄이 없고 번역 대상 일본어가 남지 않은 것을 확인했습니다. 전투·필드 메뉴를 포함한 전체 플레이 검증은 하지 않았습니다. 문제를 발견하면 Issues에 알려 주세요.

## 문서
- [CHANGELOG.md](CHANGELOG.md) — 변경 기록
- [docs/TECHNICAL.md](docs/TECHNICAL.md) — 파일 형식과 한글화 방법
- [docs/BUILD.md](docs/BUILD.md) — 직접 빌드하는 방법
- [docs/TRANSLATION_GUIDE.md](docs/TRANSLATION_GUIDE.md) — 번역 지침
- [docs/FONT_CREDITS.md](docs/FONT_CREDITS.md) — 글꼴
- [RIGHTS.md](RIGHTS.md) — 권리 및 외부 자료
