"""
바탕화면에 Streamlit 앱 바로가기 생성 스크립트
"""
import os
import sys
from pathlib import Path

def create_shortcut_windows():
    """Windows 바탕화면에 바로가기 생성"""
    try:
        import win32com.client
    except ImportError:
        print("[ERROR] win32com 모듈이 없습니다.")
        print("설치: python -m pip install pywin32")
        return False

    try:
        # 바탕화면 경로
        desktop = str(Path.home() / "Desktop")
        shortcut_path = os.path.join(desktop, "T3 Demo Configurator.lnk")

        # 배치 파일 경로
        batch_file = r"C:\Users\lotus\DemoCreate\run_app.bat"
        work_dir = r"C:\Users\lotus\DemoCreate"

        # COM 객체 생성
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)

        # 바로가기 설정
        shortcut.TargetPath = batch_file
        shortcut.WorkingDirectory = work_dir
        shortcut.Description = "T³ Demo Configurator - Streamlit 데이터 변환 플랫폼"
        shortcut.IconLocation = r"C:\Windows\System32\cmd.exe,0"

        # 저장
        shortcut.save()

        print("\n✅ 바로가기 생성 완료!")
        print(f"   위치: {shortcut_path}")
        print("\n📌 사용 방법:")
        print("   1. 바탕화면에서 'T3 Demo Configurator' 아이콘 찾기")
        print("   2. 더블클릭으로 실행")
        print("   3. 자동으로 웹브라우저에서 http://localhost:8501 열림")

        return True

    except Exception as e:
        print(f"[ERROR] 바로가기 생성 실패: {str(e)}")
        return False


def create_alternative_shortcut():
    """대체 방법: 간단한 배치 파일 만들기"""
    print("\n[Alternative] 배치 파일로 수동 바로가기 생성:")
    print(f"   1. run_app.bat 파일을 찾기 (C:\\Users\\lotus\\DemoCreate\\run_app.bat)")
    print(f"   2. 오른쪽 클릭 > '바로가기 만들기'")
    print(f"   3. 생성된 바로가기를 바탕화면으로 이동")


def create_shortcut_macos():
    """macOS 단축키 생성"""
    print("\n[macOS] Automator를 사용하여 단축키 생성:")
    print("   1. Automator 열기")
    print("   2. 새 문서 > '빠른 동작' 선택")
    print("   3. '셸 스크립트 실행' 추가")
    print("   4. 다음 코드 입력:")
    print("      cd /Users/lotus/DemoCreate && python -m streamlit run app.py")
    print("   5. 저장하고 원하는 단축키 지정")


if __name__ == '__main__':
    print("=" * 70)
    print("  T³ Demo Configurator - 바로가기 생성 스크립트")
    print("=" * 70)

    # Windows 확인
    if sys.platform == 'win32':
        print("\n[Windows] 바로가기 생성을 시도합니다...")
        success = create_shortcut_windows()

        if not success:
            print("\n대체 방법을 사용하세요:")
            create_alternative_shortcut()

    elif sys.platform == 'darwin':
        print("\n[macOS] 단축키 생성 가이드:")
        create_shortcut_macos()

    else:
        print("\n[Linux] 다음 명령어를 terminal에서 실행하세요:")
        print("   python -m streamlit run app.py")

    print("\n" + "=" * 70)
