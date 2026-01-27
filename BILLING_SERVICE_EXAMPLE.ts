/**
 * Servicio para manejar el estado de facturación
 * 
 * Este módulo proporciona funciones para verificar el estado de facturación
 * del usuario y determinar si puede ejecutar análisis AI.
 */

interface BillingStatus {
  plan: 'free' | 'starter' | 'pro' | 'team';
  usage_current: number;
  usage_limit: number;
  reset_date: string | null;
  can_analyze: boolean;
  subscription_status: string | null;
}

/**
 * Obtiene el estado de facturación del usuario
 */
export async function getBillingStatus(token: string): Promise<BillingStatus> {
  const API_URL = 'https://your-api.com'; // Reemplazar con tu URL
  
  const response = await fetch(`${API_URL}/billing/status`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error(`Failed to fetch billing status: ${response.status}`);
  }
  
  return await response.json();
}

/**
 * Verifica si el usuario puede ejecutar un análisis
 */
export async function canPerformAnalysis(token: string): Promise<boolean> {
  const status = await getBillingStatus(token);
  return status.can_analyze;
}

/**
 * Obtiene el porcentaje de uso actual
 */
export function getUsagePercentage(status: BillingStatus): number {
  if (status.usage_limit === 0) return 0;
  return (status.usage_current / status.usage_limit) * 100;
}

/**
 * Determina el color del indicador de uso
 */
export function getUsageColor(status: BillingStatus): 'green' | 'yellow' | 'red' {
  const percentage = getUsagePercentage(status);
  
  if (percentage < 70) return 'green';
  if (percentage < 90) return 'yellow';
  return 'red';
}

/**
 * Formatea la fecha de reset para mostrar al usuario
 */
export function formatResetDate(resetDate: string | null): string {
  if (!resetDate) return 'Nunca';
  
  const date = new Date(resetDate);
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

/**
 * Obtiene un mensaje descriptivo del estado actual
 */
export function getBillingMessage(status: BillingStatus): string {
  const remaining = status.usage_limit - status.usage_current;
  
  if (!status.can_analyze) {
    if (status.plan === 'free') {
      return 'Has alcanzado tu límite de 3 análisis. Actualiza a un plan pago para continuar.';
    }
    return `Has alcanzado tu límite mensual de ${status.usage_limit} análisis. Se reiniciará el ${formatResetDate(status.reset_date)}.`;
  }
  
  if (remaining <= 5) {
    return `⚠️ Te quedan ${remaining} análisis este mes`;
  }
  
  return `Tienes ${remaining} análisis disponibles de ${status.usage_limit}`;
}

/**
 * Ejemplo de uso en la extensión
 */
export async function checkAndAnalyze(
  token: string,
  profileUrl: string,
  analyzeFunction: (url: string) => Promise<any>
) {
  try {
    // 1. Verificar el estado de facturación
    const status = await getBillingStatus(token);
    
    // 2. Verificar si puede analizar
    if (!status.can_analyze) {
      // Mostrar modal de upgrade
      showUpgradeModal(status);
      return null;
    }
    
    // 3. Mostrar advertencia si está cerca del límite
    const remaining = status.usage_limit - status.usage_current;
    if (remaining <= 5) {
      const proceed = confirm(
        `Te quedan ${remaining} análisis. ¿Deseas continuar?`
      );
      if (!proceed) return null;
    }
    
    // 4. Ejecutar el análisis
    const result = await analyzeFunction(profileUrl);
    
    // 5. Actualizar el estado en la UI
    await updateBillingUI(token);
    
    return result;
  } catch (error) {
    console.error('Error checking billing status:', error);
    throw error;
  }
}

/**
 * Actualiza el indicador de uso en la UI
 */
async function updateBillingUI(token: string) {
  const status = await getBillingStatus(token);
  
  // Actualizar badge con el uso restante
  const remaining = status.usage_limit - status.usage_current;
  chrome.action.setBadgeText({ text: remaining.toString() });
  
  // Actualizar color según el porcentaje
  const color = getUsageColor(status);
  const colorMap = {
    green: '#4CAF50',
    yellow: '#FFC107',
    red: '#F44336'
  };
  chrome.action.setBadgeBackgroundColor({ color: colorMap[color] });
}

/**
 * Muestra el modal de upgrade
 */
function showUpgradeModal(status: BillingStatus) {
  const message = status.plan === 'free'
    ? 'Has usado tus 3 análisis gratuitos. Actualiza para continuar.'
    : `Has alcanzado tu límite mensual de ${status.usage_limit} análisis.`;
  
  const upgradeUrl = 'https://your-website.com/pricing';
  
  if (confirm(`${message}\n\n¿Deseas ver los planes disponibles?`)) {
    chrome.tabs.create({ url: upgradeUrl });
  }
}

/**
 * Cachea el estado de facturación por 5 minutos
 */
class BillingStatusCache {
  private cache: { status: BillingStatus; timestamp: number } | null = null;
  private readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutos
  
  async get(token: string): Promise<BillingStatus> {
    const now = Date.now();
    
    // Retornar cache si es válido
    if (this.cache && (now - this.cache.timestamp) < this.CACHE_DURATION) {
      return this.cache.status;
    }
    
    // Obtener nuevo estado
    const status = await getBillingStatus(token);
    this.cache = { status, timestamp: now };
    
    return status;
  }
  
  invalidate() {
    this.cache = null;
  }
}

export const billingCache = new BillingStatusCache();

/**
 * Ejemplo de integración en background.js
 */
export async function setupBillingMonitoring(token: string) {
  // Actualizar cada 5 minutos
  setInterval(async () => {
    try {
      await updateBillingUI(token);
    } catch (error) {
      console.error('Error updating billing UI:', error);
    }
  }, 5 * 60 * 1000);
  
  // Actualizar inmediatamente
  await updateBillingUI(token);
}
