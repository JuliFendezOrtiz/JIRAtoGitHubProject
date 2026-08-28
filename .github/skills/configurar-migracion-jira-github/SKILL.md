---
name: configurar-migracion-jira-github
description: Guía a un usuario NO técnico, paso a paso, para reunir las credenciales, completar el fichero config.yml, preparar el entorno de Python y ejecutar el script que migra los issues de Jira a GitHub Projects. Es capaz de INFERIR automáticamente la configuración a partir de un simple mensaje con la URL de Jira (p. ej. "Quiero migrar este proyecto de JIRA https://empresa.atlassian.net/jira/software/projects/ABC a un project en GitHub"). Úsala cuando el usuario quiera configurar, preparar, validar o lanzar la migración de Jira a GitHub, o cuando diga cosas como "quiero migrar mi Jira", "no sé cómo configurar el script" o "ayúdame a rellenar el config".
allowed-tools: Read, Edit, Write, Bash
---

# Configurar y lanzar la migración de Jira a GitHub Projects

Esta skill acompaña a una persona **sin conocimientos técnicos** durante todo el proceso:
inferir el máximo de datos, reunir lo que falte, obtener credenciales, rellenar la
configuración, comprobar que todo es correcto y, finalmente, ejecutar el script.

## Principios de trato con el usuario

- Habla en **castellano, con lenguaje claro y sin jerga**. Si usas un término técnico
  (token, PAT, JQL, entorno virtual…), explícalo en una frase.
- **Infiere primero, pregunta después.** Deduce todo lo que puedas del mensaje del usuario
  (ver "Inferencia inteligente") y **solo pregunta lo que no puedas deducir**.
- Cuando infieras algo, **muéstralo y pide confirmación** ("He detectado que tu Jira es
  `empresa.atlassian.net` y el proyecto es `ABC`, ¿es correcto?"). Nunca des un dato
  inventado por seguro.
- **Pregunta de una en una** lo que falte. No abrumes con formularios largos.
- **Nunca** pidas ni muestres tokens o contraseñas en el chat. Los tokens se definen como
  variables de entorno; el usuario los pega directamente en la terminal.
- Antes de cada paso, di **qué vas a hacer y por qué**. Después, confirma el resultado.
- Si algo falla, tranquiliza al usuario, explica la causa en lenguaje sencillo y propón la
  solución. Consulta `references/faq-y-problemas.md`.
- Trabaja siempre dentro de la carpeta `03-Script-Migracion/`.

## Recursos disponibles

**references/** — documentación que consultas cuando la necesitas:
- `references/obtener-credenciales.md` — cómo sacar el token de Jira, el PAT de GitHub y el
  número del Project, con indicaciones de dónde hacer clic.
- `references/faq-y-problemas.md` — preguntas frecuentes y solución de errores comunes.
- `references/glosario.md` — qué es un token, un PAT, JQL, un Project v2, un campo, etc.

**templates/** — ficheros base para el output:
- `templates/config.template.yml` — plantilla de `config.yml` con marcadores `<...>` que
  rellenas con lo inferido y confirmado.

**scripts/** — código que puedes ejecutar (la skill es autocontenida, todo vive aquí):
- `scripts/migrate_jira_to_github.py` — el script de migración que ejecuta la skill.
- `scripts/requirements.txt` — dependencias de Python del script.
- `scripts/config.example.yml` — plantilla de configuración que se copia a `config.yml`.
- `scripts/validar-configuracion.ps1` — comprueba Python, `config.yml` y las variables de
  entorno antes de lanzar la migración.

**examples/** — ejemplo del resultado esperado:
- `examples/ejemplo-migracion.md` — sesión completa de principio a fin.

Documentación del proyecto (fuera de la skill):
- `../../../03-Script-Migracion/README.md` — documentación técnica completa del script.
- `../../../01-Documentacion/guia-github-projects.md` — estructura recomendada del Project.

> **Carpeta de trabajo:** todos los comandos del flujo se ejecutan desde la carpeta
> `scripts/` de esta skill, que ya contiene el script, sus dependencias y la plantilla.

---

## Inferencia inteligente (hazlo SIEMPRE al empezar)

En cuanto el usuario escriba algo como *"Quiero migrar este proyecto de JIRA
`<URL>` a un project en GitHub"*, **extrae automáticamente** todo lo posible de la URL y del
texto antes de preguntar nada. Rellena un borrador mental de `config.yml` con lo deducido.

### Qué deducir de una URL de Jira
Las URLs de Jira Cloud tienen formas como estas:

| Ejemplo de URL | `jira.base_url` | Clave de proyecto |
|----------------|-----------------|-------------------|
| `https://empresa.atlassian.net/jira/software/projects/ABC/boards/12` | `https://empresa.atlassian.net` | `ABC` |
| `https://empresa.atlassian.net/browse/ABC-123` | `https://empresa.atlassian.net` | `ABC` |
| `https://empresa.atlassian.net/jira/core/projects/ABC/board` | `https://empresa.atlassian.net` | `ABC` |
| `https://empresa.atlassian.net/secure/RapidBoard.jspa?projectKey=ABC` | `https://empresa.atlassian.net` | `ABC` |

Reglas de extracción:
- **`base_url`**: el esquema + el host hasta `.atlassian.net` (o el dominio propio de Jira).
- **Clave de proyecto**: el segmento tras `/projects/`, el prefijo antes del `-` en
  `/browse/ABC-123`, o el valor de `projectKey=`.
- Con la clave, construye el **JQL** por defecto:
  `project = <CLAVE> AND statusCategory != Done ORDER BY created ASC`.
- Si el mensaje también trae una URL de GitHub (`https://github.com/<owner>/<repo>` o
  `.../orgs/<owner>/projects/<n>`), deduce `github.owner`, `github.repo` y
  `github.project_number` igual.

### Qué NO se puede inferir (siempre hay que pedirlo)
- El **email de Jira** del usuario.
- Los **tokens** de Jira y GitHub (por seguridad, nunca por el chat).
- El **repo** y el **número de Project** de GitHub si no vienen en el mensaje.
- Los **mapeos** de usuarios/estados/prioridades si difieren de los valores por defecto.

### Cómo presentarlo
Resume lo inferido en una tabla y marca lo que falta, por ejemplo:

> He deducido esto de tu mensaje:
> - Jira: `https://empresa.atlassian.net` · proyecto `ABC`
> - JQL propuesto: `project = ABC AND statusCategory != Done ORDER BY created ASC`
>
> Me faltan estos datos, te los pido uno a uno: tu email de Jira, el repositorio de GitHub
> de destino y el número del Project.

Luego continúa con el flujo de trabajo, saltándote lo que ya esté resuelto.

---

## Flujo de trabajo (síguelo en orden)

### Paso 0 — Inferencia + bienvenida y comprobación previa
1. Aplica la **Inferencia inteligente** al mensaje del usuario y muestra lo deducido.
2. Saluda y explica en 2-3 frases qué vais a hacer: "vamos a copiar los issues de tu Jira a
   un proyecto de GitHub, sin tocar nada en Jira".
3. Comprueba los **requisitos previos**:
   - ¿Tiene **Python 3.10 o superior**? Verifícalo con `python --version`. Si no, indícale
     que lo instale desde https://www.python.org/downloads/ y para.
   - ¿Existe ya el **repositorio de GitHub** de destino? Si no, guíale para crearlo.
   - ¿Existe ya el **GitHub Project (v2)** con los campos `Status`, `Priority` y `Estimate`?
     Si no, remítele a `../../../01-Documentacion/guia-github-projects.md`.
4. No avances hasta que los tres requisitos estén cubiertos.

### Paso 1 — Completar la información que falte
Pregunta **de una en una** solo lo que la inferencia no haya resuelto:

| Dato | Pregunta sencilla (solo si falta) |
|------|-----------------------------------|
| URL / proyecto de Jira | Ya inferido de la URL; **confírmalo**. |
| Email de Jira | "¿Con qué email entras a Jira?" |
| Owner de GitHub | "¿A qué organización o usuario de GitHub pertenece el repositorio?" |
| Repositorio | "¿Cómo se llama el repositorio de destino?" |
| Número del Project | "Abre tu Project en GitHub y dime el número que sale en la URL." |

Si el usuario no sabe alguno, guíale con `references/obtener-credenciales.md`.

### Paso 2 — Obtener las credenciales (tokens)
El script necesita dos tokens. **No los pidas por el chat**; el usuario los pegará en la
terminal más adelante.
1. **Token de Jira:** guíale para crearlo en
   https://id.atlassian.com/manage-profile/security/api-tokens
   (pasos detallados en `references/obtener-credenciales.md`).
2. **Token de GitHub (PAT):** con permisos `repo` y `project` (Classic) o lectura/escritura
   de *Issues* y *Projects* (Fine-grained).
3. Pídele que copie ambos tokens a un lugar seguro y temporal (no en el chat).

### Paso 3 — Preparar el entorno de Python
Explica que esto crea un "espacio aislado" para las dependencias del script. Sitúate en la
carpeta `scripts/` de la skill y ejecuta:

```powershell
cd .github\skills\configurar-migracion-jira-github\scripts
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Confirma que la instalación terminó sin errores antes de seguir.

### Paso 4 — Crear y rellenar config.yml
1. Desde la carpeta `scripts/`, copia la plantilla (`config.example.yml` incluida en la
   skill; usa `templates/config.template.yml` como referencia de los marcadores a rellenar):
   ```powershell
   Copy-Item config.example.yml config.yml
   ```
2. **Rellena tú** `config.yml` con lo inferido y confirmado: `jira.base_url`, `jira.email`,
   `jira.jql`, `github.owner`, `github.repo`, `github.project_number`.
3. **Deja los tokens como `env:JIRA_API_TOKEN` y `env:GITHUB_TOKEN`** (no escribas los
   tokens en el fichero).
4. Repasa los **mapeos** (`mapping.status`, `mapping.priority`, `mapping.users`): pregunta si
   sus estados, prioridades y personas coinciden con los valores por defecto y ajústalos.
   Recuerda que los valores de `status` y `priority` deben existir con el mismo nombre en el
   Project de GitHub.
5. Verifica que `config.yml` está en `.gitignore` para no subir datos sensibles.

### Paso 5 — Definir los tokens como variables de entorno
Pide al usuario que **escriba él mismo** en la terminal (para que los tokens no pasen por el
chat):

```powershell
$env:JIRA_API_TOKEN = "pega_aqui_tu_token_de_jira"
$env:GITHUB_TOKEN   = "pega_aqui_tu_token_de_github"
```

Explícale que estas variables solo duran mientras la terminal esté abierta.

### Paso 6 — Prueba en seco (dry-run) — OBLIGATORIA
Desde la carpeta `scripts/`, ejecuta la comprobación previa (Python, `config.yml` y tokens):

```powershell
.\validar-configuracion.ps1
```

Si está todo en verde, ejecuta la simulación que **no crea nada**:

```powershell
python migrate_jira_to_github.py --config config.yml --dry-run
```

- Revisa con el usuario la salida: número de issues detectados y cómo se mapean.
- Si hay errores, corrígelos (Paso 4/5 o `references/faq-y-problemas.md`) y **repite el
  dry-run** hasta que salga limpio.

### Paso 7 — Prueba limitada (piloto)
Migra solo unos pocos issues para validar en GitHub:

```powershell
python migrate_jira_to_github.py --config config.yml --limit 10
```

Pide al usuario que abra GitHub y compruebe los 10 issues y el Project (estado, prioridad,
estimación, asignados). Si algo no cuadra, ajusta los mapeos y repite.

### Paso 8 — Migración completa
Cuando el piloto sea correcto y el usuario dé el visto bueno, lanza la migración final:

```powershell
python migrate_jira_to_github.py --config config.yml
```

### Paso 9 — Verificación y cierre
1. Confirma en GitHub que los issues se crearon y están en el Project.
2. Recuerda que cada issue enlaza a su `Jira Key` original.
3. **Seguridad final:** aconséjale **revocar los tokens** de Jira y GitHub, y no subir nunca
   `config.yml` a un repositorio.

---

## Bucle de validación (aplícalo en cada paso)
Ejecutar → revisar la salida con el usuario → si hay error, diagnosticar con
`references/faq-y-problemas.md` → corregir → repetir. No pases al siguiente paso hasta que el
actual funcione.
