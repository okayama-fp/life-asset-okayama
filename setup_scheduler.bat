@echo off
chcp 65001 > nul
echo ========================================
echo  タスクスケジューラ 自動登録
echo  毎月1日 午前9:00 に自動整理を実行します
echo ========================================
echo.

:: 管理者権限チェック
net session > nul 2>&1
if errorlevel 1 (
    echo [エラー] このスクリプトは管理者として実行してください。
    echo ファイルを右クリック →「管理者として実行」を選んでください。
    pause
    exit /b 1
)

set TASK_NAME=写真動画自動整理
set BAT_PATH=%~dp0run_organize.bat

:: 既存タスクがあれば削除
schtasks /delete /tn "%TASK_NAME%" /f > nul 2>&1

:: タスク登録（毎月1日 09:00）
schtasks /create ^
  /tn "%TASK_NAME%" ^
  /tr "\"%BAT_PATH%\"" ^
  /sc MONTHLY ^
  /d 1 ^
  /st 09:00 ^
  /ru "%USERNAME%" ^
  /rl HIGHEST ^
  /f

if errorlevel 1 (
    echo.
    echo [エラー] タスクの登録に失敗しました。
) else (
    echo.
    echo [完了] タスクを登録しました。
    echo   タスク名 : %TASK_NAME%
    echo   実行時刻 : 毎月1日 午前9:00
    echo   実行内容 : %BAT_PATH%
    echo.
    echo タスクスケジューラで確認・変更できます。
    echo （スタートメニュー →「タスクスケジューラ」で検索）
)

echo.
pause
