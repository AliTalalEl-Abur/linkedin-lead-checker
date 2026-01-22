# Test script for usage control

Write-Host "Starting usage control test..." -ForegroundColor Cyan

# Login
Write-Host "`n1. Login as free user..." -ForegroundColor Yellow
$loginResponse = curl.exe -s -X POST "http://localhost:8000/auth/login" `
    -H "Content-Type: application/json" `
    -d '{"email":"freeuser@test.com"}' | ConvertFrom-Json

$token = $loginResponse.access_token
Write-Host "   Token received: $($token.Substring(0,30))..." -ForegroundColor Green

# Get user info
Write-Host "`n2. Get user info..." -ForegroundColor Yellow
$meResponse = curl.exe -s "http://localhost:8000/me" `
    -H "Authorization: Bearer $token" | ConvertFrom-Json

Write-Host "   Plan: $($meResponse.plan)" -ForegroundColor White
Write-Host "   Limit: $($meResponse.usage.limit)" -ForegroundColor White
Write-Host "   Used: $($meResponse.usage.used)" -ForegroundColor White
Write-Host "   Remaining: $($meResponse.usage.remaining)" -ForegroundColor White

# Make analyses
$limit = $meResponse.usage.limit
Write-Host "`n3. Making $limit analyses..." -ForegroundColor Yellow

for ($i = 1; $i -le $limit; $i++) {
    $analyzeResponse = curl.exe -s -X POST "http://localhost:8000/analyze/profile" `
        -H "Content-Type: application/json" `
        -H "Authorization: Bearer $token" `
        -d '{"linkedin_profile_data":{"name":"Test"}}' | ConvertFrom-Json
    
    Write-Host "   [$i/$limit] Score: $($analyzeResponse.score), Remaining: $($analyzeResponse.usage_remaining)" -ForegroundColor Green
}

# Try to exceed limit
Write-Host "`n4. Trying to exceed limit..." -ForegroundColor Yellow
$response = curl.exe -s -w "%{http_code}" -X POST "http://localhost:8000/analyze/profile" `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer $token" `
    -d '{"linkedin_profile_data":{"name":"Test"}}'

if ($response -match "402") {
    Write-Host "   SUCCESS: Got 402 Payment Required!" -ForegroundColor Green
} else {
    Write-Host "   FAIL: Expected 402, got other response" -ForegroundColor Red
}

Write-Host "`nTest complete!" -ForegroundColor Cyan
