# Sincronización de Google Photos con rclone

Sincronización incremental de Google Photos a NAS usando rclone.

## Requisitos

- rclone instalado (ya instalado via winget)
- Cuenta de Google con Google Photos

## Configuración inicial (solo una vez)

La configuración de rclone ya está completa. El remote se llama `syncro-gPhotos`.

Para verificar la configuración:

```powershell
rclone config show syncro-gPhotos
```

## Uso

### Sincronización manual

Ejecuta el script PowerShell:

```powershell
.\sync.ps1
```

O ejecuta rclone directamente:

```powershell
rclone sync syncro-gPhotos:media "\\Nas-home\cloud_data\gFotos\ (Yorch)" --progress --verbose
```

### Opciones útiles de rclone

- `--dry-run` - Simula sin descargar nada (para probar)
- `--progress` - Muestra progreso en tiempo real
- `--verbose` o `-v` - Muestra más detalles
- `--transfers 4` - Número de descargas paralelas (default: 4)
- `--log-file sync.log` - Guarda log en archivo

### Ejemplo con dry-run

Para ver qué se va a descargar sin hacerlo realmente:

```powershell
rclone sync syncro-gPhotos:media "\\Nas-home\cloud_data\gFotos\ (Yorch)" --dry-run --verbose
```

## Automatización

### Tarea programada en Windows

Puedes crear una tarea programada que ejecute `sync.ps1` automáticamente:

1. Abre "Programador de tareas" (Task Scheduler)
2. Crear tarea básica
3. Nombre: "Sync Google Photos"
4. Desencadenador: Diariamente (o la frecuencia que prefieras)
5. Acción: Iniciar un programa
   - Programa: `powershell.exe`
   - Argumentos: `-ExecutionPolicy Bypass -File "C:\Users\Yorch\Proyectos\Z.Personales\syncro-gFotos\sync.ps1"`
   - Iniciar en: `C:\Users\Yorch\Proyectos\Z.Personales\syncro-gFotos`

## Archivos del proyecto

```
syncro-gFotos/
├── sync.ps1              # Script principal de sincronización
├── RCLONE_SETUP.md      # Guía detallada de configuración de rclone
├── README.md            # Este archivo
├── .gitignore           # Ignora archivos temporales
└── sync_log.txt         # Log de sincronizaciones (generado automáticamente)
```

## Notas importantes

### Limitación de Google Photos API

Debido a cambios en la política de Google Photos (2024), rclone solo puede descargar fotos que **tú hayas subido**, no las que Google creó automáticamente.

Para backup completo de TODAS tus fotos (incluyendo las automáticas):
- Usa [Google Takeout](https://takeout.google.com/)
- Exporta Google Photos
- Configura exportación automática cada 2 meses (opcional)

### Sincronización incremental

`rclone sync` es incremental por defecto:
- Solo descarga archivos nuevos o modificados
- No re-descarga archivos que ya existen
- Elimina archivos del destino que no existen en el origen (¡cuidado!)

Si prefieres que NO elimine archivos del destino, usa `rclone copy` en lugar de `rclone sync`.

## Solución de problemas

### Error: "didn't find section in config file"

La configuración de rclone no está completa. Ejecuta:

```powershell
rclone config
```

Y sigue las instrucciones de [RCLONE_SETUP.md](RCLONE_SETUP.md).

### Error: Token expirado

Ejecuta:

```powershell
rclone config reconnect syncro-gPhotos:
```

### Ver logs

Los logs se guardan automáticamente en `sync_log.txt` después de cada ejecución.

## Más información

- [Documentación oficial de rclone](https://rclone.org/docs/)
- [rclone con Google Photos](https://rclone.org/googlephotos/)
