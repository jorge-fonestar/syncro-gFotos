#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de sincronización incremental de Google Photos
Descarga fotos y videos nuevos desde Google Photos Library API
"""

import os
import sys
import json
import time
import pickle
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional
from dotenv import load_dotenv
from tqdm import tqdm

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configurar encoding UTF-8 para Windows y deshabilitar buffering
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONUNBUFFERED'] = '1'

# Scopes necesarios para Google Photos API
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

class GooglePhotosSync:
    """Clase principal para sincronización de Google Photos"""

    def __init__(self):
        """Inicializa el sincronizador cargando configuración"""
        load_dotenv()

        # Configuración desde .env
        self.credentials_file = os.getenv('CREDENTIALS_FILE', 'credentials.json')
        self.token_file = os.getenv('TOKEN_FILE', 'token.pickle')
        self.download_path = Path(os.getenv('DOWNLOAD_PATH', './downloads'))
        self.state_file = os.getenv('STATE_FILE', 'sync_state.json')
        self.page_size = int(os.getenv('PAGE_SIZE', '100'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.retry_delay = int(os.getenv('RETRY_DELAY', '5'))

        # Estado de sincronización
        self.synced_items: Set[str] = set()
        self.service = None

        # Validaciones
        self._validate_config()

    def _validate_config(self):
        """Valida la configuración antes de iniciar"""
        if not os.path.exists(self.credentials_file):
            print(f"[ERROR] No se encuentra el archivo '{self.credentials_file}'")
            print("[INFO] Por favor, sigue las instrucciones en README.md para obtener las credenciales")
            sys.exit(1)

        # Crear carpeta de descarga si no existe
        try:
            self.download_path.mkdir(parents=True, exist_ok=True)
            print(f"[OK] Carpeta de descarga: {self.download_path}")
        except Exception as e:
            print(f"[ERROR] No se puede crear la carpeta de descarga: {e}")
            sys.exit(1)

    def authenticate(self):
        """Autentica con Google Photos API usando OAuth"""
        creds = None

        # Cargar token guardado si existe
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
                print("[OK] Token de autenticacion cargado")
            except Exception as e:
                print(f"[WARN] Error cargando token: {e}")

        # Si no hay credenciales válidas, autenticar
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    print("[INFO] Refrescando token expirado...")
                    creds.refresh(Request())
                    print("[OK] Token refrescado exitosamente")
                except Exception as e:
                    print(f"[WARN] Error refrescando token: {e}")
                    creds = None

            if not creds:
                try:
                    print("[INFO] Iniciando proceso de autenticacion OAuth...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                    print("[OK] Autenticacion exitosa")
                except Exception as e:
                    print(f"[ERROR] ERROR en autenticacion: {e}")
                    sys.exit(1)

            # Guardar token para futuros usos
            try:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
                print(f"[OK] Token guardado en {self.token_file}")
            except Exception as e:
                print(f"[WARN] No se pudo guardar el token: {e}")

        # Construir servicio de API
        try:
            self.service = build('photoslibrary', 'v1', credentials=creds, static_discovery=False)
            print("[OK] Servicio de Google Photos API inicializado")
        except Exception as e:
            print(f"[ERROR] ERROR inicializando servicio: {e}")
            sys.exit(1)

    def load_state(self):
        """Carga el estado de sincronización previo"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.synced_items = set(data.get('synced_items', []))
                print(f"[INFO] Estado cargado: {len(self.synced_items)} items previamente sincronizados")
            except Exception as e:
                print(f"[WARN] Error cargando estado: {e}. Iniciando desde cero.")
                self.synced_items = set()
        else:
            print("[INFO] No hay estado previo. Primera sincronizacion.")
            self.synced_items = set()

    def save_state(self):
        """Guarda el estado actual de sincronización"""
        try:
            data = {
                'synced_items': list(self.synced_items),
                'last_sync': datetime.now().isoformat(),
                'total_items': len(self.synced_items)
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"[OK] Estado guardado: {len(self.synced_items)} items sincronizados")
        except Exception as e:
            print(f"[WARN] Error guardando estado: {e}")

    def get_all_media_items(self) -> List[Dict]:
        """Obtiene todos los items de medios de Google Photos"""
        print("[INFO] Obteniendo lista de medios desde Google Photos...")
        all_items = []
        next_page_token = None

        try:
            while True:
                try:
                    # Llamada a la API
                    results = self.service.mediaItems().list(
                        pageSize=self.page_size,
                        pageToken=next_page_token
                    ).execute()

                    items = results.get('mediaItems', [])
                    all_items.extend(items)

                    next_page_token = results.get('nextPageToken')

                    print(f"[INFO] Items obtenidos: {len(all_items)}", end='\r')

                    if not next_page_token:
                        break

                except HttpError as e:
                    print(f"\n[WARN] Error HTTP en la API: {e}")
                    if e.resp.status in [403, 429]:
                        print(f"[INFO] Esperando {self.retry_delay} segundos antes de reintentar...")
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        raise

        except Exception as e:
            print(f"\n[ERROR] ERROR obteniendo medios: {e}")
            return all_items

        print(f"\n[OK] Total de items encontrados: {len(all_items)}")
        return all_items

    def download_item(self, item: Dict) -> bool:
        """Descarga un item individual (foto o video)"""
        item_id = item['id']
        filename = item.get('filename', f"item_{item_id}")

        # Determinar URL de descarga
        base_url = item['baseUrl']
        mime_type = item.get('mimeType', '')

        # Para videos, agregar =dv; para fotos, =d
        if 'video' in mime_type:
            download_url = f"{base_url}=dv"
        else:
            download_url = f"{base_url}=d"

        # Ruta completa de destino
        dest_path = self.download_path / filename

        # Si ya existe el archivo, verificar si es necesario re-descargarlo
        if dest_path.exists():
            # Podríamos verificar el tamaño, pero por ahora asumimos que está completo
            return True

        # Descargar con reintentos
        for attempt in range(self.max_retries):
            try:
                response = requests.get(download_url, stream=True, timeout=30)
                response.raise_for_status()

                # Obtener tamaño total si está disponible
                total_size = int(response.headers.get('content-length', 0))

                # Guardar archivo
                with open(dest_path, 'wb') as f:
                    if total_size:
                        # Con barra de progreso para archivos grandes
                        with tqdm(total=total_size, unit='B', unit_scale=True,
                                 desc=filename[:30], leave=False) as pbar:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    pbar.update(len(chunk))
                    else:
                        # Sin barra de progreso
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                return True

            except requests.exceptions.RequestException as e:
                print(f"\n[WARN] Error descargando {filename} (intento {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    print(f"[ERROR] Fallo descarga de {filename} despues de {self.max_retries} intentos")
                    return False
            except Exception as e:
                print(f"\n[ERROR] Error inesperado descargando {filename}: {e}")
                return False

        return False

    def sync(self):
        """Ejecuta la sincronización incremental"""
        print("\n" + "="*60)
        print("[INFO] Iniciando sincronizacion de Google Photos")
        print("="*60 + "\n")

        # Autenticar
        self.authenticate()

        # Cargar estado previo
        self.load_state()

        # Obtener todos los items
        all_items = self.get_all_media_items()

        if not all_items:
            print("[INFO] No hay items para sincronizar")
            return

        # Filtrar solo items nuevos
        new_items = [item for item in all_items if item['id'] not in self.synced_items]

        if not new_items:
            print("[OK] Todo esta sincronizado. No hay items nuevos.")
            return

        print(f"\n[INFO] Items nuevos para descargar: {len(new_items)}")
        print(f"[INFO] Items ya sincronizados: {len(self.synced_items)}")
        print(f"[INFO] Descargando a: {self.download_path}\n")

        # Descargar items nuevos
        successful = 0
        failed = 0

        try:
            for idx, item in enumerate(new_items, 1):
                item_id = item['id']
                filename = item.get('filename', f"item_{item_id}")
                mime_type = item.get('mimeType', '')
                media_type = "[VIDEO]" if 'video' in mime_type else "[FOTO]"

                print(f"\n[{idx}/{len(new_items)}] {media_type}: {filename}")

                if self.download_item(item):
                    self.synced_items.add(item_id)
                    successful += 1
                    print(f"[OK] Descargado exitosamente")

                    # Guardar estado cada 10 items
                    if successful % 10 == 0:
                        self.save_state()
                else:
                    failed += 1
                    print(f"[ERROR] Fallo la descarga")

        except KeyboardInterrupt:
            print("\n\n[WARN] Sincronizacion interrumpida por el usuario")
            print("[INFO] Guardando estado actual...")
            self.save_state()
            print("[OK] Estado guardado. Puedes reanudar la sincronizacion ejecutando el script nuevamente.")
            sys.exit(0)

        # Guardar estado final
        self.save_state()

        # Resumen
        print("\n" + "="*60)
        print("[INFO] RESUMEN DE SINCRONIZACION")
        print("="*60)
        print(f"[OK] Descargados exitosamente: {successful}")
        print(f"[ERROR] Fallidos: {failed}")
        print(f"[INFO] Total sincronizados: {len(self.synced_items)}")
        print(f"[INFO] Ubicacion: {self.download_path}")
        print("="*60 + "\n")


def main():
    """Función principal"""
    try:
        syncer = GooglePhotosSync()
        syncer.sync()
    except KeyboardInterrupt:
        print("\n\n[INFO] Programa terminado por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
