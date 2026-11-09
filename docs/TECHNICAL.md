# 기술 문서

## 디스크 구조
- 트랙 1개(MODE2/2352). 실행 파일 `SLPS_026.40`, 게임 데이터 `ASDATA.BIN` + 목록 `ASDATA.FAT`.
- `ASDATA.FAT`: 10바이트 항목(이름 8바이트 + 섹터 수 2바이트)이 순서대로 이어지고, 시작 섹터는 앞 항목들의 누적값입니다(`tools/fat.py`). 내부 파일 2,617개.
- 빌드는 바뀐 내부 파일을 다시 배치해 `ASDATA.BIN`을 새로 쓰고, FAT와 ISO9660 디렉터리의 크기를 고친 뒤 섹터 EDC/ECC를 다시 계산합니다(`tools/disc.py`, `tools/cdsec.py`).

## 대사 스크립트
- `$ASS` 헤더 파일. 문자열은 Shift-JIS이고, `%M`(이름 등), `%C`(색), `%W`(간격) 같은 제어 코드가 들어 있습니다(`tools/ass.py`, `tools/extract.py`).
- 이 게임의 글꼴에서 `☆`는 `!`, `★`는 `?` 모양입니다.
- 대사창은 한 줄 17자를 넘으면 자동으로 줄을 바꾸고, 문자열마다 한 줄을 차지합니다. 같은 창의 다른 문자열과 겹치지 않도록 `tools/reflow.py`가 연속된 줄 사이에서 단어를 옮기고, 혼자 쓰이는 긴 줄에만 `\n`을 넣습니다.

## 글꼴
- `KANJI`: 12×12 2bpp 글꼴 시트. Shift-JIS 코드 0x889F부터 한글 음절을 배정합니다(`tools/kfont.py`, `build.py`). 실제로 쓰인 한글 1,050자를 Galmuri11로 그려 넣습니다.
- 글자 번호 → 텍스처 위치: 페이지 = idx / 378, 행 = (idx % 378) / 21, 열 = (idx % 378) % 21, 한 칸 12px.

## 실행 파일 패치
- 0x8002adc0 글자 출력 루틴을 고쳐(`tools/spacepatch.py`), 글자 표에 없는 코드 `! `(0x2120)를 그리지 않고 6px 전진하는 반각 공백으로 씁니다.
- 실행 파일 안의 메뉴 문자열은 원래 자리에 덮어씁니다(`text/mko/exe.tsv`, `tools/exestr.py`). 메모리 카드 세이브 제목은 BIOS가 표시하므로 그대로 둡니다.

## 데이터 문자열
- `ITEM`, `MAGIC`, `ENEMY`, `WILL_D`, `P_LOD`, `P_WLD`의 이름·설명 문자열은 `tools/mdata.py` 정의대로 읽고 씁니다. 길이가 늘어 섹터 수가 커진 파일(MAGIC, KOHDA)은 재배치로 해결합니다.

## 그림 글자
- 대상 TIM은 모두 4bpp, 팔레트 0번이 투명입니다(`tools/tim.py`, `tools/gfx.py`).
- `tools/gfxall.py`에 파일별 작업이 모여 있습니다: `FNAME`(지역명 70종), `INIT`(상태 팝업·나침반·아이콘·전투 배너), `WILL_D`, `WMAP_T`, `MIND_T`, `KHAM_T`(타이틀 게임 이름).
- `tools/gfx2.py`: 원본 팔레트 안에서 가장 가까운 색을 골라 안티에일리어싱(`draw_aa`), 행별 그라데이션·외곽선 재현(`draw_style`), 원래 글자만 주변 색으로 지우고 테두리를 살리는 방식(`draw_replace`).
- 타이틀의 게임 이름 텍스처는 화면에서 가로로 약 1/3.5로 줄어 표시되므로 가로로 늘려 그립니다.

## 검증 도구
- `tools/emu.py`, `tools/srv.py`, `tools/c.py`, `tools/mv.py`: DuckStation을 백그라운드로 띄워 GDB 원격 접속으로 메모리를 읽고 쓰고, 키 입력·스크린샷을 자동화합니다.
- `tools/check.py`, `tools/rfcheck.py`: 번역 파일의 제어 코드·줄 길이 검사.
- `tools/timsheet.py`, `tools/timzoom.py`, `tools/scan.py`: 그림·문자열 조사.
