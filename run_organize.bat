@echo off
chcp 65001 > nul
echo ========================================
echo  写真・動画 自動整理スクリプト
echo ========================================

:: Pythonが入っているか確認
python --version > nul 2>&1
if errorlevel 1 (
    echo [エラー] Python が見つかりません。
    echo https://www.python.org からインストールしてください。
    pause
    exit /b 1
)

:: Pillowが入っていなければ自動インストール
python -c "import PIL" > nul 2>&1
if errorlevel 1 (
    echo Pillow をインストールします...
    pip install Pillow -q
)

:: スクリプトの場所（このバッチファイルと同じフォルダ）
set SCRIPT=%~dp0organize_photos.py

:: 実行
echo.
python "%SCRIPT%"

echo.
echo 完了しました。
timeout /t 5
