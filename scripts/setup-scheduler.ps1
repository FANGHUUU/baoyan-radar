# 保研雷达 - Windows 任务计划程序安装脚本
# 每天上午 8:03 自动搜索更新夏令营信息
# 以管理员身份运行此脚本

$ErrorActionPreference = "Stop"
$TaskName = "BaoyanRadarDailyUpdate"
$ScriptPath = "$PSScriptRoot\daily-run.ps1"

# 检查脚本是否存在
if (-not (Test-Path $ScriptPath)) {
    Write-Error "找不到 daily-run.ps1: $ScriptPath"
    exit 1
}

# 删除已有同名任务
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "删除已有任务: $TaskName"
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# 创建任务操作
$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ScriptPath`""

# 创建触发器: 每天 08:03
$Trigger = New-ScheduledTaskTrigger -Daily -At "08:03"

# 创建任务配置: 允许在电池模式下运行, 错过后尽快运行, 不强制停止
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 10)

# 注册任务 (以当前用户身份运行)
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "保研夏令营及预推免信息雷达 - 每日自动搜索更新"

Write-Host "✓ 任务计划已安装!"
Write-Host "  任务名称: $TaskName"
Write-Host "  运行时间: 每天 08:03"
Write-Host "  运行脚本: $ScriptPath"
Write-Host ""
Write-Host "管理命令:"
Write-Host "  查看: Get-ScheduledTask -TaskName $TaskName"
Write-Host "  手动运行: Start-ScheduledTask -TaskName $TaskName"
Write-Host "  删除: Unregister-ScheduledTask -TaskName $TaskName -Confirm:`$false"
Write-Host "  查看历史: Get-WinEvent -LogName 'Microsoft-Windows-TaskScheduler/Operational' | Where-Object {`$_.Message -like '*$TaskName*'} | Select-Object -First 20"
