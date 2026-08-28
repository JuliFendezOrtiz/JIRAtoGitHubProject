# Preguntas frecuentes y solución de problemas

Consulta esta base de conocimiento cuando el usuario tenga dudas o el script dé un error.

---

## Preguntas frecuentes

**¿Esto borra o cambia algo en mi Jira?**
No. El script **solo lee** de Jira. Nunca modifica ni borra nada allí.

**¿Puedo probar sin crear nada en GitHub?**
Sí. Usa `--dry-run`: simula la migración y te enseña lo que haría, sin crear issues.

**¿Y si me equivoco y quiero repetir?**
En una prueba con `--limit` habrás creado pocos issues; puedes borrarlos en GitHub y volver
a ejecutar. Por eso siempre hacemos primero un dry-run y luego un piloto pequeño.

**¿Se migran los comentarios?**
Sí, si en `config.yml` pones `options.migrate_comments: true`.

**¿Qué pasa si un estado o prioridad no coincide?**
Si el valor mapeado no existe en el Project de GitHub, ese campo se deja **vacío** para ese
issue (no falla la migración). Revisa `mapping.status` y `mapping.priority`.

**¿Tengo que dejar los tokens escritos en el fichero?**
No, y no debes. Se definen como variables de entorno (`env:JIRA_API_TOKEN`,
`env:GITHUB_TOKEN`) y se pegan en la terminal.

**Los cambios de token no funcionan al reabrir la terminal.**
Las variables de entorno solo duran mientras la terminal está abierta. Si abres una nueva,
vuelve a definirlas (Paso 5 de la skill).

---

## Errores comunes y cómo resolverlos

| Mensaje / síntoma | Causa probable | Solución |
|-------------------|----------------|----------|
| `Configuración inválida` | Falta un campo obligatorio en `config.yml`. | Revisa que `jira` (base_url, email, api_token, jql) y `github` (token, owner, repo) están rellenos. |
| `La variable de entorno 'X' no está definida` | No definiste el token en la terminal. | Ejecuta de nuevo el Paso 5: `$env:JIRA_API_TOKEN = "..."` y `$env:GITHUB_TOKEN = "..."`. |
| `401` / `403` en Jira | Email o token de Jira incorrectos. | Regenera el token de Jira y comprueba el email. |
| `401` / `403` en GitHub | El token de GitHub no tiene permisos. | Regenera el PAT con los scopes `repo` y `project`. |
| `No se encontró el Project #N` | `owner` o `project_number` incorrectos. | Verifica el número en la URL del Project y que el owner es correcto. |
| El campo `Status` queda vacío | El valor mapeado no existe en el Project. | Alinea `mapping.status` con las opciones reales del campo Status en GitHub. |
| `429 rate limit` | Demasiadas peticiones seguidas. | Sube `options.throttle_seconds` (p. ej. a `1.0`) y vuelve a ejecutar. |
| `python` no se reconoce | Python no está instalado o no está en el PATH. | Instálalo desde https://www.python.org/downloads/ y marca "Add to PATH". |
| No se puede activar el entorno (`.venv`) | Política de ejecución de PowerShell. | Ejecuta `Set-ExecutionPolicy -Scope Process RemoteSigned` y reintenta activar. |

---

## Cuándo parar y pedir ayuda a un perfil técnico

- Si tras regenerar los tokens siguen los errores `401`/`403`.
- Si la organización de GitHub tiene restricciones (SSO/SAML) que bloquean el token: hay que
  **autorizar el PAT para la organización** en la configuración del token.
- Si el proyecto de Jira usa campos personalizados poco habituales para Story Points
  (ajustar `mapping.story_points_field`).
