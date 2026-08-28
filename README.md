# Formación: de Jira a GitHub Projects

Material de formación para los **Scrum Masters** de la organización sobre cómo migrar la operativa de **Jira** a **GitHub Projects**.

> 🎯 **Objetivo:** no replicar el Jira actual, sino entender las posibilidades de GitHub Projects y definir una estructura **sencilla, homogénea y mantenible** para cada área.

## Contenido de la carpeta

| Carpeta | Qué contiene | Para quién |
|---------|--------------|------------|
| [`01-Documentacion/`](01-Documentacion/guia-github-projects.md) | Guía completa de GitHub Projects, conceptos, equivalencias Jira→GitHub, estructura recomendada y enlaces oficiales. | Lectura base para todos. |
| [`02-Presentacion/`](02-Presentacion/Formaci%C3%B3n%20Github%20Project%20v0.pdf) | Presentación en PDF para impartir la formación. | Formador. |
| [`03-Script-Migracion/`](03-Script-Migracion/README.md) | Script de Python para migrar issues de Jira a GitHub + fichero de configuración y su README. | Quien ejecute la migración. |
| [`.github/skills/`](.github/skills/configurar-migracion-jira-github/SKILL.md) | Skill que guía a un perfil **no técnico** para configurar y lanzar el script de migración, con inferencia automática desde la URL de Jira. | Quien ejecute la migración asistido por IA. |

## Ruta de aprendizaje sugerida

1. **Leer** la guía en `01-Documentacion/`.
2. **Ver** el vídeo oficial de introducción: https://www.youtube.com/watch?v=c67GaAkf1BE
3. **Impartir/asistir** a la formación con la presentación de `02-Presentacion/`.
4. **Practicar** la migración con el script de `03-Script-Migracion/` en un proyecto piloto,
   o usar la **skill asistida** de `.github/skills/` si no tienes perfil técnico.

## Migración asistida por IA (skill)

La carpeta [`.github/skills/configurar-migracion-jira-github/`](.github/skills/configurar-migracion-jira-github/SKILL.md)
contiene una **skill** que acompaña a un perfil **no técnico** en todo el proceso:

- **Infiere** la configuración a partir de un mensaje con la URL de Jira
  (p. ej. *"Quiero migrar este proyecto de JIRA `<URL>` a un project en GitHub"*).
- **Guía** paso a paso para obtener credenciales, rellenar `config.yml` y preparar el entorno.
- **Valida y lanza** el script (`--dry-run`, piloto y migración completa).

Es **autocontenida**: incluye su propia copia del script en `scripts/`, además de
`references/` (base de conocimiento), `templates/` (plantilla de `config.yml`),
`examples/` (sesión de ejemplo) y `scripts/validar-configuracion.ps1` (comprobación previa).

## Recursos oficiales

- 📘 Quickstart: https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/quickstart-for-projects
- 📘 Best Practices: https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects
- 📘 Documentación completa: https://docs.github.com/en/issues/planning-and-tracking-with-projects
