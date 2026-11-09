# 빌드 방법

번역 대본(`text/`)과 글꼴 파일은 저장소에 없으므로, 아래는 같은 자료를 갖춘 경우의 절차입니다.

## 준비
- Python 3.11 이상, Pillow (`pip install pillow`), 분석용 capstone(선택)
- 원본 `Khamrai (Japan).bin` (README의 해시와 일치)을 저장소 상위 폴더에 둡니다.
- 글꼴: `fonts/Galmuri7.ttf`, `fonts/Galmuri9.ttf`, `fonts/Galmuri11.ttf`, 상위 폴더에 `SeoulHangangB.ttf`, `SeoulHangangM.ttf`, `SeoulHangangEB.ttf`

## 순서
1. 원본 추출: `python tools/unpack.py` → `orig/`, `ext/`
2. 원문 추출: `python tools/extract.py`(대사 → `text/ja.json`, `text/src/`), `python tools/mextract.py`(메뉴·데이터 → `text/msrc/`)
3. 번역: `text/ko/sNN.tsv`, `text/mko/<파일>.tsv` (`docs/TRANSLATION_GUIDE.md`)
4. 빌드: `python build.py` → 상위 폴더에 `Khamrai (Japan) [KR].bin` (약 20초, 로그는 `build.log`)
5. 차분 파일: `xdelta3 -e -0 -S none -A -s "Khamrai (Japan).bin" "Khamrai (Japan) [KR].bin" Khamrai_KO_v1.0.xdelta`
