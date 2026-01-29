# Pre-Deploy Checklist Script
# Run this before deploying to Vercel

Write-Host "🔍 Verificando configuración para Vercel Deploy..." -ForegroundColor Cyan
Write-Host ""

$errors = 0
$warnings = 0

# Check 1: Verify we're in the web directory
Write-Host "✓ Verificando directorio..." -ForegroundColor Yellow
if (Test-Path "package.json") {
    $pkg = Get-Content "package.json" | ConvertFrom-Json
    if ($pkg.name -eq "linkedin-lead-checker-web") {
        Write-Host "  ✅ Directorio correcto: web/" -ForegroundColor Green
    } else {
        Write-Host "  ❌ ERROR: No estás en el directorio web/" -ForegroundColor Red
        $errors++
    }
} else {
    Write-Host "  ❌ ERROR: package.json no encontrado" -ForegroundColor Red
    $errors++
}

# Check 2: Verify Next.js version
Write-Host ""
Write-Host "✓ Verificando Next.js..." -ForegroundColor Yellow
if (Test-Path "package.json") {
    $pkg = Get-Content "package.json" | ConvertFrom-Json
    if ($pkg.dependencies.next) {
        Write-Host "  ✅ Next.js version: $($pkg.dependencies.next)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ ERROR: Next.js no encontrado en dependencias" -ForegroundColor Red
        $errors++
    }
}

# Check 3: Verify build command
Write-Host ""
Write-Host "✓ Verificando build command..." -ForegroundColor Yellow
if (Test-Path "package.json") {
    $pkg = Get-Content "package.json" | ConvertFrom-Json
    if ($pkg.scripts.build -eq "next build") {
        Write-Host "  ✅ Build command: next build" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  WARNING: Build command inesperado: $($pkg.scripts.build)" -ForegroundColor Yellow
        $warnings++
    }
}

# Check 4: Verify vercel.json exists
Write-Host ""
Write-Host "✓ Verificando vercel.json..." -ForegroundColor Yellow
if (Test-Path "vercel.json") {
    $vercel = Get-Content "vercel.json" | ConvertFrom-Json
    Write-Host "  ✅ vercel.json encontrado" -ForegroundColor Green
    if ($vercel.framework -eq "nextjs") {
        Write-Host "  ✅ Framework: Next.js" -ForegroundColor Green
    }
} else {
    Write-Host "  ⚠️  WARNING: vercel.json no encontrado (auto-detección)" -ForegroundColor Yellow
    $warnings++
}

# Check 5: Verify .env.example exists
Write-Host ""
Write-Host "✓ Verificando .env.example..." -ForegroundColor Yellow
if (Test-Path ".env.example") {
    Write-Host "  ✅ .env.example encontrado" -ForegroundColor Green
    $envContent = Get-Content ".env.example"
    if ($envContent -match "NEXT_PUBLIC_API_URL") {
        Write-Host "  ✅ NEXT_PUBLIC_API_URL documentado" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  WARNING: NEXT_PUBLIC_API_URL no documentado" -ForegroundColor Yellow
        $warnings++
    }
} else {
    Write-Host "  ⚠️  WARNING: .env.example no encontrado" -ForegroundColor Yellow
    $warnings++
}

# Check 6: Verify public folder
Write-Host ""
Write-Host "✓ Verificando archivos públicos..." -ForegroundColor Yellow
if (Test-Path "public") {
    Write-Host "  ✅ Directorio public/ existe" -ForegroundColor Green
    
    if (Test-Path "public/robots.txt") {
        Write-Host "  ✅ robots.txt encontrado" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  WARNING: robots.txt no encontrado" -ForegroundColor Yellow
        $warnings++
    }
    
    if (Test-Path "public/sitemap.xml") {
        Write-Host "  ✅ sitemap.xml encontrado" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  WARNING: sitemap.xml no encontrado" -ForegroundColor Yellow
        $warnings++
    }
} else {
    Write-Host "  ❌ ERROR: Directorio public/ no encontrado" -ForegroundColor Red
    $errors++
}

# Check 7: Run build test
Write-Host ""
Write-Host "✓ Probando build..." -ForegroundColor Yellow
Write-Host "  Ejecutando: npm run build" -ForegroundColor Gray

$buildOutput = npm run build 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Build exitoso" -ForegroundColor Green
} else {
    Write-Host "  ❌ ERROR: Build falló" -ForegroundColor Red
    Write-Host $buildOutput -ForegroundColor Red
    $errors++
}

# Check 8: Verify no loopback references
Write-Host ""
$loopbackHostPattern = "local" + "host"
$loopbackIpPattern = "127.0.0." + "1"
Write-Host "✓ Verificando referencias a loopback..." -ForegroundColor Yellow
$loopbackFiles = Get-ChildItem -Path "pages","components","lib" -Recurse -Include "*.js","*.jsx","*.ts","*.tsx" -ErrorAction SilentlyContinue | 
    Select-String -Pattern "${loopbackHostPattern}|${loopbackIpPattern}" -AllMatches
    
if ($loopbackFiles) {
    Write-Host "  ⚠️  WARNING: Referencias hardcodeadas a loopback encontradas:" -ForegroundColor Yellow
    $loopbackFiles | ForEach-Object {
        Write-Host "    - $($_.Filename):$($_.LineNumber)" -ForegroundColor Yellow
    }
    $warnings++
} else {
    Write-Host "  ✅ Sin referencias hardcodeadas a loopback" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📊 RESUMEN" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($errors -eq 0 -and $warnings -eq 0) {
    Write-Host "✅ ¡TODO LISTO PARA DEPLOY!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Siguiente paso:" -ForegroundColor Cyan
    Write-Host "  vercel" -ForegroundColor White
    Write-Host ""
    Write-Host "O desde el dashboard:" -ForegroundColor Cyan
    Write-Host "  https://vercel.com/new" -ForegroundColor White
    exit 0
} elseif ($errors -eq 0) {
    Write-Host "⚠️  ADVERTENCIAS: $warnings" -ForegroundColor Yellow
    Write-Host "Puedes deployar, pero revisa los warnings arriba." -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "❌ ERRORES: $errors" -ForegroundColor Red
    Write-Host "⚠️  ADVERTENCIAS: $warnings" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Por favor corrige los errores antes de deployar." -ForegroundColor Red
    exit 1
}
