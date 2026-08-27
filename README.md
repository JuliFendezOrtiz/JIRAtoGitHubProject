# Formación: de Jira a GitHub Projects

Material de formación para los **Scrum Masters** de la organización sobre cómo migrar la operativa de **Jira** a **GitHub Projects**.

> 🎯 **Objetivo:** no replicar el Jira actual, sino entender las posibilidades de GitHub Projects y definir una estructura **sencilla, homogénea y mantenible** para cada área.

## Contenido de la carpeta

| Carpeta | Qué contiene | Para quién |
|---------|--------------|------------|
| [`01-Documentacion/`](01-Documentacion/guia-github-projects.md) | Guía completa de GitHub Projects, conceptos, equivalencias Jira→GitHub, estructura recomendada y enlaces oficiales. | Lectura base para todos. |
| [`02-Presentacion/`](02-Presentacion/presentacion-formacion.md) | Presentación de 6 diapositivas (formato Marp) para impartir la formación. | Formador. |
| [`03-Script-Migracion/`](03-Script-Migracion/README.md) | Script de Python para migrar issues de Jira a GitHub + fichero de configuración y su README. | Quien ejecute la migración. |

## Ruta de aprendizaje sugerida

1. **Leer** la guía en `01-Documentacion/`.
2. **Ver** el vídeo oficial de introducción: https://www.youtube.com/watch?v=c67GaAkf1BE
3. **Impartir/asistir** a la formación con la presentación de `02-Presentacion/`.
4. **Practicar** la migración con el script de `03-Script-Migracion/` en un proyecto piloto.

## Recursos oficiales

- 📘 Quickstart: https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/quickstart-for-projects
- 📘 Best Practices: https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects
- 📘 Documentación completa: https://docs.github.com/en/issues/planning-and-tracking-with-projects

## Cómo ver la presentación como diapositivas

La presentación está en formato **Marp** (Markdown):

1. Instala la extensión **"Marp for VS Code"**.
2. Abre `02-Presentacion/presentacion-formacion.md` y pulsa *Open Preview*.
3. Para exportar a PDF o PPTX: comando *"Marp: Export Slide Deck..."*.
