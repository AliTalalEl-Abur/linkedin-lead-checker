#!/usr/bin/env pwsh
# Test del sistema de tracking
# Este script prueba los endpoints de tracking de forma simple

Write-Host "🧪 Testing LinkedIn Lead Checker - Tracking System" -ForegroundColor Cyan
Write-Host "=" -repeat 60 -ForegroundColor Gray
Write-Host ""

# Configuración
$API_URL = $env:BACKEND_URL
$HEADERS = @{
    "Content-Type" = "application/json"
}

# Test 1: Evento de instalación
Write-Host "📦 Test 1: Install Extension Click Event" -ForegroundColor Yellow
$body1 = @{
    event = "install_extension_click"
    page = "landing"
    referrer = "https://google.com"
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Uri "$API_URL/events/track" -Method POST -Headers $HEADERS -Body $body1
    Write-Host "✅ Success!" -ForegroundColor Green
    Write-Host "   Status: $($response1.status)" -ForegroundColor Gray
    Write-Host "   Event: $($response1.event)" -ForegroundColor Gray
    Write-Host "   Time: $($response1.timestamp)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 2: Evento de waitlist
Write-Host "📧 Test 2: Join Waitlist Event" -ForegroundColor Yellow
$body2 = @{
    event = "waitlist_join"
    page = "landing"
    referrer = $null
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "$API_URL/events/track" -Method POST -Headers $HEADERS -Body $body2
    Write-Host "✅ Success!" -ForegroundColor Green
    Write-Host "   Status: $($response2.status)" -ForegroundColor Gray
    Write-Host "   Event: $($response2.event)" -ForegroundColor Gray
    Write-Host "   Time: $($response2.timestamp)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 3: Evento desde sección "how-it-works"
Write-Host "🔄 Test 3: Install Click from How-It-Works Section" -ForegroundColor Yellow
$body3 = @{
    event = "install_extension_click"
    page = "how-it-works"
    referrer = "https://linkedin.com"
} | ConvertTo-Json

try {
    $response3 = Invoke-RestMethod -Uri "$API_URL/events/track" -Method POST -Headers $HEADERS -Body $body3
    Write-Host "✅ Success!" -ForegroundColor Green
    Write-Host "   Status: $($response3.status)" -ForegroundColor Gray
    Write-Host "   Event: $($response3.event)" -ForegroundColor Gray
    Write-Host "   Time: $($response3.timestamp)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=" -repeat 60 -ForegroundColor Gray
Write-Host "✅ Tracking tests completed!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Cyan
Write-Host "   - Check backend logs to see the EVENT_TRACK entries" -ForegroundColor Gray
Write-Host "   - Open browser DevTools → Network to see tracking calls" -ForegroundColor Gray
Write-Host "   - Events are fire-and-forget (non-blocking)" -ForegroundColor Gray
Write-Host ""
