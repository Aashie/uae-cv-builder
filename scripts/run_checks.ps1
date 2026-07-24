$ErrorActionPreference = "Stop"

Write-Host "== UAE CV Builder checks =="

Write-Host ""
Write-Host "== Initial git status =="
git status --short

Write-Host ""
Write-Host "== Pytest =="
.\venv\Scripts\python.exe -m pytest -q

Write-Host ""
Write-Host "== Final git status =="
git status --short
