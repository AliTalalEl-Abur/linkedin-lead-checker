# Endpoint GET /billing/status

## Descripción

El endpoint `GET /billing/status` devuelve información completa sobre el estado de facturación del usuario autenticado, incluyendo su plan actual, uso de análisis, límites y capacidad para ejecutar análisis AI.

## URL

```
GET /billing/status
```

## Autenticación

Este endpoint requiere autenticación JWT. Incluye el token en el header:

```
Authorization: Bearer <token>
```

## Respuesta Exitosa

**Status Code:** `200 OK`

**Estructura de la Respuesta:**

```json
{
  "plan": "pro",
  "usage_current": 45,
  "usage_limit": 150,
  "reset_date": "2026-02-15T00:00:00Z",
  "can_analyze": true,
  "subscription_status": "active"
}
```

### Campos de la Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `plan` | `string` | Plan actual del usuario: `"free"`, `"starter"`, `"pro"`, o `"team"` |
| `usage_current` | `integer` | Número de análisis utilizados en el período actual |
| `usage_limit` | `integer` | Límite total de análisis para el plan actual |
| `reset_date` | `string \| null` | Fecha ISO 8601 cuando se reinicia el contador (solo para planes pagos). `null` para plan free |
| `can_analyze` | `boolean` | Si `true`, el usuario puede ejecutar más análisis AI. Si `false`, ha alcanzado su límite |
| `subscription_status` | `string \| null` | Estado de la suscripción Stripe: `"active"`, `"canceled"`, `"past_due"`, etc. `null` si no tiene suscripción |

## Límites por Plan

| Plan | Límite | Reset | Tipo de Contador |
|------|--------|-------|------------------|
| **Free** | 3 análisis | Nunca (lifetime) | `lifetime_analyses_count` |
| **Starter** | 40 análisis/mes | Mensual | `monthly_analyses_count` |
| **Pro** | 150 análisis/mes | Mensual | `monthly_analyses_count` |
| **Team** | 500 análisis/mes | Mensual | `monthly_analyses_count` |

## Ejemplos de Uso

### JavaScript/TypeScript (Extension o Web)

```typescript
async function checkBillingStatus(token: string) {
  const response = await fetch('https://api.example.com/billing/status', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch billing status');
  }
  
  const data = await response.json();
  
  // Verificar si puede analizar
  if (!data.can_analyze) {
    console.log(`Límite alcanzado: ${data.usage_current}/${data.usage_limit}`);
    if (data.reset_date) {
      console.log(`Se reinicia el: ${new Date(data.reset_date).toLocaleDateString()}`);
    }
  }
  
  return data;
}
```

### Python

```python
import requests

def check_billing_status(token: str) -> dict:
    """
    Obtiene el estado de facturación del usuario
    """
    response = requests.get(
        'https://api.example.com/billing/status',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    response.raise_for_status()
    data = response.json()
    
    # Verificar si puede analizar
    if not data['can_analyze']:
        print(f"Límite alcanzado: {data['usage_current']}/{data['usage_limit']}")
        if data['reset_date']:
            print(f"Se reinicia el: {data['reset_date']}")
    
    return data
```

### cURL

```bash
curl -X GET "https://api.example.com/billing/status" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Respuestas de Error

### 401 Unauthorized

Usuario no autenticado o token inválido:

```json
{
  "detail": "Not authenticated"
}
```

### 500 Internal Server Error

Error del servidor:

```json
{
  "detail": "Internal server error"
}
```

## Casos de Uso

### 1. Mostrar Estado de Uso en la UI

```typescript
// En la extensión o web
async function displayUsageStatus() {
  const status = await checkBillingStatus(userToken);
  
  // Mostrar progreso
  const percentage = (status.usage_current / status.usage_limit) * 100;
  console.log(`Uso: ${percentage.toFixed(1)}%`);
  
  // Mostrar alerta si está cerca del límite
  if (percentage > 80) {
    showWarning(`Te quedan ${status.usage_limit - status.usage_current} análisis`);
  }
}
```

### 2. Validar Antes de Ejecutar Análisis

```typescript
async function performAnalysis(profileUrl: string) {
  const status = await checkBillingStatus(userToken);
  
  if (!status.can_analyze) {
    // Mostrar modal de upgrade
    showUpgradeModal({
      plan: status.plan,
      resetDate: status.reset_date
    });
    return;
  }
  
  // Proceder con el análisis
  return await analyzeProfile(profileUrl);
}
```

### 3. Mostrar Banner de Upgrade

```typescript
function shouldShowUpgradeBanner(status: BillingStatus): boolean {
  const usagePercentage = (status.usage_current / status.usage_limit) * 100;
  
  // Mostrar banner si:
  // - Plan free y ha usado >66% (2/3 análisis)
  // - Plan starter y ha usado >75%
  // - Plan pro y ha usado >80%
  return (
    (status.plan === 'free' && usagePercentage > 66) ||
    (status.plan === 'starter' && usagePercentage > 75) ||
    (status.plan === 'pro' && usagePercentage > 80)
  );
}
```

## Notas Importantes

1. **Caché**: Este endpoint puede ser llamado frecuentemente. Considera implementar caché en el cliente (5-10 minutos).

2. **Plan Free**: Para usuarios free, `reset_date` siempre será `null` porque su límite es lifetime (no se resetea).

3. **Actualización en Tiempo Real**: Después de cada análisis exitoso, considera refrescar el estado de facturación.

4. **Estado `can_analyze`**: Este campo es la fuente de verdad para determinar si se debe permitir un análisis. Siempre verifica este campo antes de iniciar un análisis.

5. **Sincronización con Stripe**: El campo `subscription_status` refleja el estado real de la suscripción en Stripe y se actualiza vía webhooks.

## Implementación Interna

El endpoint está implementado en:
- **Archivo**: `app/api/routes/billing.py`
- **Función**: `get_billing_status()`
- **Modelo**: `BillingStatusResponse`

## Tests

Para verificar que el endpoint funciona correctamente, ejecuta:

```bash
python test_billing_status.py
```

Este test valida:
- ✅ Respuesta para todos los planes (free, starter, pro, team)
- ✅ Cálculo correcto de límites y uso
- ✅ Campo `can_analyze` según el uso
- ✅ Campo `reset_date` solo para planes pagos
- ✅ Autenticación requerida
