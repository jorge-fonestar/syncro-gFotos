# Script de sincronización de Google Photos usando rclone
# Ejecuta: .\sync.ps1

Write-Host "Iniciando sincronización de Google Photos..." -ForegroundColor Green

rclone sync syncro-gPhotos:media "\\Nas-home\cloud_data\gFotos\ (Yorch)" `
    --progress `
    --log-file "sync_log.txt" `
    --log-level INFO `
    --transfers 4 `
    --verbose

Write-Host "`nSincronización completada!" -ForegroundColor Green
Write-Host "Log guardado en sync_log.txt" -ForegroundColor Yellow
