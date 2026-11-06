# Windows PowerShell 5.1 compatible. Dry-run by default. Never overwrites an existing repository.
[CmdletBinding()]
param([switch] $Publish, [switch] $StartBuild)
$ErrorActionPreference = 'Stop'
$repo = 'Yasora-Labs/Yasora-Markdown-Studio'
if ($StartBuild -and -not $Publish) { throw 'StartBuild requires -Publish; preview mode cannot trigger build jobs.' }
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
Write-Host 'Yasora Markdown Studio — GitHub publication preflight' -ForegroundColor Cyan
foreach ($path in @('README.md','.gitignore','LICENSE','handoff.md','.github\workflows\build-release.yml','src\yasora_studio\app.py','android\app\build.gradle')) {
    if (-not (Test-Path -LiteralPath (Join-Path $root $path) -PathType Leaf)) { throw "Missing project source: $path" }
}
foreach ($exe in @('git.exe','gh.exe')) {
    if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) { throw "Required tool missing: $exe" }
}
& gh.exe auth status
if ($LASTEXITCODE -ne 0) { throw 'GitHub CLI must be authenticated with repository creation rights for Yasora-Labs.' }
& gh.exe repo view $repo --json name | Out-Null
if ($LASTEXITCODE -eq 0) { throw "$repo already exists. Refusing to overwrite. Use a separate reviewed update workflow." }
Write-Host "Proposed new PUBLIC repo: $repo"
Write-Host "Source directory: $root"
Write-Host 'No user documents, binary dependencies, or local keys should be included.'
if (-not $Publish) {
    Write-Host 'PREVIEW ONLY. Review source and licenses. Re-run with -Publish to create a public repo.' -ForegroundColor Yellow
    return
}
if (Test-Path -LiteralPath (Join-Path $root '.git')) { throw 'This directory is already a git checkout. Refusing to change remotes.' }
$author = & git.exe config --global user.name
$email = & git.exe config --global user.email
if ([string]::IsNullOrWhiteSpace($author) -or [string]::IsNullOrWhiteSpace($email)) { throw 'Configure Git commit identity first (git config --global user.name / user.email).' }
& git.exe init -b main
if ($LASTEXITCODE -ne 0) { throw 'git init failed' }
& git.exe add --all
if ($LASTEXITCODE -ne 0) { throw 'git add failed' }
Write-Host 'Files staged for publication:' -ForegroundColor Cyan
& git.exe diff --cached --name-only
& git.exe diff --cached --check
if ($LASTEXITCODE -ne 0) { throw 'git staged diff check failed' }
& git.exe commit -m 'Initial cross-platform alpha source and draft release pipeline'
if ($LASTEXITCODE -ne 0) { throw 'git commit failed' }
Write-Host 'Creating PUBLIC repository in Yasora-Labs. This is not a dry run.' -ForegroundColor Yellow
& gh.exe repo create $repo --public --source . --remote origin --push
if ($LASTEXITCODE -ne 0) { throw 'GitHub creation/push failed. Inspect local git state and gh permissions; do not re-run blindly.' }
Write-Host "Published source to https://github.com/$repo" -ForegroundColor Green
if ($StartBuild) {
    Write-Host 'Requesting native builds in GitHub Actions...'
    & gh.exe workflow run 'build-release.yml' --repo $repo --ref main
    if ($LASTEXITCODE -ne 0) { throw 'Repository created, but starting Actions failed. Start workflow manually from GitHub Actions.' }
    Write-Host 'Build workflow requested. Review Actions results and download the generated installer artifacts.' -ForegroundColor Green
} else {
    Write-Host 'Next: run Build all platform installers in GitHub Actions. Do NOT mark a release stable until native QA passes.'
}
