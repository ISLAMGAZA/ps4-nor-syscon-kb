# publish.ps1 - Publish ps4-nor-syscon-kb to GitHub.
# Run this AFTER: (1) installing GitHub CLI, (2) `gh auth login`, (3) creating a FRESH fine-grained PAT.
# This script contains NO secrets. It relies on your local `gh` credentials.
$ErrorActionPreference = "Stop"
$repo = "ISLAMGAZA/ps4-nor-syscon-kb"
$here = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host "==> Creating repo + pushing (public)..." -ForegroundColor Cyan
gh repo create $repo --public --source "." --remote origin --push `
    --description "PS4 NOR/Syscon repair knowledge base (English + Arabic). Community-driven fault corpus and tools."

Write-Host "==> Enabling Discussions..." -ForegroundColor Cyan
gh api -X PATCH "repos/$repo" -f has_discussions=true | Out-Null

Write-Host "==> Setting topics..." -ForegroundColor Cyan
gh api -X PUT "repos/$repo/topics" -H "Accept: application/vnd.github+json" `
    -f "names[]=ps4" -f "names[]=ps4-repair" -f "names[]=nor" -f "names[]=syscon" `
    -f "names[]=bios" -f "names[]=knowledge-base" -f "names[]=repair" | Out-Null

Write-Host "==> Creating Release v1.0 with the GUI exe..." -ForegroundColor Cyan
$exe = "C:\6\dist\PS4_NOR_EASYTOOL_V1_GUI.exe"
if (-not (Test-Path $exe)) { Write-Host "ERROR: exe not found at $exe" -ForegroundColor Red; exit 1 }
$notes = Join-Path $here "..\RELEASE_NOTES.md"
gh release create v1.0 $exe `
    --title "PS4 NOR EASYTOOL V1 (GUI)" `
    --notes-file $notes

Write-Host "DONE. Repo: https://github.com/$repo" -ForegroundColor Green
