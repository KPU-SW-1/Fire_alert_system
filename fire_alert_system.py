import time
import random

# 0. 색상 코드 정의
class Colors:
    RED = '\033[91m'  # 오류/위험
    GREEN = '\033[92m'  # 정상
    YELLOW = '\033[93m'  # 경고
    RESET = '\033[0m'  # 초기화
    BOLD = '\033[1m'  # 굵게



# 임계값 설정(감지시 화재 기준)
TEMP_THRESHOLD = 60.0
SMOKE_THRESHOLD = 0.1


#  칸 밀림 방지 출력 함수
def pad_and_color(text, width, color=None):
    # 1. 공간 확보 (중앙 정렬)
    padded_text = f"{text:^{width}}"

    # 2. 색상 입히기
    if color:
        return f"{color}{padded_text}{Colors.RESET}"
    else:
        return padded_text


# 3. 로직 및 출력 (틀 관련)
def print_header():
    print("=" * 160)
    # 각 컬럼의 너비를 미리 정해둡니다.
    # ID(6), Temp(12), Smoke(12), Heat_S(12), Smoke_S(12), Control(12), Alarm(10), Status(20)
    print(
        f"| {'ID':^6} | {'Temp(°C)':^12} | {'Smoke(m-1)':^12} | {'Heat(S)':^12} | {'Smoke(S)':^12} | {'Control':^12} | {'Alarm':^10} | {'Status':^12} | {'Detailed Reason':^30} |")
    print("=" * 160)


def log_event(step_id, status, reason, temp, smoke,
              heat_val, heat_expect,
              smoke_val, smoke_expect,
              ctrl_val, ctrl_expect,
              alarm_val):

    # --- 1. 각 데이터 문자열 준비 ---
    heat_str = "True" if heat_val else "False"
    smoke_str = "True" if smoke_val else "False"
    ctrl_str = "True" if ctrl_val else "False"
    alarm_str = "ON" if alarm_val else "off"

    # --- 2. 색상 결정 로직 ---
    # (1) Heat 센서 색상
    c_heat = None
    if heat_val != heat_expect: c_heat = Colors.RED + Colors.BOLD

    # (2) Smoke 센서 색상
    c_smoke = None
    if smoke_val != smoke_expect: c_smoke = Colors.RED + Colors.BOLD

    # (3) Control 제어기 색상
    c_ctrl = None
    if ctrl_val != ctrl_expect: c_ctrl = Colors.RED + Colors.BOLD

    # (4) Alarm 색상
    # 오류(제어기랑 다름)면 빨강+굵게, 제어기랑 같으면 색 없음
    c_alarm = None
    if alarm_val != ctrl_val:  # 오류 상황
        c_alarm = Colors.RED + Colors.BOLD

    # (5) Status 색상
    c_status = Colors.GREEN  # 기본 초록
    if status == "Emergency":
        c_status = Colors.RED + Colors.BOLD
    elif status == "Warning":
        c_status = Colors.YELLOW

    # --- 3. 공간 확보 후 색칠하기 (pad_and_color 사용) ---
    # 이미 함수 안에서 너비(padding)를 맞추므로, f-string에서는 너비를 지정하지 않습니다.
    p_id = f"{step_id:^6}"
    p_temp = f"{temp:^12.1f}"
    p_smoke = f"{smoke:^12.2f}"

    # 여기서 너비를 지정합니다 (헤더와 동일하게)
    p_heat = pad_and_color(heat_str, 12, c_heat)
    p_smoke_s = pad_and_color(smoke_str, 12, c_smoke)
    p_ctrl = pad_and_color(ctrl_str, 12, c_ctrl)
    p_alarm = pad_and_color(alarm_str, 10, c_alarm)  # Alarm 너비 10
    p_status = pad_and_color(status, 12, c_status)  # Status 너비 12
    p_reason = f"{reason:^30}"

    # --- 4. 최종 출력 ---
    # 변수 자체에 공백이 포함되어 있으므로 바로 출력합니다.
    print(f"| {p_id} | {p_temp} | {p_smoke} | {p_heat} | {p_smoke_s} | {p_ctrl} | {p_alarm} | {p_status} | {p_reason} |")


def print_manual_footer():
    print(f"\n{Colors.BOLD}   [ 시스템 상태별 표준 대응 매뉴얼 ]{Colors.RESET}\n")

    # Normal 매뉴얼
    print(f"   {Colors.GREEN}■ Normal (정상){Colors.RESET}")
    print(f"     └─ [전략] 지속적인 모니터링 수행")
    print(f"     └─ [실행] 시스템 상태를 '정상'으로 표시 ")
    print("")

    # Warning 매뉴얼
    print(f"   {Colors.YELLOW}■ Warning (오작동/이상 징후){Colors.RESET}")
    print(f"     └─ [전략] 관리자에게 시스템 점검 및 수리 요청")
    print(f"     └─ [실행] 센서 점검 및 오작동 원인 분석 (감도 설정 등 재확인)")
    print("")

    # Emergency 매뉴얼
    print(f"   {Colors.RED}{Colors.BOLD}■ Emergency (비상/화재){Colors.RESET}")
    print(f"     └─ [전략] 예비 시스템 가동 및 수동 대응 전환 전략 실행")
    print(f"     └─ [실행 1] 인명 보호 우선: 건물 전체 사이렌/비상등 작동")
    print(f"     └─ [실행 2] 확산 방지: 방화문 폐쇄 및 셔터 하강")
    print(f"     └─ [실행 3] 신고: 소방서 및 건물주에게 화재 위치 자동 통보")

# ---------------------------------------------------------------------
# 4. 메인 시뮬레이션
# ---------------------------------------------------------------------
def main():
    print(f"\n{Colors.BOLD}### [Critical System] 화재 감지 및 대응 시스템 ###{Colors.RESET}")
    print(
        "※" + f"{Colors.GREEN}초록색=정상{Colors.RESET}, " + f"{Colors.RED}{Colors.BOLD}빨간색=오류(센서 불일치/고장){Colors.RESET}")

    print_header()

    for i in range(1, 11):
        step_id = f"S-{i:02d}"

        # --- [1] 물리 환경 (Ground Truth) ---
        # 40%로 확률로 화재 발생 하는 랜덤 함수 (이상 온도, 감광 계수 감지)
        is_real_fire = random.random() > 0.6
        if is_real_fire:
            actual_temp = random.uniform(65.0, 800.0)
            actual_smoke = random.uniform(0.6, 3.0)
            env_type = "FIRE"
        else:
            actual_temp = random.uniform(20.0, 45.0)
            actual_smoke = random.uniform(0.0, 0.3)
            env_type = "SAFE"

        # --- [2] 이상적인 센서 값---
        expect_heat = actual_temp >= TEMP_THRESHOLD
        expect_smoke = actual_smoke >= SMOKE_THRESHOLD

        # --- [3] 실제 값(Actual) & 결함 주입 ---
        actual_heat_sensor = expect_heat
        actual_smoke_sensor = expect_smoke

        # 20% 확률로 센서 고장
        if random.random() < 0.2:
            # 고장이 난다면, 30% 확률로 '열 센서'를 고장 낼지 '연기 센서'를 고장낼지, 전부를 고장낼지 결정
            if random.random() > 0.3:
                actual_heat_sensor = not expect_heat
            elif random.random() > 0.3:
                actual_smoke_sensor = not expect_smoke
            else:
                actual_heat_sensor = not expect_heat
                actual_smoke_sensor = not expect_smoke

        # --- [4] 중앙 제어기 로직 (AND) ---
        expect_ctrl = actual_heat_sensor and actual_smoke_sensor
        actual_ctrl = expect_ctrl

        # 5% 확률로 중앙 제어기(Control) 고장
        if random.random() < 0.05: actual_ctrl = not expect_ctrl

        # --- [5] 알람 로직 ---
        actual_alarm = actual_ctrl
        
        # 알람 고장
        if random.random() < 0.05: actual_alarm = not actual_alarm

        status = "Unknown"
        reason = "-"

        # --- [6] 최종 상태 판별 ---
        # 1. Normal (정상) 화재 시 경보가 제대로 울렸거나, 평소에 경보가 울리지 않았거나
        if env_type == "FIRE" and actual_alarm:
            status = "Normal"
            reason = "정상 작동 상태"
        elif env_type == "SAFE" and not actual_alarm:
            status = "Normal"
            reason = "정상 유지 상태"

        # 2. Warning (오작동: 불이 안 났는데 경보가 울림)
        elif env_type == "SAFE" and actual_alarm:
            status = "Warning"
            # Warning Case 1: 센서 오작동
            if actual_heat_sensor and actual_smoke_sensor:
                reason = "센서 오작동"

                # Warning Case 2: 센서 상관없이 중앙 제어기만 오류 (True)
            else:
                reason = "중앙 제어기 / 비상벨 오작동"

        # 3. Emergency (비상/실패: 불이 났는데 경보가 안 울림)
        elif env_type == "FIRE" and not actual_alarm:
            status = "Emergency"
            # Emergency Case 3: 열 연기 둘 다 감지 False
            if not actual_heat_sensor and not actual_smoke_sensor:
                reason = "둘 다 감지 실패"
            # Emergency Case 1: 열 감지만 잘못됨 (열만 False)
            elif not actual_heat_sensor and actual_smoke_sensor:
                reason = "열 감지 실패"
            # Emergency Case 2: 연기 감지만 잘못됨 (연기만 False)
            elif actual_heat_sensor and not actual_smoke_sensor:
                reason = "연기 감지 실패"

            # Emergency Case 4: 감지는 성공했지만 중앙제어기 처리 불가 (제어기 False)
            elif actual_heat_sensor and actual_smoke_sensor and not actual_ctrl:
                reason = "제어기 처리 실패"

            # Emergency Case 5: 감지 성공, 제어기 성공, 그러나 경보 off (알람 고장)
            elif actual_ctrl and not actual_alarm:
                reason = "경보벨 고장"
        # 나머지
        else:
            status = "Unknown Error"
            reason = "알 수 없는 상태"

        # --- 로그 출력 ---
        log_event(step_id, status, reason, actual_temp, actual_smoke,
                  actual_heat_sensor, expect_heat,
                  actual_smoke_sensor, expect_smoke,
                  actual_ctrl, expect_ctrl,
                  actual_alarm)

        time.sleep(1)

    print("=" * 160)

    print_manual_footer()

if __name__ == "__main__":
    main()