param(
    [string]$ProjectRoot = "C:\Users\juanc\Documents\GitHub\proyecto-de-ventas-dyunic",
    [string]$PythonPath = "",
    [ValidateSet("auto", "onedrive", "desktop")]
    [string]$Source = "auto",
    [switch]$SkipGitSync
)

$ErrorActionPreference = "Stop"

$LogDir = Join-Path $ProjectRoot "logs"
$LogPath = Join-Path $LogDir "sincronizacion_excel.log"
$DesktopScriptPath = Join-Path $ProjectRoot "scripts de limpieza\sincronizar_tablas_excel.py"
$OneDriveScriptPath = Join-Path $ProjectRoot "scripts de limpieza\sincronizar_tablas_onedrive.py"
$OneDriveConfigPath = Join-Path $ProjectRoot "scripts de limpieza\configuracion_onedrive_excel.json"

New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogLine = "[$Timestamp] $Message"
    for ($Attempt = 1; $Attempt -le 5; $Attempt++) {
        try {
            Add-Content -LiteralPath $LogPath -Value $LogLine -Encoding UTF8 -ErrorAction Stop
            return
        }
        catch {
            if ($Attempt -eq 5) {
                throw
            }
            Start-Sleep -Milliseconds (100 * $Attempt)
        }
    }
}

function Invoke-PythonSync {
    param(
        [string]$PythonExecutable,
        [string]$ScriptPath
    )

    # Windows PowerShell convierte stderr nativo en ErrorRecord. Con Stop activo
    # solo conservaba la primera linea del traceback; Continue permite capturarlo completo.
    $PreviousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $CommandOutput = @(
            & $PythonExecutable $ScriptPath --project-root $ProjectRoot --include-large 2>&1 |
                ForEach-Object { $_.ToString() }
        )
        $CommandExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $PreviousErrorActionPreference
    }

    return [pscustomobject]@{
        Output = $CommandOutput
        ExitCode = $CommandExitCode
    }
}

function Invoke-GitSync {
    Push-Location -LiteralPath $ProjectRoot
    $PreviousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $TablePathspec = ":(glob)tablas/*.csv"
        $GitStatus = @(git status --porcelain -- $TablePathspec 2>&1)
        $GitStatusExitCode = $LASTEXITCODE
        if ($GitStatusExitCode -ne 0) {
            throw "No se pudo revisar el estado de Git: $($GitStatus -join ' ')"
        }

        if ($GitStatus.Count -eq 0) {
            Write-Log "Git: no hay cambios para guardar."
            return
        }

        Write-Log "Git: cambios detectados. Preparando commit automatico."
        $GitAddOutput = @(git add -- $TablePathspec 2>&1)
        $GitAddExitCode = $LASTEXITCODE
        foreach ($Line in $GitAddOutput) {
            Write-Log "Git add: $Line"
        }
        if ($GitAddExitCode -ne 0) {
            throw "git add fallo."
        }

        $CommitMessage = "Actualiza tablas desde OneDrive $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
        $GitCommitOutput = @(git commit -m $CommitMessage 2>&1)
        $GitCommitExitCode = $LASTEXITCODE
        foreach ($Line in $GitCommitOutput) {
            Write-Log "Git commit: $Line"
        }
        if ($GitCommitExitCode -ne 0) {
            throw "git commit fallo."
        }

        $GitPushOutput = @(git push origin main 2>&1)
        $GitPushExitCode = $LASTEXITCODE
        foreach ($Line in $GitPushOutput) {
            Write-Log "Git push: $Line"
        }
        if ($GitPushExitCode -ne 0) {
            throw "git push fallo."
        }

        Write-Log "Git: cambios subidos correctamente a origin/main."
    }
    finally {
        $ErrorActionPreference = $PreviousErrorActionPreference
        Pop-Location
    }
}

try {
    Write-Log "Inicio sincronizacion Excel -> Streamlit"

    if ([string]::IsNullOrWhiteSpace($PythonPath)) {
        $PythonPath = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    }

    if (-not (Test-Path -LiteralPath $PythonPath)) {
        $PythonPath = "python"
        Write-Log "Python del entorno del proyecto no encontrado. Usando python del PATH."
    }

    $UseOneDrive = $false
    if ($Source -eq "onedrive") {
        $UseOneDrive = $true
    }
    elseif ($Source -eq "auto" -and (Test-Path -LiteralPath $OneDriveConfigPath)) {
        $UseOneDrive = $true
    }

    if ($UseOneDrive) {
        Write-Log "Fuente seleccionada: OneDrive"
        $SyncResult = Invoke-PythonSync -PythonExecutable $PythonPath -ScriptPath $OneDriveScriptPath
        $Output = $SyncResult.Output
        $ExitCode = $SyncResult.ExitCode
    }
    else {
        Write-Log "Fuente seleccionada: Excel de escritorio"
        $SyncResult = Invoke-PythonSync -PythonExecutable $PythonPath -ScriptPath $DesktopScriptPath
        $Output = $SyncResult.Output
        $ExitCode = $SyncResult.ExitCode
    }

    if ($ExitCode -ne 0 -and $Source -eq "auto" -and $UseOneDrive) {
        foreach ($Line in $Output) {
            Write-Log $Line
        }
        Write-Log "OneDrive fallo en modo auto. Intentando respaldo con Excel de escritorio."
        $SyncResult = Invoke-PythonSync -PythonExecutable $PythonPath -ScriptPath $DesktopScriptPath
        $Output = $SyncResult.Output
        $ExitCode = $SyncResult.ExitCode
    }

    foreach ($Line in $Output) {
        Write-Log $Line
    }

    if ($ExitCode -ne 0) {
        throw "La sincronizacion termino con codigo $ExitCode."
    }

    Write-Log "Sincronizacion completada correctamente"

    if ($SkipGitSync) {
        Write-Log "Git: sincronizacion omitida por parametro SkipGitSync."
    }
    else {
        Invoke-GitSync
    }
}
catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    exit 1
}
