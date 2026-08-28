# Ejemplo de una sesión de migración

Muestra cómo se ve el proceso de principio a fin. Sirve de referencia del formato y del
resultado esperado.

---

## 1. Mensaje inicial del usuario

> Quiero migrar este proyecto de JIRA
> `https://acme.atlassian.net/jira/software/projects/PAY/boards/7`
> a un project en GitHub.

## 2. Inferencia de la skill

De ese único mensaje, la skill deduce y muestra:

| Dato | Valor inferido | Origen |
|------|----------------|--------|
| `jira.base_url` | `https://acme.atlassian.net` | host de la URL |
| Clave de proyecto | `PAY` | segmento tras `/projects/` |
| `jira.jql` | `project = PAY AND statusCategory != Done ORDER BY created ASC` | construido con la clave |

Y pide lo que falta, de una en una: email de Jira, owner/repo de GitHub y número de Project.

## 3. config.yml resultante (fragmento)

```yaml
jira:
  base_url: "https://acme.atlassian.net"
  email: "ana.perez@acme.com"
  api_token: "env:JIRA_API_TOKEN"
  jql: "project = PAY AND statusCategory != Done ORDER BY created ASC"
github:
  token: "env:GITHUB_TOKEN"
  owner: "acme-inc"
  repo: "payments"
  project_number: 4
```

## 4. Salida esperada del dry-run

```
$ python migrate_jira_to_github.py --config config.yml --dry-run
[dry-run] 42 issues encontrados en Jira (project = PAY).
[dry-run] PAY-101 "Añadir pasarela de pago" -> Issue + Project (Status=In Progress, Priority=P1, Estimate=5)
[dry-run] PAY-102 "Error en checkout"        -> Issue + Project (Status=Backlog,    Priority=P0, Estimate=3)
...
[dry-run] No se ha creado nada. Ejecuta sin --dry-run para migrar de verdad.
```

## 5. Cierre

- Piloto con `--limit 10`, verificación en GitHub, y migración completa.
- Revocar los tokens de Jira y GitHub al terminar.
