# 2webm Setup Script
Write-Host "2webm - Setup Utility"
Write-Host "==========================="

# Set TLS 1.2 for all HTTPS connections
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Create required directories
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonDir = Join-Path $scriptPath "python"
$ffmpegDir = Join-Path $scriptPath "ffmpeg"
$ffmpegBinDir = Join-Path $ffmpegDir "bin"
$outputDir = Join-Path $scriptPath "output"

# Create directories if they don't exist
if (-not (Test-Path $pythonDir)) {
    New-Item -ItemType Directory -Path $pythonDir | Out-Null
}
if (-not (Test-Path $ffmpegBinDir -PathType Container)) {
    New-Item -ItemType Directory -Path $ffmpegBinDir -Force | Out-Null
}
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

# Download embedded Python
Write-Host "Downloading Python embedded package..."
$pythonUrl = "https://www.python.org/ftp/python/3.9.10/python-3.9.10-embed-amd64.zip"
$pythonZip = Join-Path $scriptPath "python_embed.zip"

try {
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonZip -UseBasicParsing
    Write-Host "Download complete"
    
    # Extract Python
    Write-Host "Extracting Python..."
    Expand-Archive -Path $pythonZip -DestinationPath $pythonDir -Force
    Write-Host "Extraction complete"
    
    # Download and install pip
    Write-Host "Setting up pip..."
    $getPipUrl = "https://bootstrap.pypa.io/get-pip.py"
    $getPipPath = Join-Path $pythonDir "get-pip.py"
    Invoke-WebRequest -Uri $getPipUrl -OutFile $getPipPath -UseBasicParsing
    
    # Edit python39._pth file to enable site-packages
    $pthPath = Join-Path $pythonDir "python39._pth"
    if (Test-Path $pthPath) {
        $content = Get-Content $pthPath
        $updatedContent = $content -replace '#import site', 'import site'
        Set-Content -Path $pthPath -Value $updatedContent
    }
    
    # Install pip
    $pythonExe = Join-Path $pythonDir "python.exe"
    Start-Process -FilePath $pythonExe -ArgumentList $getPipPath -Wait
    
    # Cleanup
    Remove-Item $pythonZip -Force
    Remove-Item $getPipPath -Force
} catch {
    Write-Host "ERROR: Failed to download or extract Python"
    Write-Host "Error details: $_"
    Write-Host "Please download Python manually and extract to the 'python' directory:"
    Write-Host "https://www.python.org/downloads/"
    Read-Host "Press any key to continue"
    exit 1
}

# Download FFmpeg
Write-Host "Downloading FFmpeg..."
$ffmpegUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
$ffmpegZip = Join-Path $scriptPath "ffmpeg.zip"

try {
    Invoke-WebRequest -Uri $ffmpegUrl -OutFile $ffmpegZip -UseBasicParsing
    Write-Host "Download complete"
    
    # Extract
    Write-Host "Extracting FFmpeg..."
    Expand-Archive -Path $ffmpegZip -DestinationPath $scriptPath -Force
    
    # Move necessary files
    Write-Host "Moving necessary files..."
    $extractedDir = Join-Path $scriptPath "ffmpeg-master-latest-win64-gpl"
    Copy-Item "$extractedDir\bin\*" -Destination $ffmpegBinDir -Recurse -Force
    
    # Remove unnecessary files
    Write-Host "Removing unnecessary files..."
    Remove-Item $extractedDir -Recurse -Force
    Remove-Item $ffmpegZip -Force
} catch {
    Write-Host "ERROR: Failed to download or extract FFmpeg"
    Write-Host "Error details: $_"
    Write-Host "Please download manually and place in ffmpeg/bin directory: https://ffmpeg.org/download.html"
    Read-Host "Press any key to continue"
    exit 1
}

# Install required libraries (not needed for Tkinter as it's built into Python)
Write-Host "Python embedded package is ready to use"

Write-Host ""
Write-Host "Setup complete!"
Write-Host "Run 2webm.bat to start the application"
Read-Host "Press any key to continue" 