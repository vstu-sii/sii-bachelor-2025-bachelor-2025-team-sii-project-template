# scripts/test-mlops.ps1
Write-Host "== Checking Docker =="
docker --version; docker compose version

Write-Host "`n== Starting infra =="
Push-Location ".\infra"
docker compose -f .\docker-compose.dev.yml up -d

Write-Host "`n== Waiting 8s then probing endpoints =="
Start-Sleep -Seconds 8
$ok = $true
foreach ($url in @("http://localhost:8000","http://localhost:3000")) {
  try {
    $resp = Invoke-WebRequest -UseBasicParsing -Uri $url -Method Head -TimeoutSec 5
    Write-Host "$url -> $($resp.StatusCode)"
  } catch {
    Write-Warning "$url not reachable"; $ok = $false
  }
}
Pop-Location

# --- Monitoring block (modified) ---
Push-Location ".\monitoring"
docker compose up -d
Start-Sleep -Seconds 5

function ProbeGet($url) {
  try {
    $resp = Invoke-WebRequest -UseBasicParsing -Uri $url -Method Get -TimeoutSec 6
    Write-Host "$url -> $($resp.StatusCode)"; return $true
  } catch {
    Write-Warning "$url unreachable"; return $false
  }
}

$ok = (ProbeGet "http://localhost:9090/-/ready")   -and $ok
$ok = (ProbeGet "http://localhost:9090/-/healthy") -and $ok
$ok = (ProbeGet "http://localhost:3001")           -and $ok

Pop-Location
# --- end monitoring block ---

if ($ok) { Write-Host "`nALL GOOD ✅" -ForegroundColor Green } else { Write-Host "`nSome checks failed ❌" -ForegroundColor Red }

