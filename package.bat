@echo off
chcp 65001 > nul
:: 高级打包脚本
pyinstaller --onefile --windowed --noconsole ^
--name "图片信息收集" ^
reminder_app.py

echo.
echo 构建完成！可执行文件位于 dist 目录下
echo 文件名称：图片信息收集.exe
echo.
pause