import os
import django
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')

# Database credentials from settings
DB_NAME = 'bookmyseat_s4ty'
DB_USER = 'bookmyseat_s4ty_user'
DB_PASSWORD = 'D2SoRhCWCpPsQK1XnWzCm4rYS4KxOULn'
DB_HOST = 'dpg-d4bipj7diees73ajvgcg-a.singapore-postgres.render.com'

# Connect and drop/recreate database
conn = psycopg2.connect(
    dbname='postgres',
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

try:
    cursor.execute(f'DROP DATABASE IF EXISTS {DB_NAME}')
    cursor.execute(f'CREATE DATABASE {DB_NAME}')
    print("✓ Database reset successful")
except Exception as e:
    print(f"✗ Error: {e}")
finally:
    cursor.close()
    conn.close()

# Now run Django setup and migrate
django.setup()
from django.core.management import call_command
call_command('migrate')
call_command('loaddata', 'data.json')
print("✓ Data loaded successfully")