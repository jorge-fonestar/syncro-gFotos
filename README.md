# Sincronización Incremental de Google Photos

Script Python para sincronizar fotos y videos desde Google Photos a una carpeta local o NAS de forma incremental.

## Características

- Sincronización incremental (solo descarga items nuevos)
- Soporte para fotos y videos
- Estado persistente (recuerda qué ya descargó)
- Manejo robusto de errores con reintentos automáticos
- Reanudación automática si se interrumpe
- Barras de progreso para descargas
- Compatible con rutas de red (NAS)

## Requisitos

- Python 3.7 o superior
- Windows 11 (o cualquier OS compatible con Python)
- Cuenta de Google con acceso a Google Photos
- Credenciales de API de Google Cloud

---

## Paso 1: Obtener credenciales de Google Cloud (credentials.json)

### 1.1 Crear un proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Inicia sesión con tu cuenta de Google
3. Haz clic en el selector de proyectos (arriba a la izquierda, al lado de "Google Cloud")
4. Haz clic en **"NEW PROJECT"** (Nuevo Proyecto)
5. Ingresa un nombre para tu proyecto (ej: "Google Photos Sync")
6. Haz clic en **"CREATE"** (Crear)
7. Espera unos segundos y selecciona el proyecto recién creado

### 1.2 Habilitar la API de Google Photos

1. En el menú lateral, ve a **"APIs & Services"** > **"Library"**
   - O usa este enlace directo: [API Library](https://console.cloud.google.com/apis/library)
2. En el buscador, escribe: **"Photos Library API"**
3. Haz clic en **"Photos Library API"**
4. Haz clic en el botón azul **"ENABLE"** (Habilitar)
5. Espera a que se habilite (puede tardar unos segundos)

### 1.3 Configurar la pantalla de consentimiento OAuth

1. En el menú lateral, ve a **"APIs & Services"** > **"OAuth consent screen"**
2. Selecciona **"External"** (Usuario externo)
3. Haz clic en **"CREATE"** (Crear)
4. Completa la información requerida:
   - **App name**: Nombre de tu aplicación (ej: "Google Photos Sync")
   - **User support email**: Tu email
   - **Developer contact information**: Tu email
5. Haz clic en **"SAVE AND CONTINUE"** (Guardar y continuar)
6. En la sección **"Scopes"** (Alcances):
   - Haz clic en **"ADD OR REMOVE SCOPES"**
   - Busca: **"Photos Library API"**
   - Selecciona: `https://www.googleapis.com/auth/photoslibrary.readonly`
   - Haz clic en **"UPDATE"** y luego **"SAVE AND CONTINUE"**
7. En la sección **"Test users"**:
   - Haz clic en **"ADD USERS"**
   - Agrega tu email de Google (el que usarás para acceder a Google Photos)
   - Haz clic en **"SAVE AND CONTINUE"**
8. Revisa el resumen y haz clic en **"BACK TO DASHBOARD"**

### 1.4 Crear credenciales OAuth 2.0

1. En el menú lateral, ve a **"APIs & Services"** > **"Credentials"**
2. Haz clic en **"CREATE CREDENTIALS"** > **"OAuth client ID"**
3. En "Application type", selecciona: **"Desktop app"**
4. Ingresa un nombre (ej: "Google Photos Sync Desktop")
5. Haz clic en **"CREATE"**
6. Aparecerá un diálogo con tu Client ID y Client Secret
7. Haz clic en **"DOWNLOAD JSON"** (Descargar JSON)
8. **IMPORTANTE**: Renombra el archivo descargado a **`credentials.json`**
9. Mueve `credentials.json` a la carpeta de este proyecto

---

## Paso 2: Instalación y configuración

### 2.1 Instalar dependencias

Abre PowerShell o CMD en la carpeta del proyecto y ejecuta:

```bash
pip install -r requirements.txt
```

### 2.2 Configurar variables de entorno

1. Copia el archivo de ejemplo:
   ```bash
   copy .env.example .env
   ```

2. Edita el archivo `.env` con tu editor favorito (Notepad, VSCode, etc.)

3. Configura las rutas según tus necesidades:

```env
# Archivo de credenciales (debe estar en la misma carpeta)
CREDENTIALS_FILE=credentials.json

# Ruta de destino para las fotos y videos
# Ejemplos para Windows:
#   - Ruta local: C:\Users\Yorch\Pictures\GooglePhotosBackup
#   - Ruta de red (NAS) por IP: \\192.168.1.100\fotos\backup
#   - Ruta de red (NAS) por nombre: \\MI-NAS\fotos\backup
#   - Unidad mapeada: Z:\fotos\backup
DOWNLOAD_PATH=C:\Users\Yorch\Pictures\GooglePhotosBackup

# Archivo de estado (guarda qué items ya se descargaron)
STATE_FILE=sync_state.json

# Archivo de token OAuth (se genera automáticamente)
TOKEN_FILE=token.pickle

# Configuración de la API
PAGE_SIZE=100
MAX_RETRIES=3
RETRY_DELAY=5
```

### 2.3 Configuración de NAS (opcional)

Si quieres sincronizar directamente a un NAS:

**Opción A: Usar ruta UNC (Universal Naming Convention)**
```env
DOWNLOAD_PATH=\\192.168.1.100\fotos\GooglePhotosBackup
```

**Opción B: Mapear una unidad de red primero**
1. Abre el Explorador de archivos
2. Clic derecho en "Este equipo" > "Conectar a unidad de red"
3. Selecciona una letra (ej: Z:)
4. Ingresa la ruta del NAS: `\\192.168.1.100\fotos`
5. Marca "Reconectar al iniciar sesión"
6. Usa la unidad mapeada en el .env:
```env
DOWNLOAD_PATH=Z:\GooglePhotosBackup
```

---

## Paso 3: Primer uso

### 3.1 Ejecutar el script

```bash
python sync_google_photos.py
```

### 3.2 Autenticación OAuth (primera vez)

1. El script abrirá automáticamente tu navegador
2. Inicia sesión con tu cuenta de Google
3. Verás una advertencia: "Google hasn't verified this app"
   - Haz clic en **"Advanced"** (Avanzado)
   - Haz clic en **"Go to [nombre de tu app] (unsafe)"**
   - Esto es normal porque es tu propia aplicación
4. Autoriza el acceso a Google Photos (solo lectura)
5. El navegador mostrará: "The authentication flow has completed"
6. Cierra el navegador y vuelve a la terminal

El script guardará el token de autenticación en `token.pickle` para futuros usos.

---

## Uso

### Sincronización normal

```bash
python sync_google_photos.py
```

### Características del script

- **Primera ejecución**: Descargará TODAS tus fotos y videos
- **Ejecuciones posteriores**: Solo descargará items nuevos
- **Interrupción**: Presiona `Ctrl+C` para detener. El progreso se guarda automáticamente
- **Reanudación**: Solo ejecuta el script nuevamente. Continuará desde donde se quedó
- **Estado persistente**: Se guarda en `sync_state.json`

### Progreso y mensajes

El script muestra información detallada:

- Número de items nuevos vs ya sincronizados
- Progreso de descarga con barras de progreso
- Tipo de medio (foto/video) y nombre de archivo
- Resumen final con estadísticas

---

## Estructura de archivos

```
syncro-gFotos/
├── credentials.json        # Credenciales de Google Cloud (NO COMPARTIR)
├── token.pickle           # Token de autenticación (generado automáticamente)
├── sync_state.json        # Estado de sincronización (generado automáticamente)
├── .env                   # Configuración (NO COMPARTIR, contiene rutas)
├── .env.example           # Ejemplo de configuración
├── requirements.txt       # Dependencias de Python
├── sync_google_photos.py  # Script principal
└── README.md             # Este archivo
```

---

## Seguridad

### Archivos sensibles (NO COMPARTIR ni subir a Git)

- `credentials.json` - Contiene tus credenciales de OAuth
- `token.pickle` - Contiene tu token de acceso
- `.env` - Puede contener rutas privadas

### Recomendación: Crear .gitignore

Si usas Git, crea un archivo `.gitignore`:

```gitignore
credentials.json
token.pickle
.env
sync_state.json
__pycache__/
*.pyc
```

---

## Solución de problemas

### Error: "No se encuentra credentials.json"

- Asegúrate de haber descargado y renombrado el archivo de credenciales
- Verifica que esté en la misma carpeta que el script
- Verifica el valor de `CREDENTIALS_FILE` en `.env`

### Error: "No se puede crear la carpeta de descarga"

- Verifica que la ruta en `DOWNLOAD_PATH` sea válida
- Si es una ruta de red, verifica que el NAS esté encendido y accesible
- Verifica permisos de escritura en la carpeta

### Error: "403 Forbidden" o "429 Too Many Requests"

- El script reintentará automáticamente con esperas
- Google Photos API tiene límites de uso
- Espera unos minutos y vuelve a ejecutar

### El navegador no se abre en la autenticación

- Copia manualmente la URL que aparece en la terminal
- Pégala en tu navegador
- Completa la autenticación
- Copia el código de autorización de vuelta a la terminal

### Archivos duplicados o corruptos

- Elimina `sync_state.json` para empezar desde cero
- El script no re-descargará archivos existentes en la carpeta de destino

---

## Programación automática (opcional)

### Windows Task Scheduler

Para ejecutar el script automáticamente cada día:

1. Abre "Programador de tareas" (Task Scheduler)
2. Clic en "Crear tarea básica"
3. Nombre: "Google Photos Sync"
4. Desencadenador: "Diariamente" a la hora deseada
5. Acción: "Iniciar un programa"
   - Programa: `python`
   - Argumentos: `"C:\Users\Yorch\Proyectos\Z.Personales\syncro-gFotos\sync_google_photos.py"`
   - Iniciar en: `C:\Users\Yorch\Proyectos\Z.Personales\syncro-gFotos`

---

## Contribuciones y soporte

Este es un proyecto personal. Si encuentras bugs o tienes sugerencias, siéntete libre de modificar el código según tus necesidades.

## Licencia

Este proyecto es de código abierto. Úsalo libremente.
