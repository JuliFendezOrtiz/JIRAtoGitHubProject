#!/usr/bin/env python3
"""Migración de issues de Jira a GitHub Issues + GitHub Projects (v2).

Lee la configuración desde un fichero YAML, extrae los issues de Jira mediante
su API REST y los recrea como GitHub Issues, añadiéndolos a un Project (v2) y
rellenando los campos personalizados (Status, Priority, Estimate...).

Uso:
    python migrate_jira_to_github.py --config config.yml
    python migrate_jira_to_github.py --config config.yml --dry-run
    python migrate_jira_to_github.py --config config.yml --limit 10

Consulta el README.md para la descripción completa de la configuración.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Any

import requests
import yaml

GITHUB_API = "https://api.github.com"
GITHUB_GRAPHQL = "https://api.github.com/graphql"


# --------------------------------------------------------------------------- #
# Configuración
# --------------------------------------------------------------------------- #
@dataclass
class Config:
    """Configuración tipada cargada desde el YAML."""

    jira: dict[str, Any]
    github: dict[str, Any]
    mapping: dict[str, Any] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def load(path: str) -> "Config":
        with open(path, "r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}

        cfg = Config(
            jira=raw.get("jira", {}),
            github=raw.get("github", {}),
            mapping=raw.get("mapping", {}),
            options=raw.get("options", {}),
        )
        cfg._resolve_env()
        cfg._validate()
        return cfg

    def _resolve_env(self) -> None:
        """Permite usar ${VAR} o env:VAR en tokens/credenciales sensibles."""
        for section in (self.jira, self.github):
            for key, value in list(section.items()):
                if isinstance(value, str):
                    section[key] = _expand_env(value)

    def _validate(self) -> None:
        required = {
            "jira": ["base_url", "email", "api_token", "jql"],
            "github": ["token", "owner", "repo"],
        }
        errors: list[str] = []
        for section_name, keys in required.items():
            section = getattr(self, section_name)
            for key in keys:
                if not section.get(key):
                    errors.append(f"Falta '{section_name}.{key}' en la configuración.")
        if errors:
            raise SystemExit("Configuración inválida:\n  - " + "\n  - ".join(errors))


def _expand_env(value: str) -> str:
    """Resuelve ${VAR} y el prefijo env:VAR contra variables de entorno."""
    if value.startswith("env:"):
        var = value[len("env:") :]
        resolved = os.environ.get(var)
        if resolved is None:
            raise SystemExit(f"La variable de entorno '{var}' no está definida.")
        return resolved
    return os.path.expandvars(value)


# --------------------------------------------------------------------------- #
# Cliente de Jira
# --------------------------------------------------------------------------- #
class JiraClient:
    def __init__(self, base_url: str, email: str, api_token: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = (email, api_token)
        self.session.headers.update({"Accept": "application/json"})

    def search_issues(self, jql: str, limit: int | None = None) -> list[dict[str, Any]]:
        """Devuelve todos los issues que cumplen el JQL, paginando."""
        issues: list[dict[str, Any]] = []
        start_at = 0
        page_size = 50
        while True:
            params = {
                "jql": jql,
                "startAt": start_at,
                "maxResults": page_size,
                "fields": "*all",
            }
            resp = self.session.get(f"{self.base_url}/rest/api/2/search", params=params)
            _raise_for_status(resp, "Jira search")
            data = resp.json()
            batch = data.get("issues", [])
            issues.extend(batch)

            if limit and len(issues) >= limit:
                return issues[:limit]
            start_at += page_size
            if start_at >= data.get("total", 0) or not batch:
                break
        return issues

    def get_comments(self, issue_key: str) -> list[dict[str, Any]]:
        resp = self.session.get(
            f"{self.base_url}/rest/api/2/issue/{issue_key}/comment"
        )
        _raise_for_status(resp, f"Jira comments {issue_key}")
        return resp.json().get("comments", [])


# --------------------------------------------------------------------------- #
# Cliente de GitHub (REST + GraphQL para Projects v2)
# --------------------------------------------------------------------------- #
class GitHubClient:
    def __init__(self, token: str, owner: str, repo: str):
        self.owner = owner
        self.repo = repo
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    # --- REST: Issues --------------------------------------------------------
    def ensure_label(self, name: str, color: str = "ededed") -> None:
        resp = self.session.get(
            f"{GITHUB_API}/repos/{self.owner}/{self.repo}/labels/{name}"
        )
        if resp.status_code == 200:
            return
        self.session.post(
            f"{GITHUB_API}/repos/{self.owner}/{self.repo}/labels",
            json={"name": name, "color": color},
        )

    def create_issue(
        self,
        title: str,
        body: str,
        labels: list[str],
        assignees: list[str],
    ) -> dict[str, Any]:
        payload = {"title": title, "body": body}
        if labels:
            payload["labels"] = labels
        if assignees:
            payload["assignees"] = assignees
        resp = self.session.post(
            f"{GITHUB_API}/repos/{self.owner}/{self.repo}/issues", json=payload
        )
        _raise_for_status(resp, "GitHub create issue")
        return resp.json()

    def add_comment(self, issue_number: int, body: str) -> None:
        resp = self.session.post(
            f"{GITHUB_API}/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments",
            json={"body": body},
        )
        _raise_for_status(resp, "GitHub add comment")

    # --- GraphQL: Projects v2 ------------------------------------------------
    def graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        resp = self.session.post(
            GITHUB_GRAPHQL, json={"query": query, "variables": variables}
        )
        _raise_for_status(resp, "GitHub GraphQL")
        data = resp.json()
        if "errors" in data:
            raise SystemExit(f"Error GraphQL: {data['errors']}")
        return data["data"]

    def get_project(self, project_number: int) -> dict[str, Any]:
        """Obtiene el id del Project y el detalle de sus campos."""
        query = """
        query($owner: String!, $number: Int!) {
          organization(login: $owner) {
            projectV2(number: $number) { id fields(first: 50) { nodes {
              ... on ProjectV2FieldCommon { id name }
              ... on ProjectV2SingleSelectField { id name options { id name } }
            } } }
          }
          user(login: $owner) {
            projectV2(number: $number) { id fields(first: 50) { nodes {
              ... on ProjectV2FieldCommon { id name }
              ... on ProjectV2SingleSelectField { id name options { id name } }
            } } }
          }
        }
        """
        data = self.graphql(query, {"owner": self.owner, "number": project_number})
        project = (data.get("organization") or {}).get("projectV2") or (
            data.get("user") or {}
        ).get("projectV2")
        if not project:
            raise SystemExit(
                f"No se encontró el Project #{project_number} para '{self.owner}'."
            )
        return project

    def add_issue_to_project(self, project_id: str, issue_node_id: str) -> str:
        query = """
        mutation($projectId: ID!, $contentId: ID!) {
          addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
            item { id }
          }
        }
        """
        data = self.graphql(
            query, {"projectId": project_id, "contentId": issue_node_id}
        )
        return data["addProjectV2ItemById"]["item"]["id"]

    def set_single_select(
        self, project_id: str, item_id: str, field_id: str, option_id: str
    ) -> None:
        query = """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
          updateProjectV2ItemFieldValue(input: {
            projectId: $projectId, itemId: $itemId, fieldId: $fieldId,
            value: {singleSelectOptionId: $optionId}
          }) { projectV2Item { id } }
        }
        """
        self.graphql(
            query,
            {
                "projectId": project_id,
                "itemId": item_id,
                "fieldId": field_id,
                "optionId": option_id,
            },
        )

    def set_number(
        self, project_id: str, item_id: str, field_id: str, number: float
    ) -> None:
        query = """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $number: Float!) {
          updateProjectV2ItemFieldValue(input: {
            projectId: $projectId, itemId: $itemId, fieldId: $fieldId,
            value: {number: $number}
          }) { projectV2Item { id } }
        }
        """
        self.graphql(
            query,
            {
                "projectId": project_id,
                "itemId": item_id,
                "fieldId": field_id,
                "number": number,
            },
        )


# --------------------------------------------------------------------------- #
# Lógica de migración
# --------------------------------------------------------------------------- #
class Migrator:
    def __init__(self, cfg: Config, dry_run: bool = False):
        self.cfg = cfg
        self.dry_run = dry_run
        self.jira = JiraClient(
            cfg.jira["base_url"], cfg.jira["email"], cfg.jira["api_token"]
        )
        self.gh = GitHubClient(
            cfg.github["token"], cfg.github["owner"], cfg.github["repo"]
        )
        self.project: dict[str, Any] | None = None
        self.field_index: dict[str, dict[str, Any]] = {}

    def run(self, limit: int | None = None) -> None:
        print(f"Buscando issues en Jira con JQL: {self.cfg.jira['jql']}")
        issues = self.jira.search_issues(self.cfg.jira["jql"], limit=limit)
        print(f"Encontrados {len(issues)} issues.")

        project_number = self.cfg.github.get("project_number")
        if project_number and not self.dry_run:
            self.project = self.gh.get_project(int(project_number))
            self.field_index = {
                f["name"]: f for f in self.project["fields"]["nodes"] if f.get("name")
            }
            print(f"Project #{project_number} cargado ({len(self.field_index)} campos).")

        migrated = 0
        for issue in issues:
            try:
                self._migrate_one(issue)
                migrated += 1
            except Exception as exc:  # noqa: BLE001 - continuar con el resto
                key = issue.get("key", "?")
                print(f"  [ERROR] {key}: {exc}", file=sys.stderr)
            time.sleep(self.cfg.options.get("throttle_seconds", 0.5))

        print(f"\nCompletado. {migrated}/{len(issues)} issues migrados.")
        if self.dry_run:
            print("(dry-run: no se ha creado nada en GitHub)")

    def _migrate_one(self, issue: dict[str, Any]) -> None:
        key = issue["key"]
        fields = issue.get("fields", {})
        summary = fields.get("summary", "(sin título)")
        title = f"[{key}] {summary}"

        labels = self._labels_for(fields)
        assignees = self._assignees_for(fields)
        body = self._body_for(key, fields)

        print(f"- {key}: {summary}")
        if self.dry_run:
            print(f"    labels={labels} assignees={assignees}")
            return

        for label in labels:
            self.gh.ensure_label(label)

        gh_issue = self.gh.create_issue(title, body, labels, assignees)
        issue_number = gh_issue["number"]
        node_id = gh_issue["node_id"]

        if self.cfg.options.get("migrate_comments", True):
            self._migrate_comments(key, issue_number)

        if self.project:
            self._add_to_project(node_id, fields)

    # --- helpers de mapeo ----------------------------------------------------
    def _labels_for(self, fields: dict[str, Any]) -> list[str]:
        labels: list[str] = []
        issue_type = (fields.get("issuetype") or {}).get("name", "")
        type_map = self.cfg.mapping.get("issue_type_to_label", {})
        mapped = type_map.get(issue_type)
        if mapped:
            labels.append(mapped)
        for extra in self.cfg.mapping.get("extra_labels", []):
            labels.append(extra)
        return labels

    def _assignees_for(self, fields: dict[str, Any]) -> list[str]:
        assignee = fields.get("assignee") or {}
        jira_user = assignee.get("emailAddress") or assignee.get("displayName")
        user_map = self.cfg.mapping.get("users", {})
        gh_user = user_map.get(jira_user)
        return [gh_user] if gh_user else []

    def _body_for(self, key: str, fields: dict[str, Any]) -> str:
        description = fields.get("description") or "_Sin descripción._"
        jira_url = f"{self.cfg.jira['base_url'].rstrip('/')}/browse/{key}"
        status = (fields.get("status") or {}).get("name", "")
        reporter = (fields.get("reporter") or {}).get("displayName", "")
        parts = [
            description,
            "\n\n---",
            f"**Origen Jira:** [{key}]({jira_url})",
        ]
        if status:
            parts.append(f"**Estado original:** {status}")
        if reporter:
            parts.append(f"**Reporter original:** {reporter}")
        return "\n".join(parts)

    def _migrate_comments(self, key: str, issue_number: int) -> None:
        for comment in self.jira.get_comments(key):
            author = (comment.get("author") or {}).get("displayName", "desconocido")
            created = comment.get("created", "")
            body = comment.get("body", "")
            self.gh.add_comment(
                issue_number, f"**{author}** ({created}):\n\n{body}"
            )

    def _add_to_project(self, node_id: str, fields: dict[str, Any]) -> None:
        assert self.project is not None
        item_id = self.gh.add_issue_to_project(self.project["id"], node_id)

        # Status
        self._apply_single_select(
            item_id,
            field_name=self.cfg.mapping.get("status_field", "Status"),
            value=self._map_status(fields),
        )
        # Priority
        self._apply_single_select(
            item_id,
            field_name=self.cfg.mapping.get("priority_field", "Priority"),
            value=self._map_priority(fields),
        )
        # Estimate (story points)
        estimate = self._map_estimate(fields)
        if estimate is not None:
            self._apply_number(
                item_id,
                field_name=self.cfg.mapping.get("estimate_field", "Estimate"),
                value=estimate,
            )

    def _apply_single_select(
        self, item_id: str, field_name: str, value: str | None
    ) -> None:
        if not value:
            return
        field = self.field_index.get(field_name)
        if not field or "options" not in field:
            return
        option = next(
            (o for o in field["options"] if o["name"].lower() == value.lower()), None
        )
        if not option:
            return
        self.gh.set_single_select(
            self.project["id"], item_id, field["id"], option["id"]  # type: ignore[index]
        )

    def _apply_number(self, item_id: str, field_name: str, value: float) -> None:
        field = self.field_index.get(field_name)
        if not field:
            return
        self.gh.set_number(self.project["id"], item_id, field["id"], value)  # type: ignore[index]

    def _map_status(self, fields: dict[str, Any]) -> str | None:
        jira_status = (fields.get("status") or {}).get("name")
        return self.cfg.mapping.get("status", {}).get(jira_status)

    def _map_priority(self, fields: dict[str, Any]) -> str | None:
        jira_priority = (fields.get("priority") or {}).get("name")
        return self.cfg.mapping.get("priority", {}).get(jira_priority)

    def _map_estimate(self, fields: dict[str, Any]) -> float | None:
        field_id = self.cfg.mapping.get("story_points_field")
        if not field_id:
            return None
        value = fields.get(field_id)
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None


# --------------------------------------------------------------------------- #
# Utilidades
# --------------------------------------------------------------------------- #
def _raise_for_status(resp: requests.Response, context: str) -> None:
    if resp.status_code >= 400:
        raise RuntimeError(f"{context} falló ({resp.status_code}): {resp.text[:500]}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migra issues de Jira a GitHub Issues + Projects."
    )
    parser.add_argument("--config", required=True, help="Ruta al fichero YAML.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra lo que se haría sin crear nada en GitHub.",
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Máximo de issues a migrar."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = Config.load(args.config)
    Migrator(cfg, dry_run=args.dry_run).run(limit=args.limit)


if __name__ == "__main__":
    main()
