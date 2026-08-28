# Glosario para no técnicos

Definiciones cortas de los términos que aparecen durante la migración. Úsalas para explicar
conceptos al usuario en una frase.

- **Script:** un pequeño programa que ejecuta una tarea automáticamente. Aquí, copiar los
  issues de Jira a GitHub.

- **Terminal (PowerShell):** la ventana donde escribes comandos para el ordenador. Es donde
  lanzamos el script.

- **Token / API token (Jira):** una "contraseña temporal" que permite al script leer tus
  datos de Jira sin usar tu contraseña real.

- **PAT (Personal Access Token, GitHub):** lo mismo que un token, pero para GitHub. Le da al
  script permiso para crear issues y usar el Project.

- **Permisos / scopes:** lo que un token puede hacer. Damos solo lo mínimo: `repo` (issues)
  y `project` (proyectos).

- **Variable de entorno:** una forma de guardar un valor (como un token) en la terminal sin
  escribirlo en un fichero. Así el token no queda guardado en ningún sitio.

- **config.yml:** el fichero de configuración donde indicamos tu Jira, tu repositorio y cómo
  se traduce cada dato. Se crea copiando `config.example.yml`.

- **YAML:** el formato del fichero de configuración. Es texto sencillo con `clave: valor` y
  sangrías. Hay que respetar los espacios (usar espacios, no tabuladores).

- **JQL (Jira Query Language):** la forma de decirle a Jira "dame estos issues". Por ejemplo
  `project = ABC AND statusCategory != Done` = "los del proyecto ABC que no están hechos".

- **Issue:** una tarea, historia o bug. Es la unidad de trabajo tanto en Jira como en GitHub.

- **Project (v2) de GitHub:** el tablero de GitHub donde se organizan los issues, con
  columnas y campos como Status, Priority y Estimate. Es el equivalente al tablero de Jira.

- **Campo (field):** una propiedad del issue en el Project, como `Status` (estado),
  `Priority` (prioridad) o `Estimate` (estimación / story points).

- **Label (etiqueta):** una marca de color en el issue de GitHub. El script convierte el
  tipo de Jira (Story, Bug…) en una etiqueta (`type: story`, `type: bug`).

- **Mapeo (mapping):** la tabla de equivalencias. Dice, por ejemplo, que "In Progress" de
  Jira se convierte en "In Progress" del Project, o que un usuario de Jira es tal usuario de
  GitHub.

- **Dry-run (prueba en seco):** una ejecución de mentira que muestra lo que haría el script
  sin crear nada. Sirve para revisar antes de migrar de verdad.

- **Entorno virtual (venv):** una carpeta aislada donde se instalan las piezas que el script
  necesita, sin afectar al resto del ordenador.

- **Rate limit:** un límite de cuántas peticiones puedes hacer por minuto. Si se supera, hay
  que esperar; por eso existe la pausa `throttle_seconds`.
