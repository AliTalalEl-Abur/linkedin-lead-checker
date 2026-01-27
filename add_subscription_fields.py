"""
Script para agregar los campos de suscripción a la tabla users
Ejecutar: python add_subscription_fields.py
"""

import sqlite3
import os
from pathlib import Path

# Buscar el archivo de base de datos
db_paths = [
    "linkedin_lead_checker.db",
    "./linkedin_lead_checker.db",
    "../linkedin_lead_checker.db",
]

db_path = None
for path in db_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    print("❌ No se encontró la base de datos")
    print("   Buscado en:", db_paths)
    exit(1)

print(f"📂 Usando base de datos: {db_path}")

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n🔍 Verificando campos existentes...")

# Obtener información de la tabla
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
column_names = [col[1] for col in columns]

print(f"✓ Campos actuales: {', '.join(column_names)}")

# Campos que necesitamos agregar
new_fields = {
    'subscription_status': 'TEXT',
    'monthly_analyses_count': 'INTEGER DEFAULT 0 NOT NULL',
    'monthly_analyses_reset_at': 'TIMESTAMP',
}

# Verificar qué campos faltan
missing_fields = []
for field_name in new_fields.keys():
    if field_name not in column_names:
        missing_fields.append(field_name)

if not missing_fields:
    print("\n✅ Todos los campos ya existen!")
    conn.close()
    exit(0)

print(f"\n➕ Agregando campos faltantes: {', '.join(missing_fields)}")

# Agregar campos faltantes
try:
    for field_name in missing_fields:
        field_type = new_fields[field_name]
        sql = f"ALTER TABLE users ADD COLUMN {field_name} {field_type}"
        print(f"   Ejecutando: {sql}")
        cursor.execute(sql)
    
    # Crear índices si no existen
    print("\n📊 Creando índices...")
    
    # Verificar si los índices ya existen
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='users'")
    existing_indexes = [row[0] for row in cursor.fetchall()]
    
    indexes = [
        ("ix_users_stripe_customer_id", "stripe_customer_id"),
        ("ix_users_stripe_subscription_id", "stripe_subscription_id"),
    ]
    
    for index_name, column_name in indexes:
        if index_name not in existing_indexes:
            sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON users ({column_name})"
            print(f"   Creando índice: {index_name}")
            cursor.execute(sql)
        else:
            print(f"   ✓ Índice ya existe: {index_name}")
    
    # Commit cambios
    conn.commit()
    
    print("\n✅ Migración completada exitosamente!")
    print("\n📋 Nuevos campos agregados:")
    print("   • subscription_status (TEXT) - Estado de la suscripción Stripe")
    print("   • monthly_analyses_count (INTEGER) - Contador mensual de análisis")
    print("   • monthly_analyses_reset_at (TIMESTAMP) - Fecha de reset mensual")
    
    # Verificar campos finales
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print(f"\n📊 Total de campos ahora: {len(columns)}")
    
except Exception as e:
    print(f"\n❌ Error durante la migración: {e}")
    conn.rollback()
    exit(1)
finally:
    conn.close()

print("\n✨ Listo para recibir webhooks de Stripe!")
