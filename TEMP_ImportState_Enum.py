# Código a insertar: ImportState Enum
# Se debe insertar entre _ACTION_LABELS y class ImportPage

class ImportState(Enum):
    """Estados de la máquina de estados de importación (Documento 11, §3)."""

    SIN_ARCHIVO = "sin_archivo"
    ARCHIVO_SELECCIONADO = "archivo_seleccionado"
    VALIDANDO = "validando"
    VALIDO = "valido"
    CON_ERRORES = "con_errores"
    APLICANDO = "aplicando"
    COMPLETADO = "completado"
