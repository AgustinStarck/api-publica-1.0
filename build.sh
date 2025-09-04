#!/usr/bin/env bash
# build.sh
echo "🚀 Building Django project for Render..."

# Instalar dependencias
pip install -r requirements.txt

# Crear directorio staticfiles si no existe
mkdir -p staticfiles

# Colectar archivos estáticos
python manage.py collectstatic --noinput --clear

# Aplicar migraciones
python manage.py migrate --noinput

echo "✅ Build completed successfully!"