# Script de migración Jira → GitHub Projects

Script en Python que extrae los issues de **Jira** y los recrea como **GitHub Issues**, añadiéndolos a un **GitHub Project (v2)** y rellenando sus campos personalizados (`Status`, `Priority`, `Estimate`).

## ¿Qué migra?

- ✅ Issues (título, descripción) con trazabilidad al `Jira Key` original.
- ✅ Tipo de issue → **label** (`type: story`, `type: bug`, …).
- ✅ Estado de Jira → campo **Status** del Project.
- ✅ Prioridad de Jira → campo **Priority** del Project.
- ✅ Story Points → campo **Estimate** del Project.
- ✅ Asignado → **assignee** (según el mapeo de usuarios).
- ✅ Comentarios (opcional).

> El script **no borra ni modifica** nada en Jira. Solo lee.

---

## 1. Requisitos previos

- **Python 3.10 o superior**.
- Un **repositorio** de GitHub de destino ya creado.
- Un **GitHub Project (v2)** creado con los campos `Status`, `Priority` y `Estimate` (los nombres deben coincidir con `config.yml`). Ver la estructura recomendada en `01-Documentacion/guia-github-projects.md`.
- **Token de Jira** (API token): https://id.atlassian.com/manage-profile/security/api-tokens
- **Token de GitHub** (Personal Access Token) con permisos:
  - Classic: `repo` y `project`.
  - Fine-grained: acceso de lectura/escritura a *Issues* y a *Projects* del owner.

---

## 2. Instalación

```powershell
# Desde la carpeta 03-Script-Migracion
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # en Windows PowerShell
pip install -r requirements.txt
```

---

## 3. Configuración

1. Copia la plantilla de configuración:

   ```powershell
   Copy-Item config.example.yml config.yml
   ```

2. Define tus tokens como variables de entorno (recomendado, evita escribirlos en el fichero):

   ```powershell
   $env:JIRA_API_TOKEN = "tu_token_de_jira"
   $env:GITHUB_TOKEN   = "tu_token_de_github"
   ```

3. Edita `config.yml` con tus datos. Estas son las secciones:

### `jira`
| Campo | Descripción |
|-------|-------------|
| `base_url` | URL de tu instancia, p. ej. `https://empresa.atlassian.net`. |
| `email` | Email de la cuenta de Jira. |
| `api_token` | Token de Jira. Usa `env:JIRA_API_TOKEN` para leerlo del entorno. |
| `jql` | Consulta JQL que selecciona los issues a migrar. |

### `github`
| Campo | Descripción |
|-------|-------------|
| `token` | PAT de GitHub. Usa `env:GITHUB_TOKEN`. |
| `owner` | Organización o usuario dueño del repo/project. |
| `repo` | Repositorio donde se crean los Issues. |
| `project_number` | Número del Project (visible en su URL). Omítelo para no usar Project. |

### `mapping`
| Campo | Descripción |
|-------|-------------|
| `story_points_field` | Campo custom de Jira con los Story Points (p. ej. `customfield_10016`). |
| `status_field` / `priority_field` / `estimate_field` | Nombres de los campos en el Project de GitHub. |
| `issue_type_to_label` | Tipo de issue de Jira → label de GitHub. |
| `extra_labels` | Labels añadidos a todos los issues migrados. |
| `status` | Estado de Jira → opción del campo `Status`. |
| `priority` | Prioridad de Jira → opción del campo `Priority`. |
| `users` | Usuario de Jira (email/nombre) → login de GitHub. |

### `options`
| Campo | Descripción |
|-------|-------------|
| `migrate_comments` | `true`/`false` para migrar comentarios. |
| `throttle_seconds` | Pausa entre issues para respetar los rate limits. |

> **Importante:** las opciones de `status` y `priority` deben existir con el mismo nombre en el Project de GitHub; si no, el campo se deja vacío para ese issue.

---

## 4. Uso

**Prueba en seco** (no crea nada, solo muestra lo que haría):

```powershell
python migrate_jira_to_github.py --config config.yml --dry-run
```

**Migrar solo unos pocos issues** (recomendado para validar):

```powershell
python migrate_jira_to_github.py --config config.yml --limit 10
```

**Migración completa:**

```powershell
python migrate_jira_to_github.py --config config.yml
```

### Opciones de línea de comandos
| Opción | Descripción |
|--------|-------------|
| `--config <ruta>` | Ruta al fichero YAML (obligatorio). |
| `--dry-run` | Simula la migración sin crear nada en GitHub. |
| `--limit <n>` | Migra como máximo `n` issues. |

---

## 5. Flujo recomendado

1. Crea el Project en GitHub con los campos del estándar de tu área.
2. Rellena `config.yml` y define los tokens como variables de entorno.
3. Ejecuta con `--dry-run` y revisa el mapeo en consola.
4. Ejecuta con `--limit 10` sobre un equipo piloto y valida el resultado en GitHub.
5. Lanza la migración completa.
6. Revisa los Issues creados: cada uno incluye un enlace a su `Jira Key` original.

---

## 6. Resolución de problemas

| Síntoma | Causa probable | Solución |
|---------|----------------|----------|
| `Configuración inválida` | Falta un campo obligatorio en el YAML. | Revisa `jira` y `github`. |
| `401`/`403` en Jira | Token o email incorrectos. | Regenera el API token de Jira. |
| `401`/`403` en GitHub | PAT sin permisos `repo`/`project`. | Regenera el token con los scopes correctos. |
| `No se encontró el Project #N` | `owner`/`project_number` incorrectos. | Verifica el número en la URL del Project. |
| El campo `Status` queda vacío | El valor mapeado no existe en el Project. | Alinea `mapping.status` con las opciones del Project. |
| `429 rate limit` | Demasiadas peticiones. | Sube `options.throttle_seconds`. |

---

## 7. Seguridad

- **No** subas `config.yml` con tokens a un repositorio. Usa siempre variables de entorno (`env:...`).
- Los tokens deben tener el **mínimo permiso necesario** y una caducidad razonable.
- Revoca los tokens una vez finalizada la migración.
