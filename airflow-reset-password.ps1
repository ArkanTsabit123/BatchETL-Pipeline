# airflow-reset-password.ps1
# DESCRIPTION: Resets Airflow admin password to 'admin' for the BatchETL Pipeline

<#
.SYNOPSIS
    Resets the Airflow admin user password to 'admin'

.DESCRIPTION
    This script connects to the running Airflow container, deletes the existing
    admin user if present, and creates a new admin user with password 'admin'.
    This is useful when Airflow Standalone generates a random password.

.EXAMPLE
    .\airflow-reset-password.ps1
    Resets password and displays confirmation message

.NOTES
    Requires Docker to be running and Airflow container to be up
#>

function Test-DockerRunning {
    <#
    .SYNOPSIS
        Checks if Docker daemon is running
    .OUTPUTS
        bool - True if Docker is running, False otherwise
    #>
    try {
        $dockerCheck = docker info 2>&1
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
        return $false
    }
    catch {
        return $false
    }
}

function Test-ContainerRunning {
    <#
    .SYNOPSIS
        Checks if Airflow container is running
    .OUTPUTS
        bool - True if container is running, False otherwise
    #>
    param(
        [string]$ContainerName = "batch-etl-airflow"
    )
    
    try {
        $containerStatus = docker inspect -f '{{.State.Status}}' $ContainerName 2>&1
        if ($LASTEXITCODE -eq 0 -and $containerStatus -eq "running") {
            return $true
        }
        return $false
    }
    catch {
        return $false
    }
}

function Reset-AirflowPassword {
    <#
    .SYNOPSIS
        Resets Airflow admin password to 'admin'
    .OUTPUTS
        int - Exit code (0 for success, 1 for failure)
    #>
    param(
        [string]$ContainerName = "batch-etl-airflow",
        [string]$Username = "admin",
        [string]$Password = "admin"
    )
    
    $command = @"
airflow users delete -u $Username 2>/dev/null; 
airflow users create \
    --username $Username \
    --password $Password \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
"@
    
    $fullCommand = "bash -c `"$command`""
    $result = docker exec -it $ContainerName $fullCommand
    
    return $LASTEXITCODE
}

function Main {
    Write-Host "[INFO] Resetting Airflow password..." -ForegroundColor Yellow
    
    if (-not (Test-DockerRunning)) {
        Write-Host "[ERROR] Docker is not running. Please start Docker Desktop." -ForegroundColor Red
        return 1
    }
    
    if (-not (Test-ContainerRunning)) {
        Write-Host "[ERROR] Airflow container is not running. Please run docker-compose up -d" -ForegroundColor Red
        return 1
    }
    
    $exitCode = Reset-AirflowPassword
    
    if ($exitCode -eq 0) {
        Write-Host "[SUCCESS] Password reset completed successfully." -ForegroundColor Green
        Write-Host "[INFO] Airflow UI: http://localhost:8080" -ForegroundColor Cyan
        Write-Host "[INFO] Username: admin" -ForegroundColor Cyan
        Write-Host "[INFO] Password: admin" -ForegroundColor Cyan
        return 0
    }
    else {
        Write-Host "[ERROR] Failed to reset password. Exit code: $exitCode" -ForegroundColor Red
        return 1
    }
}

Main
exit $LASTEXITCODE