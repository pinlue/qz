Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass


function Start-NewPowerShellWindow($command) {
    Start-Process powershell.exe -ArgumentList "-NoExit", "-Command $command"
}

# Start celery worker
Start-NewPowerShellWindow "celery -A qz worker -l info --pool=solo"
Start-Sleep -Seconds 5

# Start celery beat
Start-NewPowerShellWindow "celery -A qz beat -l info --schedule celery/celerybeat-schedule"
Start-Sleep -Seconds 5

# Start Flower
Start-NewPowerShellWindow "celery -A qz flower"
