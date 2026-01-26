#!/usr/bin/env python3
"""
Simple Event Analytics Script
Analiza los logs del servidor para extraer métricas de tracking
"""
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


def parse_log_file(log_file: str = "server.log"):
    """
    Parsea el archivo de log del servidor y extrae eventos de tracking
    
    Formato esperado:
    INFO - EVENT_TRACK | install_extension_click | page=landing | ip=127.0.0*** | ua=... | referrer=direct
    """
    events = []
    pattern = r"EVENT_TRACK \| (\w+) \| page=(\w+) \| ip=([\w\.:*]+) \| ua=(.+?) \| referrer=(.+?)$"
    
    log_path = Path(log_file)
    if not log_path.exists():
        print(f"⚠️  Log file not found: {log_file}")
        print("ℹ️  Events are currently only logged to stdout/console")
        return events
    
    with open(log_path, 'r') as f:
        for line in f:
            match = re.search(pattern, line)
            if match:
                event_type, page, ip, ua, referrer = match.groups()
                events.append({
                    'type': event_type,
                    'page': page,
                    'ip': ip,
                    'user_agent': ua.strip(),
                    'referrer': referrer.strip()
                })
    
    return events


def analyze_events(events: list):
    """Genera estadísticas de los eventos"""
    if not events:
        print("📊 No events found in logs\n")
        return
    
    print("=" * 70)
    print("📊 LINKEDIN LEAD CHECKER - EVENT ANALYTICS")
    print("=" * 70)
    print()
    
    # Conteo total
    print(f"📈 Total Events: {len(events)}")
    print()
    
    # Eventos por tipo
    event_types = Counter(e['type'] for e in events)
    print("🎯 Events by Type:")
    for event_type, count in event_types.most_common():
        percentage = (count / len(events)) * 100
        print(f"   • {event_type}: {count} ({percentage:.1f}%)")
    print()
    
    # Eventos por página
    pages = Counter(e['page'] for e in events)
    print("📄 Events by Page:")
    for page, count in pages.most_common():
        percentage = (count / len(events)) * 100
        print(f"   • {page}: {count} ({percentage:.1f}%)")
    print()
    
    # Referrers
    referrers = Counter(e['referrer'] for e in events)
    print("🔗 Top Referrers:")
    for referrer, count in referrers.most_common(10):
        percentage = (count / len(events)) * 100
        display_ref = referrer if referrer != 'direct' else '(direct)'
        print(f"   • {display_ref}: {count} ({percentage:.1f}%)")
    print()
    
    # IPs únicas (aproximado, ya que están enmascaradas)
    unique_ips = len(set(e['ip'] for e in events))
    print(f"🌐 Unique IPs (approx): {unique_ips}")
    print()
    
    # Métricas de conversión
    print("💡 Conversion Metrics:")
    install_clicks = sum(1 for e in events if e['type'] == 'install_extension_click')
    waitlist_joins = sum(1 for e in events if e['type'] == 'waitlist_join')
    
    if install_clicks > 0:
        conversion_rate = (waitlist_joins / install_clicks) * 100
        print(f"   • Install Clicks: {install_clicks}")
        print(f"   • Waitlist Joins: {waitlist_joins}")
        print(f"   • Conversion Rate: {conversion_rate:.1f}%")
    else:
        print("   • Not enough data yet")
    
    print()
    print("=" * 70)


def main():
    """Función principal"""
    print()
    print("🔍 Searching for event logs...")
    print()
    
    # Intentar diferentes ubicaciones de logs
    possible_logs = [
        "server.log",
        "app.log",
        "logs/server.log",
        "data/events.jsonl"  # Si implementas el guardado en JSON
    ]
    
    events = []
    for log_file in possible_logs:
        if Path(log_file).exists():
            print(f"✅ Found: {log_file}")
            events = parse_log_file(log_file)
            break
    else:
        print("⚠️  No log files found")
        print()
        print("💡 Current Implementation:")
        print("   Events are logged to stdout/console only")
        print()
        print("   To capture events permanently:")
        print("   1. Run backend with output redirect:")
        print("      python start_server.py > server.log 2>&1")
        print()
        print("   2. Or implement file logging in events.py")
        print("      (See TRACKING_IMPLEMENTATION.md for examples)")
        print()
        return
    
    print()
    analyze_events(events)


if __name__ == "__main__":
    main()
