$ErrorActionPreference = "Stop"

# Build a standalone Windows GUI executable (no console window).
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot

python -m pip install -r requirements.txt
python -m pip install pyinstaller

python -m PyInstaller --clean --noconsole --onefile --name "ServiceDeskManager" --icon "icons\scotiabank_logo_icon_170755.png" --add-data "templates;templates" --add-data "icons;icons" --add-data "output;output" --add-data "logs;logs" "app.py"

Pop-Location

Write-Host "Build complete. Output: dist\ServiceDeskManager.exe"
