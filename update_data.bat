@echo off
cd /d "%~dp0"
echo [*] データキャッシュを削除中...
rmdir /s /q "クロスモールCSV" >nul 2>&1
echo [OK] 削除完了！
echo.
echo [*] アプリを起動します...
echo.
streamlit run main_process.py
pause
