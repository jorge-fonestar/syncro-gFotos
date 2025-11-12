# Configuración de rclone para Google Photos

## Paso 1: Configurar el remote de Google Photos

Abre una nueva terminal PowerShell (importante: nueva terminal para que cargue la variable PATH) y ejecuta:

```powershell
rclone config
```

Sigue estos pasos en el menú interactivo:

1. **n** (New remote)
2. **Nombre**: `gfotos` (o el que prefieras)
3. **Storage**: `17` (Google Photos) - el número puede variar, busca "Google Photos"
4. **client_id**: Deja en blanco (presiona Enter)
5. **client_secret**: Deja en blanco (presiona Enter)
6. **scope**: `1` (readonly)
7. **root_folder_id**: Deja en blanco (presiona Enter)
8. **service_account_file**: Deja en blanco (presiona Enter)
9. **Edit advanced config**: `n` (No)
10. **Use auto config**: `y` (Yes) - Se abrirá el navegador
11. **Autoriza con tu cuenta de Google** en el navegador
12. **Confirm**: `y` (Yes)
13. **q** (Quit)

## Paso 2: Verificar la configuración

```powershell
rclone lsd gfotos:
```

Deberías ver las carpetas de tu Google Photos (album, media, feature-content, shared-album, etc.)

## Paso 3: Probar descarga

Prueba listando algunos archivos:

```powershell
rclone ls gfotos:media --max-depth 1
```

## Paso 4: Sincronizar a tu NAS

Ejecuta la sincronización:

```powershell
rclone sync gfotos:media "\\Nas-home\cloud_data\gFotos\ (Yorch)" --progress --verbose
```

## Opciones útiles:

- `--progress`: Muestra el progreso
- `--verbose` o `-v`: Muestra más detalles
- `--dry-run`: Simula la sincronización sin descargar nada
- `--transfers 4`: Número de transferencias paralelas (por defecto 4)
- `--checkers 8`: Número de verificadores de archivos

## Sincronización incremental automática

El comando `rclone sync` es incremental por defecto. Solo descarga archivos nuevos o modificados.

## Script automatizado

Puedes crear un script PowerShell para ejecutar la sincronización:

```powershell
# sync_gfotos.ps1
rclone sync gfotos:media "\\Nas-home\cloud_data\gFotos\ (Yorch)" `
    --progress `
    --log-file "sync_log.txt" `
    --log-level INFO
```

Ejecuta con:
```powershell
.\sync_gfotos.ps1
```
