# GitHub Repository Setup Helper
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "GitHub Repository Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$repoName = "crowd-risk-monitoring"
$username = "shangaric"
$url = "https://github.com/new?name=$repoName&description=Live+crowd+risk+monitoring+platform+with+real-time+CCTV+analysis+and+ML-based+hazard+detection"

Write-Host "Opening GitHub repository creation page..." -ForegroundColor Yellow
Write-Host "Repository will be: $username/$repoName" -ForegroundColor Green
Write-Host ""

# Open browser
Start-Process $url

Write-Host "Instructions:" -ForegroundColor Yellow
Write-Host "1. The browser should open to GitHub's new repository page" -ForegroundColor White
Write-Host "2. Repository name should be pre-filled: $repoName" -ForegroundColor White
Write-Host "3. DO NOT check 'Initialize with README'" -ForegroundColor Red
Write-Host "4. Click 'Create repository'" -ForegroundColor White
Write-Host ""
Write-Host "After creating the repository, press any key to push your code..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "Pushing code to GitHub..." -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "SUCCESS! Repository created and code pushed!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "View your repository at: https://github.com/$username/$repoName" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "ERROR: Could not push to GitHub" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "Make sure you created the repository on GitHub first." -ForegroundColor Yellow
    Write-Host "Then run: git push -u origin main" -ForegroundColor Yellow
}
