# Script PowerShell para criar tarefa agendada no Windows
# Execute como Administrador

$TaskName = "CaixaForte_ProfessorPardal"
$Description = "Executa o Professor Pardal para processar notas de corretagem"
$ScriptPath = Join-Path $PSScriptRoot "executar_agora.bat"

# Configurar trigger para 10:00 todos os dias
$Trigger = New-ScheduledTaskTrigger -Daily -At 10:00AM

# Configurar ação
$Action = New-ScheduledTaskAction -Execute $ScriptPath -WorkingDirectory $PSScriptRoot

# Configurar settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Remover tarefa existente se houver
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# Criar nova tarefa
Register-ScheduledTask -TaskName $TaskName -Description $Description -Trigger $Trigger -Action $Action -Settings $Settings -User $env:USERNAME

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Tarefa agendada criada com sucesso!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Nome: $TaskName"
Write-Host "Horario: 10:00 todos os dias"
Write-Host ""
Write-Host "Para verificar: Abra o 'Agendador de Tarefas' do Windows"
Write-Host ""
