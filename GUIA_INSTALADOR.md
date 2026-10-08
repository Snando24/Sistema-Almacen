# Guía de instalador

Este proyecto queda preparado para generar un instalador de Windows con `PyInstaller` + `Inno Setup`.

## Requisitos

- Windows 10 u 11
- Python 3.12
- Dependencias del proyecto instaladas
- Inno Setup 6

## Preparación

En la raíz del proyecto:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Instale también Inno Setup 6 si aún no está en el equipo.

## Generar el instalador

Ejecute:

```powershell
.\build_installer.ps1
```

El script:

- valida que `PyInstaller` esté disponible;
- genera `dist\SisAlmacen\SisAlmacen.exe`;
- compila `SisAlmacenInstaller.iss`;
- deja el instalador final en `installer\SisAlmacen-Installer.exe`.

## Datos del usuario

Cuando la aplicación corre instalada, la base de datos y los logs se guardan en la carpeta local del usuario:

```text
%LOCALAPPDATA%\SisAlmacen\
```

Dentro de esa carpeta se crean:

- `var\sisalmacen.sqlite3`
- `logs\sisalmacen.log`
- `var\respaldos\`

Esto evita errores de permisos al instalar en `Archivos de programa`.

## Instalar en otra PC

Copie el archivo `installer\SisAlmacen-Installer.exe` a la otra computadora y ejecútelo.

Después de instalar:

- abra la aplicación desde el acceso directo creado;
- en el primer arranque se inicializará la base local automáticamente;
- si se reinstala o actualiza, conserve `%LOCALAPPDATA%\SisAlmacen\` para mantener la información.
