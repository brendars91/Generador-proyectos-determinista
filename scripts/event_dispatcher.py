#!/usr/bin/env python3
"""
AGCCE Event Dispatcher v1.0
Webhook-First Event Dispatcher para integracion con n8n.

DIRECTIVAS:
1. Solo emitir webhooks en hitos criticos (no cada paso)
2. Idempotencia via plan_id
3. Credential Isolation: Webhooks URL externos, no env vars del sistema

EVENTOS CRITICOS:
- PLAN_VALIDATED: Plan generado y validado exitosamente
- EXECUTION_ERROR: Error durante ejecucion
- EVIDENCE_READY: Evidencia recopilada, lista para reporte

Uso:
  from event_dispatcher import EventDispatcher
  EventDispatcher.emit("PLAN_VALIDATED", {"plan_id": "PLAN-XXX", ...})
"""

import json
import os
import sys
import time
import hashlib
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Importar utilidades
try:
    from common import Colors, Symbols, log_pass, log_fail, log_warn, log_info
except ImportError:
    class Colors:
        GREEN = RED = YELLOW = BLUE = CYAN = RESET = BOLD = ''
    class Symbols:
        CHECK = '[OK]'
        CROSS = '[X]'
        WARN = '[!]'
        INFO = '[i]'
    def log_pass(msg): print(f"[OK] {msg}")
    def log_fail(msg): print(f"[X] {msg}")
    def log_warn(msg): print(f"[!] {msg}")
    def log_info(msg): print(f"[i] {msg}")

# Importar telemetria
try:
    from metrics_collector import Telemetry
except ImportError:
    Telemetry = None


# Configuracion
CONFIG_FILE = "config/n8n_webhooks.json"
EVENT_LOG_FILE = "logs/events.jsonl"
IDEMPOTENCY_FILE = "logs/idempotency_keys.json"

# Eventos criticos permitidos
CRITICAL_EVENTS = {
    "PLAN_VALIDATED": "Plan generado y validado exitosamente",
    "EXECUTION_ERROR": "Error durante la ejecucion del plan",
    "EVIDENCE_READY": "Evidencia lista para envio",
    "SECURITY_BREACH_ATTEMPT": "Intento de brecha de seguridad detectado",
    "HIGH_LATENCY_THRESHOLD": "Umbral de latencia excedido",
    "HITL_TIMEOUT": "Timeout esperando aprobacion humana"
}


def load_webhook_config() -> Dict[str, str]:
    """Carga configuracion de webhooks."""
    default_config = {
        "PLAN_VALIDATED": "",
        "EXECUTION_ERROR": "",
        "EVIDENCE_READY": "",
        "SECURITY_BREACH_ATTEMPT": "",
        "HIGH_LATENCY_THRESHOLD": "",
        "HITL_TIMEOUT": "",
        "_comment": "Reemplaza URLs vacias con tus webhooks de n8n"
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # Crear archivo de configuracion si no existe
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=2)
    
    return default_config


def load_idempotency_keys() -> Dict[str, str]:
    """Carga registro de idempotency keys."""
    if os.path.exists(IDEMPOTENCY_FILE):
        try:
            with open(IDEMPOTENCY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_idempotency_key(key: str, timestamp: str) -> None:
    """Guarda idempotency key."""
    keys = load_idempotency_keys()
    keys[key] = timestamp
    
    os.makedirs(os.path.dirname(IDEMPOTENCY_FILE), exist_ok=True)
    with open(IDEMPOTENCY_FILE, 'w', encoding='utf-8') as f:
        json.dump(keys, f, indent=2)


def generate_idempotency_key(event_type: str, plan_id: str) -> str:
    """Genera idempotency key basada en plan_id y evento."""
    data = f"{event_type}:{plan_id}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def log_event(event_type: str, payload: Dict, success: bool, error: str = None) -> None:
    """Registra evento en log."""
    os.makedirs("logs", exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "success": success,
        "error": error,
        "plan_id": payload.get("plan_id"),
        "idempotency_key": payload.get("idempotency_key")
    }
    
    with open(EVENT_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


class EventDispatcher:
    """
    Dispatcher de eventos para n8n.
    Implementa Webhook-First pattern con idempotencia.
    """
    
    _config: Dict[str, str] = None
    _initialized: bool = False
    
    @classmethod
    def _ensure_initialized(cls) -> None:
        """Inicializa configuracion si no esta cargada."""
        if not cls._initialized:
            cls._config = load_webhook_config()
            cls._initialized = True
    
    @classmethod
    def get_webhook_url(cls, event_type: str) -> Optional[str]:
        """Obtiene URL de webhook para un evento."""
        cls._ensure_initialized()
        url = cls._config.get(event_type, "")
        return url if url and not url.startswith("_") else None
    
    @classmethod
    def is_event_valid(cls, event_type: str) -> bool:
        """Verifica si el evento es valido."""
        return event_type in CRITICAL_EVENTS
    
    @classmethod
    def check_idempotency(cls, event_type: str, plan_id: str) -> tuple:
        """
        Verifica idempotencia.
        Returns: (is_duplicate, idempotency_key)
        """
        if not plan_id:
            return False, None
        
        key = generate_idempotency_key(event_type, plan_id)
        existing_keys = load_idempotency_keys()
        
        if key in existing_keys:
            return True, key
        
        return False, key
    
    @classmethod
    def emit(
        cls,
        event_type: str,
        payload: Dict[str, Any],
        force: bool = False,
        async_mode: bool = True
    ) -> bool:
        """
        Emite un evento via webhook.
        
        Args:
            event_type: Tipo de evento critico
            payload: Datos del evento (debe incluir plan_id)
            force: Ignorar idempotencia
            async_mode: Emitir en background
        
        Returns:
            bool: True si el evento fue emitido/encolado
        """
        cls._ensure_initialized()
        
        # Validar evento
        if not cls.is_event_valid(event_type):
            log_warn(f"Evento no reconocido: {event_type}")
            return False
        
        # Obtener webhook URL
        webhook_url = cls.get_webhook_url(event_type)
        if not webhook_url:
            log_info(f"Webhook no configurado para {event_type}")
            return False
        
        # Verificar idempotencia
        plan_id = payload.get("plan_id", "")
        is_duplicate, idempotency_key = cls.check_idempotency(event_type, plan_id)
        
        if is_duplicate and not force:
            log_info(f"Evento duplicado ignorado: {event_type} ({idempotency_key})")
            return False
        
        # Preparar payload
        full_payload = {
            "event_type": event_type,
            "event_description": CRITICAL_EVENTS.get(event_type, ""),
            "timestamp": datetime.now().isoformat(),
            "idempotency_key": idempotency_key,
            "payload": payload
        }
        
        if async_mode:
            thread = threading.Thread(
                target=cls._send_webhook,
                args=(webhook_url, full_payload, event_type, idempotency_key)
            )
            thread.daemon = True
            thread.start()
            return True
        else:
            return cls._send_webhook(webhook_url, full_payload, event_type, idempotency_key)
    
    @classmethod
    def _send_webhook(
        cls,
        url: str,
        payload: Dict,
        event_type: str,
        idempotency_key: str
    ) -> bool:
        """Envia webhook HTTP POST."""
        try:
            data = json.dumps(payload).encode('utf-8')
            
            request = Request(
                url,
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'X-AGCCE-Event': event_type,
                    'X-Idempotency-Key': idempotency_key or ''
                },
                method='POST'
            )
            
            with urlopen(request, timeout=10) as response:
                status = response.status
                
                if status >= 200 and status < 300:
                    # Exito - guardar idempotency key
                    if idempotency_key:
                        save_idempotency_key(idempotency_key, datetime.now().isoformat())
                    
                    log_pass(f"Webhook enviado: {event_type}")
                    log_event(event_type, payload.get("payload", {}), True)
                    
                    # Registrar en telemetria
                    if Telemetry:
                        Telemetry.record_async({
                            "contract": "AGCCE-OBS-V1",
                            "type": "automation.webhook_sent",
                            "timestamp": datetime.now().isoformat(),
                            "metrics": {
                                "event_type": event_type,
                                "success": True
                            }
                        })
                    
                    return True
                else:
                    raise Exception(f"HTTP {status}")
        
        except (URLError, HTTPError) as e:
            error_msg = str(e)
            log_fail(f"Error webhook {event_type}: {error_msg}")
            log_event(event_type, payload.get("payload", {}), False, error_msg)
            return False
        
        except Exception as e:
            error_msg = str(e)
            log_fail(f"Error webhook {event_type}: {error_msg}")
            log_event(event_type, payload.get("payload", {}), False, error_msg)
            return False
    
    @classmethod
    def emit_plan_validated(cls, plan_id: str, plan_data: Dict) -> bool:
        """Emite evento PLAN_VALIDATED."""
        return cls.emit("PLAN_VALIDATED", {
            "plan_id": plan_id,
            "objective": plan_data.get("objective", {}).get("description", ""),
            "steps_count": len(plan_data.get("steps", [])),
            "validation_status": "passed"
        })
    
    @classmethod
    def emit_execution_error(cls, plan_id: str, step_id: str, error: str) -> bool:
        """Emite evento EXECUTION_ERROR."""
        return cls.emit("EXECUTION_ERROR", {
            "plan_id": plan_id,
            "step_id": step_id,
            "error": error,
            "severity": "high"
        })
    
    @classmethod
    def emit_evidence_ready(
        cls,
        plan_id: str,
        evidence_path: str,
        summary: Dict
    ) -> bool:
        """Emite evento EVIDENCE_READY."""
        return cls.emit("EVIDENCE_READY", {
            "plan_id": plan_id,
            "evidence_path": evidence_path,
            "summary": summary
        })
    
    @classmethod
    def emit_security_alert(cls, plan_id: str, alert_type: str, details: Dict) -> bool:
        """Emite evento SECURITY_BREACH_ATTEMPT."""
        return cls.emit("SECURITY_BREACH_ATTEMPT", {
            "plan_id": plan_id,
            "alert_type": alert_type,
            "details": details,
            "severity": "critical"
        })


def configure_webhooks():
    """CLI para configurar webhooks."""
    print("=== Configurar Webhooks n8n ===\n")
    
    config = load_webhook_config()
    
    for event in CRITICAL_EVENTS:
        current = config.get(event, "")
        print(f"{event}:")
        print(f"  Descripcion: {CRITICAL_EVENTS[event]}")
        print(f"  URL actual: {current or '(no configurado)'}")
        
        new_url = input(f"  Nueva URL (Enter para mantener): ").strip()
        if new_url:
            config[event] = new_url
        print()
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuracion guardada en: {CONFIG_FILE}")


def main():
    if len(sys.argv) < 2:
        print("Uso: python event_dispatcher.py [configure | test | status]")
        print("\nComandos:")
        print("  configure  Configurar URLs de webhooks")
        print("  test       Enviar evento de prueba")
        print("  status     Ver estado de configuracion")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "configure":
        configure_webhooks()
    
    elif cmd == "test":
        event_type = sys.argv[2] if len(sys.argv) > 2 else "PLAN_VALIDATED"
        print(f"Enviando evento de prueba: {event_type}")
        
        success = EventDispatcher.emit(event_type, {
            "plan_id": "PLAN-TEST1234",
            "test": True,
            "message": "Evento de prueba AGCCE"
        }, force=True, async_mode=False)
        
        print(f"Resultado: {'OK' if success else 'FAILED'}")
    
    elif cmd == "status":
        config = load_webhook_config()
        print("=== Estado de Webhooks ===\n")
        
        for event, desc in CRITICAL_EVENTS.items():
            url = config.get(event, "")
            status = "Configurado" if url else "No configurado"
            icon = Symbols.CHECK if url else Symbols.CROSS
            print(f"{icon} {event}: {status}")
    
    else:
        print(f"Comando desconocido: {cmd}")


if __name__ == '__main__':
    main()
