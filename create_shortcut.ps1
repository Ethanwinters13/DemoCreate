# 바탕화면 바로가기 생성 스크립트
# 관리자 권한으로 실행 필요

$DesktopPath = [System.IO.Path]::Combine($env:USERPROFILE, "Desktop")
$ShortcutPath = [System.IO.Path]::Combine($DesktopPath, "T3 Demo Configurator.lnk")
$BatchFilePath = "C:\Users\lotus\DemoCreate\run_app.bat"

# COM 객체 생성
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)

# 바로가기 설정
$Shortcut.TargetPath = $BatchFilePath
$Shortcut.WorkingDirectory = "C:\Users\lotus\DemoCreate"
$Shortcut.Description = "T³ Demo Configurator - Streamlit 애플리케이션"
$Shortcut.IconLocation = "C:\Windows\System32\cmd.exe,0"  # cmd.exe 아이콘

# 바로가기 저장
$Shortcut.Save()

Write-Host "✅ 바로가기 생성 완료!"
Write-Host "위치: $ShortcutPath"
Write-Host ""
Write-Host "바탕화면의 'T3 Demo Configurator' 아이콘을 더블클릭하면 앱이 실행됩니다."
