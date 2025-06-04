@echo off
echo =========================================
echo 港股成交量筛选分析系统 - Streamlit版本
echo =========================================
echo.
echo 正在启动Web应用...
echo 浏览器将自动打开 http://localhost:8501
echo.
echo 如需退出，请按 Ctrl+C
echo.

cd /d "%~dp0"
streamlit run streamlit_app.py

pause 