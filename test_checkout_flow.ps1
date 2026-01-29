# Script de prueba completo del flujo Stripe Checkout
# Usa puerto 8001 (ajusta si tu servidor corre en otro)

$BASE_URL = $env:BACKEND_URL

Write-Host "`n🧪 TEST: Flujo Completo de Stripe Checkout`n" -ForegroundColor Cyan

# 1. Crear usuario y obtener token
Write-Host "1️⃣  Creando usuario de prueba..." -ForegroundColor Yellow
try {
    $loginResp = Invoke-RestMethod -Method Post `
        -Uri "$BASE_URL/auth/login" `
        -Body (@{ email = 'test-checkout@example.com' } | ConvertTo-Json) `
        -ContentType 'application/json'
    
    $TOKEN = $loginResp.access_token
    Write-Host "   ✅ Token JWT obtenido" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error al crear usuario: $_" -ForegroundColor Red
    exit 1
}

# 2. Verificar plan inicial (debe ser "free")
Write-Host "`n2️⃣  Verificando plan inicial..." -ForegroundColor Yellow
try {
    $user = Invoke-RestMethod -Method Get `
        -Uri "$BASE_URL/user" `
        -Headers @{ Authorization = "Bearer $TOKEN" }
    
    Write-Host "   📊 Plan actual: $($user.plan)" -ForegroundColor Cyan
    Write-Host "   📊 Email: $($user.email)" -ForegroundColor Cyan
    Write-Host "   📊 Uso semanal: $($user.usage.usage_this_week)/$($user.usage.weekly_limit)" -ForegroundColor Cyan
    
    if ($user.plan -ne "free") {
        Write-Host "   ⚠️  Advertencia: el plan inicial no es 'free'" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Error al obtener perfil: $_" -ForegroundColor Red
    exit 1
}

# 3. Crear sesión de checkout
Write-Host "`n3️⃣  Creando sesión de Checkout..." -ForegroundColor Yellow
try {
    $checkoutResp = Invoke-RestMethod -Method Post `
        -Uri "$BASE_URL/billing/checkout" `
        -Headers @{ Authorization = "Bearer $TOKEN" } `
        -Body (@{ return_url = "${env:NEXT_PUBLIC_SITE_URL}/billing/return?session_id={CHECKOUT_SESSION_ID}" } | ConvertTo-Json) `
        -ContentType 'application/json'
    
    Write-Host "   ✅ Sesión creada: $($checkoutResp.sessionId)" -ForegroundColor Green
    Write-Host "   🌐 URL de pago: $($checkoutResp.url)" -ForegroundColor Cyan
    Write-Host "`n   👉 Abre esta URL en tu navegador y paga con: 4242 4242 4242 4242" -ForegroundColor Yellow
    Write-Host "      (cualquier fecha futura, cualquier CVC)`n" -ForegroundColor Yellow
    
    # Copiar URL al portapapeles (opcional)
    Set-Clipboard -Value $checkoutResp.url
    Write-Host "   📋 URL copiada al portapapeles`n" -ForegroundColor Green
    
    # Pausa para que el usuario complete el pago
    Write-Host "   ⏸️  Presiona Enter después de completar el pago en el navegador..." -ForegroundColor Magenta
    Read-Host
    
} catch {
    Write-Host "   ❌ Error al crear checkout: $_" -ForegroundColor Red
    Write-Host "   💡 Verifica que STRIPE_PRO_PRICE_ID esté configurado en .env" -ForegroundColor Yellow
    exit 1
}

# 4. Verificar actualización del plan (debe ser "pro")
Write-Host "`n4️⃣  Verificando actualización de plan..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
try {
    $userUpdated = Invoke-RestMethod -Method Get `
        -Uri "$BASE_URL/user" `
        -Headers @{ Authorization = "Bearer $TOKEN" }
    
    Write-Host "   📊 Plan actual: $($userUpdated.plan)" -ForegroundColor Cyan
    Write-Host "   📊 Uso semanal: $($userUpdated.usage.usage_this_week)/$($userUpdated.usage.weekly_limit)" -ForegroundColor Cyan
    
    if ($userUpdated.plan -eq "pro") {
        Write-Host "`n   ✅ ¡ÉXITO! Plan actualizado a PRO" -ForegroundColor Green
        Write-Host "   🎉 Límite semanal aumentado de 5 a 500 análisis" -ForegroundColor Green
    } else {
        Write-Host "`n   ⚠️  Advertencia: el plan sigue siendo '$($userUpdated.plan)'" -ForegroundColor Yellow
        Write-Host "   💡 Verifica que:" -ForegroundColor Yellow
        Write-Host "      - Stripe CLI esté escuchando: stripe listen --forward-to BACKEND_URL/billing/webhook/stripe" -ForegroundColor Yellow
        Write-Host "      - STRIPE_WEBHOOK_SECRET esté correcto en .env" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Error al verificar plan: $_" -ForegroundColor Red
    exit 1
}

# 5. (Opcional) Probar Billing Portal
Write-Host "`n5️⃣  ¿Quieres probar el Billing Portal? (S/N)" -ForegroundColor Yellow
$respuesta = Read-Host
if ($respuesta -eq 'S' -or $respuesta -eq 's') {
    try {
        $portalResp = Invoke-RestMethod -Method Post `
            -Uri "$BASE_URL/billing/portal-session" `
            -Headers @{ Authorization = "Bearer $TOKEN" }
        
        Write-Host "   ✅ Portal creado" -ForegroundColor Green
        Write-Host "   🌐 URL: $($portalResp.url)" -ForegroundColor Cyan
        Write-Host "`n   👉 Abre esta URL para gestionar tu suscripción`n" -ForegroundColor Yellow
        
        Set-Clipboard -Value $portalResp.url
        Write-Host "   📋 URL copiada al portapapeles`n" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Error al crear portal: $_" -ForegroundColor Red
    }
}

Write-Host "`n✅ Test completado`n" -ForegroundColor Green
