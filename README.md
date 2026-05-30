# 🎙️ Sonido Pro

<p align="center">
  <img src="https://img.shields.io/badge/Open_Beta-v1.0.0--beta-orange?style=for-the-badge&logo=github&logoColor=white" alt="Open Beta">
  <img src="https://img.shields.io/badge/Platform-Windows_.exe-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/Architecture-Pure_WAV-ff3366?style=for-the-badge" alt="WAV Only">
  <img src="https://img.shields.io/badge/Developer-micio-orange?style=for-the-badge" alt="Developer">
</p>

<p align="center">
  <b>"불완전한 외부 코덱 ZERO, 오직 순정 코어로만 작동하는 무결점 Windows 오디오 레코더"</b><br>
  파이썬 3.13+ 아키텍처 변경으로 인한 인코딩 복병을 완벽하게 해결하고, 빌드 오버헤드가 없는 완전무결한 <code>.exe</code> 스탠드얼론 어플리케이션, <b>Sonido Pro</b>입니다.
</p>

---

## ⚡ Key Features

* **가볍고 강력한 `.exe` 실행 파일:** 별도의 파이썬 환경이나 복잡한 종속성 라이브러리 설치 필요 없이, 단 하나의 독립 실행 파일로 즉시 구동됩니다.
* **정밀한 실시간 시각화 (Visualizer Engine):** 마이크 입력 신호를 60Hz 주파수로 정밀 추적하여 눈을 사로잡는 비주얼 웨이브 그래픽을 선사합니다.
* **압도적인 무결성 (No Crash, No Corruption):** 배포 환경에서 흔히 발생하는 MP3 인코더 꼬임 이슈를 과감히 제거하여, 파일 손상(0KB) 없는 정통 고음질 무압축 WAV 레코딩을 보장합니다.
* **하이엔드 테마 스킨 가변 탑재:** 개발자 감성을 저격하는 `Cyberpunk`, `Slate Gray`, `Obsidian Black` 3종 프리셋 UI 테마와 한국어/English 실시간 토글 지원.

---

## 🎨 UI 테마 프리셋 가이드

> 💡 **Tip:** 프로그램 내 설정(Settings) 메뉴에서 언제든지 실시간으로 스타일과 다국어를 스위칭할 수 있습니다.

| 프리셋 스킨 | 메인 컬러 레퍼런스 | 비주얼 감성 |
| :--- | :--- | :--- |
| **Cyberpunk** | `#121214` ｜ `#00ffcc` ｜ `#ff3366` | 네온 그린과 핫핑크 포인트의 미래지향적 사이버 테마 |
| **Slate Gray** | `#2c3e50` ｜ `#3498db` ｜ `#e74c3c` | 차분하고 정돈된 모던 인더스트리얼 데스크톱 룩 |
| **Obsidian Black** | `#070708` ｜ `#e67e22` ｜ `#d35400` | 딥 블랙 베이스에 다크 오렌지 포인트를 준 하드코어 테마 |

---

## 📦 인스톨러 마법사 아티팩트 (Installer Infrastructure)

**Sonido Pro**는 안정적인 윈도우 인스톨러 패키징 마법사(Inno Setup 등) 생성을 위해 검증된 스크립트 인프라를 독립적으로 포함하고 있습니다.

* `PreInstall.bat` : 설치 진행 시 구버전이나 백그라운드에 상주 중인 `Sonido Pro` 관련 프로세스를 안전하게 강제 종료
* `PostInstall.bat` : 윈도우 시스템 AppData 내 독립 설정 공간 및 전용 저장 폴더(`%APPDATA%\micio_recorder\save`) 자동 빌드
* **이는 아직 지원하지 않습니다.**

---

# 📜 MIT 라이선스 (MIT License)

**Copyright (c) 2026 micio. All rights reserved.**

* **상업적 이용 (Commercial Use):** 전면 허용 ✅
* **소스 코드 수정 (Modification):** 전면 허용 ✅
* **재배포 (Redistribution):** 전면 허용 ✅

---

### 💡 주요 조건 및 안내 사항 (Terms & Conditions)

> **조건 및 허용 범위**
> 본 소프트웨어의 복사본과 관련된 문서 파일을 획득하는 모든 사람에게 소프트웨어를 무상으로 제한 없이 취급할 수 있는 권리가 부여됩니다. 여기에는 소프트웨어의 사본을 사용, 복제, 수정, 병합, 게시, 배포, 하위 라이선스 부여 및/또는 판매할 수 있는 권리가 포함됩니다.

> **의무 사항 (저작권 표시)**
> 소프트웨어의 모든 사본 또는 상당한 부분에는 위의 **저작권 공지(Copyright)**와 본 **허용 공지(MIT 라이선스 본문)**가 반드시 포함되어야 합니다.

> **면책 조항 (법적 책임 제한)**
> 본 소프트웨어는 상품성, 특정 목적에의 적합성 및 비침해에 대한 보증을 포함하여(단, 이에 한정지어지지 않음) 어떠한 종류의 명시적이거나 묵시적인 보증도 없이 **"있는 그대로"** 제공됩니다. 어떠한 경우에도 원작자나 저작권자는 계약, 불법행위 또는 기타 사유로 발생한 어떠한 청구, 손해 또는 기타 책임에 대해 책임을 지지 않습니다.
