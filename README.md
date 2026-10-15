# Zomput-Random_Talent

![Zomput Random Talent](docs/media/workshop-cover.jpg)

대표 이미지는 모드 주제를 표현한 AI 생성 일러스트이며 실제 게임 화면이 아닙니다. [원본 및 생성 프롬프트](docs/ARTWORK.md)

Project Zomboid **Build 42.21 / 42.21.0**에서 직업과 특성을 무작위로만 선택하게 하는 모드입니다. 한국어·영어를 지원합니다.

**Mod ID:** `ZomputRandomTalent`

**Workshop ID:** `3820144158` · [스팀 창작마당](https://steamcommunity.com/sharedfiles/filedetails/?id=3820144158)

## 사용 방법

1. 서버와 접속 클라이언트에서 모드를 활성화합니다. 싱글플레이에서도 사용할 수 있습니다.
2. 샌드박스의 **Zomput 무작위 특성 → 무작위 선택 기회**를 설정합니다. 기본 5회, 범위 1~100회입니다.
3. 직업·특성 화면에서 **무작위**를 누릅니다. 직업과 특성이 함께 바뀌며 버튼 옆에 남은 횟수가 표시됩니다.
4. 최소 한 번 실행한 뒤 다음 화면으로 진행할 수 있습니다. 횟수가 0이면 무작위 버튼이 비활성화됩니다.

첫 무작위도 횟수에 포함됩니다. 초기화와 저장된 빌드 불러오기는 사용할 수 없으며, 직접 직업 선택·특성 추가·삭제는 마우스와 게임패드에서 모두 차단합니다. 외형 화면에 갔다가 돌아와도 횟수가 유지되고, 새 캐릭터를 만들 때 새 횟수가 부여됩니다.

포인트가 음수이거나 남아도 캐릭터를 생성할 수 있습니다. 원래 포인트 숫자는 바꾸지 않습니다. 기본 게임의 무작위는 포인트를 0~3에 맞추려 최대 1,000회 보정하지만 항상 보장되지는 않습니다. 이 모드는 점수 보정 대신 직업과 긍정·부정 특성 후보를 직접 추첨하며 기본 게임의 특성 적용·상호 배제 검사를 사용합니다. 따라서 기본 무작위와 추첨 분포가 다릅니다.

직업이 주는 고유 특성을 유지하며, 서버 수면 옵션에 따라 사용할 수 없는 특성은 기본 게임처럼 후보에서 제외됩니다. 후보 목록이 비어도 오류를 내지 않으며 추첨 반복 횟수는 제한되어 있습니다. 다른 모드의 오류로 추첨이 실패하면 해당 기회는 소모되고 진행은 차단됩니다.

## 설치와 호환

멀티플레이는 서버와 모든 클라이언트에 같은 모드 버전을 사용하세요. 서버 `Mods` 목록에는 `ZomputRandomTalent`, `WorkshopItems` 목록에는 `3820144158`을 추가합니다. 샌드박스 설정 키는 `ZomputRandomTalent.RollLimit`입니다.

제한 범위는 현재 게임 실행 중의 캐릭터 생성 과정입니다. 서버 계정별 영구 횟수 제한이나 변조된 클라이언트를 막는 보안 기능은 아닙니다. 게임을 완전히 종료하거나 연결 과정을 새로 시작하면 새 생성 과정으로 취급될 수 있습니다. 기존 생존 캐릭터의 직업·특성은 바꾸지 않습니다.

캐릭터 생성 화면을 대체하거나 특성을 직접 수정하는 다른 모드와는 충돌할 수 있습니다. 새 캐릭터 생성에서 먼저 확인하세요. 검증 결과와 남은 항목은 [테스트 기록](docs/TESTING.md)에 기록합니다.

## English

Random-only profession and traits for Build 42.21. Set **Zomput Random Talent → Randomization attempts** in sandbox options (1–100, default 5). The first roll counts. Remaining attempts appear beside Random; the button is disabled at zero. Roll at least once before continuing. Negative or surplus trait points do not prevent creation.

Manual changes, reset and preset loading are blocked, including controller paths. Going back from appearance preserves the budget. This is a character-creation UI rule, not a persistent account limit or protection against modified clients. Install on the server and every client. Existing characters are unchanged.
