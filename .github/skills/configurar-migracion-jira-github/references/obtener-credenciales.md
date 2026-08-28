# Cómo obtener las credenciales y los datos necesarios

Guía visual y sencilla para reunir todo lo que pide el script. Comparte estos pasos con el
usuario cuando no sepa de dónde sacar un dato.

---

## 1. Token de Jira (API token)

Sirve para que el script pueda **leer** tus issues de Jira. No da acceso a nada más de lo
que ya puedes ver tú.

1. Entra en https://id.atlassian.com/manage-profile/security/api-tokens
2. Pulsa **"Create API token"** (Crear token).
3. Ponle un nombre que recuerdes, por ejemplo `migracion-github`.
4. Pulsa **"Create"** y luego **"Copy"** para copiar el token.
5. Guárdalo en un sitio seguro y temporal (lo pegarás en la terminal, no en el chat).

> ⚠️ El token solo se muestra **una vez**. Si lo pierdes, crea uno nuevo.

---

## 2. Token de GitHub (Personal Access Token, "PAT")

Sirve para que el script pueda **crear** los issues y añadirlos al Project.

### Opción A — Token clásico (más sencillo)
1. Entra en https://github.com/settings/tokens
2. Pulsa **"Generate new token"** → **"Generate new token (classic)"**.
3. En **Note** pon `migracion-jira`.
4. En **Expiration** elige una caducidad corta (p. ej. 7 días).
5. Marca los permisos (**scopes**): `repo` y `project`.
6. Pulsa **"Generate token"** y **copia** el valor (empieza por `ghp_...`).

### Opción B — Token de grano fino (fine-grained)
1. Entra en https://github.com/settings/tokens?type=beta
2. **Generate new token**.
3. En **Repository access** elige el repositorio de destino.
4. En **Permissions** concede **lectura y escritura** a *Issues* y a *Projects*.
5. Genera y copia el token.

> ⚠️ Igual que en Jira, el token solo se ve **una vez**. Guárdalo con cuidado.

---

## 3. Owner y nombre del repositorio

Mira la URL del repositorio en GitHub:

```
https://github.com/mi-organizacion/mi-repositorio
                    └── owner ──┘ └── repo ──┘
```

- **owner** = lo que va justo después de `github.com/`.
- **repo** = lo siguiente.

---

## 4. Número del Project (v2)

1. Abre tu Project en GitHub (Projects de la organización o del usuario).
2. Mira la URL:
   ```
   https://github.com/orgs/mi-organizacion/projects/7
                                                    └── número del Project = 7
   ```
3. Ese número es el valor de `github.project_number` en `config.yml`.

---

## 5. Clave del proyecto de Jira (para el JQL)

Abre cualquier ticket de Jira del proyecto que quieres migrar. Su código tiene la forma
`ABC-123`. La parte antes del guion (`ABC`) es la **clave del proyecto**.

También puedes leerla directamente de la URL de Jira: el segmento tras `/projects/`
(`.../projects/ABC/...`) o el valor de `projectKey=ABC`.

En `config.yml`, el campo `jql` quedaría así (sustituyendo `ABC`):

```yaml
jql: "project = ABC AND statusCategory != Done ORDER BY created ASC"
```

Esto selecciona los issues de ese proyecto que **no están terminados**. Si quieres migrar
también los terminados, quita la parte `AND statusCategory != Done`.
