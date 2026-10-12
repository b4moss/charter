#!/usr/bin/env python3
"""Sync docs/charter/ from this repository into consumer repos and open PRs.

Intended to run in GitHub Actions (or locally) with:

  SYNC_GITHUB_TOKEN  PAT / app token with contents:write + pull_requests:write
                     on all GitHub consumer repositories
  SYNC_GITEA_TOKEN   Gitea token with write + PR permission
  SYNC_GITEA_URL     optional, default https://git.b4m.jp
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


try:
    import yaml
except ImportError:  # pragma: no cover
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    raise SystemExit(2)


BRANCH_PREFIX = "update-charter"


@dataclass
class Target:
    forge: str  # github | gitea
    repo: str
    base: str


@dataclass
class SyncResult:
    repo: str
    forge: str
    status: str
    pr_url: str = ""
    base: str = ""
    local_mods: list[dict[str, Any]] = field(default_factory=list)
    detail: str = ""


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=merged,
        text=True,
        capture_output=True,
        check=check,
    )


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_targets(path: Path) -> list[Target]:
    data = yaml.safe_load(path.read_text()) or {}
    out: list[Target] = []
    for item in data.get("github") or []:
        out.append(Target("github", item["repo"], item.get("base") or "main"))
    for item in data.get("gitea") or []:
        out.append(Target("gitea", item["repo"], item.get("base") or "main"))
    return out


def release_hashes(charter_git: Path) -> dict[str, dict[str, str]]:
    """relpath -> {tag: sha256} for docs/charter across v* tags."""
    tags_proc = run(["git", "tag", "-l", "v*"], cwd=charter_git, check=False)
    tags = [t for t in tags_proc.stdout.splitlines() if t.strip()]
    out: dict[str, dict[str, str]] = {}
    with tempfile.TemporaryDirectory(prefix="charter-tags-") as tmp:
        root = Path(tmp)
        for tag in tags:
            dest = root / tag
            dest.mkdir(parents=True, exist_ok=True)
            proc = subprocess.run(
                ["git", "archive", tag, "docs/charter"],
                cwd=str(charter_git),
                capture_output=True,
                check=False,
            )
            if proc.returncode != 0 or not proc.stdout:
                continue
            subprocess.run(["tar", "-x", "-C", str(dest)], input=proc.stdout, check=True)
            charter_dir = dest / "docs" / "charter"
            if not charter_dir.exists():
                continue
            for p in charter_dir.rglob("*"):
                if not p.is_file():
                    continue
                rel = str(p.relative_to(charter_dir)).replace("\\", "/")
                out.setdefault(rel, {})[tag] = file_hash(p)
    return out


def detect_local_mods(repo_charter: Path, known: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    if not repo_charter.exists():
        return [{"path": "(missing docs/charter)", "reason": "missing"}]
    mods: list[dict[str, Any]] = []
    for p in sorted(repo_charter.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(repo_charter)).replace("\\", "/")
        digest = file_hash(p)
        if rel in known and digest in known[rel].values():
            continue
        if rel in known:
            mods.append(
                {
                    "path": rel,
                    "reason": "content-differs-from-all-releases",
                    "known_tags": sorted(known[rel].keys()),
                }
            )
        else:
            mods.append({"path": rel, "reason": "extra-file-not-in-any-release"})
    return mods


def api_request(
    url: str,
    *,
    token: str,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    forge: str = "github",
) -> tuple[int, Any]:
    data = None
    headers = {"Accept": "application/json", "User-Agent": "charter-sync"}
    if forge == "github":
        headers["Authorization"] = f"Bearer {token}"
        headers["X-GitHub-Api-Version"] = "2022-11-28"
    else:
        headers["Authorization"] = f"token {token}"
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            parsed = json.loads(raw) if raw else {"message": str(e)}
        except json.JSONDecodeError:
            parsed = {"message": raw or str(e)}
        return e.code, parsed


def github_clone_url(repo: str, token: str) -> str:
    return f"https://x-access-token:{token}@github.com/{repo}.git"


def gitea_clone_url(repo: str, token: str, host: str) -> str:
    host = host.rstrip("/")
    parsed = urllib.parse.urlparse(host)
    netloc = f"oauth2:{token}@{parsed.netloc}"
    return urllib.parse.urlunparse(("https", netloc, f"/{repo}.git", "", "", ""))


def replace_charter(dest_repo: Path, source_charter: Path) -> None:
    target = dest_repo / "docs" / "charter"
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_charter, target)


def git_commit_all(repo_dir: Path, message: str) -> bool:
    run(["git", "add", "-A", "docs/charter"], cwd=repo_dir)
    status = run(["git", "status", "--porcelain", "docs/charter"], cwd=repo_dir, check=False)
    if not status.stdout.strip():
        return False
    env = {
        "GIT_AUTHOR_NAME": "charter-sync",
        "GIT_AUTHOR_EMAIL": "charter-sync@users.noreply.github.com",
        "GIT_COMMITTER_NAME": "charter-sync",
        "GIT_COMMITTER_EMAIL": "charter-sync@users.noreply.github.com",
    }
    run(
        ["git", "-c", "commit.gpgsign=false", "commit", "-m", message],
        cwd=repo_dir,
        env=env,
    )
    return True


def ensure_branch(repo_dir: Path, branch: str) -> None:
    run(["git", "checkout", "-B", branch], cwd=repo_dir)


def pr_body(version: str, base: str, local_mods: list[dict[str, Any]]) -> str:
    mods_section = "なし"
    if local_mods:
        lines = [f"- `{m.get('path')}` ({m.get('reason')})" for m in local_mods]
        mods_section = "\n".join(lines)
    return f"""## Summary
`docs/charter/` を [b4moss/charter@{version}](https://github.com/b4moss/charter/releases/tag/{version}) に同期しました。

### 方針
- charter 正本で `docs/charter/` を上書き
- ベースブランチ: `{base}`

### 上書き前に検出したローカル改変
{mods_section}

---
Automated by `scripts/sync-charter` in b4moss/charter.
"""


def sync_github(
    target: Target,
    *,
    source_charter: Path,
    version: str,
    token: str,
    known: dict[str, dict[str, str]],
    work_root: Path,
    dry_run: bool,
) -> SyncResult:
    branch = f"{BRANCH_PREFIX}-{version.lstrip('v')}"
    result = SyncResult(target.repo, "github", "pending", base=target.base)
    dir_ = work_root / f"gh__{target.repo.replace('/', '__')}"
    if dir_.exists():
        shutil.rmtree(dir_)
    clone = run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            target.base,
            github_clone_url(target.repo, token),
            str(dir_),
        ],
        check=False,
    )
    if clone.returncode != 0:
        result.status = "clone_failed"
        result.detail = (clone.stderr or clone.stdout)[-500:]
        return result

    result.local_mods = detect_local_mods(dir_ / "docs" / "charter", known)
    if dry_run:
        result.status = "dry_run"
        return result

    ensure_branch(dir_, branch)
    replace_charter(dir_, source_charter)
    message = f"docs: sync charter to {version}\n\nSync docs/charter/ with b4moss/charter@{version}."
    changed = git_commit_all(dir_, message)
    if not changed:
        # still report existing PR if any
        code, data = api_request(
            f"https://api.github.com/repos/{target.repo}/pulls?head={target.repo.split('/')[0]}:{branch}&base={target.base}&state=open",
            token=token,
        )
        if code == 200 and data:
            result.pr_url = data[0].get("html_url", "")
            result.status = "unchanged_existing_pr" if result.pr_url else "unchanged"
        else:
            result.status = "unchanged"
        return result

    push = run(
        ["git", "push", "--force", github_clone_url(target.repo, token), f"HEAD:{branch}"],
        cwd=dir_,
        check=False,
    )
    if push.returncode != 0:
        result.status = "push_failed"
        result.detail = (push.stderr or push.stdout)[-500:]
        return result

    # find or create PR
    owner = target.repo.split("/")[0]
    code, data = api_request(
        f"https://api.github.com/repos/{target.repo}/pulls?head={owner}:{branch}&base={target.base}&state=open",
        token=token,
    )
    if code == 200 and data:
        result.pr_url = data[0]["html_url"]
        result.status = "updated_existing_pr"
        return result

    code, data = api_request(
        f"https://api.github.com/repos/{target.repo}/pulls",
        token=token,
        method="POST",
        body={
            "title": f"docs: sync charter to {version}",
            "head": branch,
            "base": target.base,
            "body": pr_body(version, target.base, result.local_mods),
        },
    )
    if code in (200, 201) and isinstance(data, dict):
        result.pr_url = data.get("html_url", "")
        result.status = "pr_created"
    else:
        result.status = "pr_failed"
        result.detail = json.dumps(data, ensure_ascii=False)[:500]
    return result


def sync_gitea(
    target: Target,
    *,
    source_charter: Path,
    version: str,
    token: str,
    host: str,
    known: dict[str, dict[str, str]],
    work_root: Path,
    dry_run: bool,
) -> SyncResult:
    branch = f"{BRANCH_PREFIX}-{version.lstrip('v')}"
    result = SyncResult(target.repo, "gitea", "pending", base=target.base)
    dir_ = work_root / f"gte__{target.repo.replace('/', '__')}"
    if dir_.exists():
        shutil.rmtree(dir_)
    clone_url = gitea_clone_url(target.repo, token, host)
    clone = run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            target.base,
            clone_url,
            str(dir_),
        ],
        check=False,
    )
    if clone.returncode != 0:
        result.status = "clone_failed"
        result.detail = (clone.stderr or clone.stdout)[-500:]
        return result

    result.local_mods = detect_local_mods(dir_ / "docs" / "charter", known)
    if dry_run:
        result.status = "dry_run"
        return result

    ensure_branch(dir_, branch)
    replace_charter(dir_, source_charter)
    message = f"docs: sync charter to {version}\n\nSync docs/charter/ with b4moss/charter@{version}."
    changed = git_commit_all(dir_, message)
    owner, name = target.repo.split("/", 1)
    api = host.rstrip("/") + "/api/v1"

    if not changed:
        code, data = api_request(
            f"{api}/repos/{owner}/{name}/pulls?state=open",
            token=token,
            forge="gitea",
        )
        if code == 200 and isinstance(data, list):
            for pr in data:
                if pr.get("head", {}).get("ref") == branch:
                    result.pr_url = pr.get("html_url", "")
                    break
        result.status = "unchanged_existing_pr" if result.pr_url else "unchanged"
        return result

    push = run(
        ["git", "push", "--force", clone_url, f"HEAD:{branch}"],
        cwd=dir_,
        check=False,
    )
    if push.returncode != 0:
        result.status = "push_failed"
        result.detail = (push.stderr or push.stdout)[-500:]
        return result

    code, data = api_request(
        f"{api}/repos/{owner}/{name}/pulls?state=open",
        token=token,
        forge="gitea",
    )
    if code == 200 and isinstance(data, list):
        for pr in data:
            if pr.get("head", {}).get("ref") == branch:
                result.pr_url = pr.get("html_url", "")
                result.status = "updated_existing_pr"
                return result

    code, data = api_request(
        f"{api}/repos/{owner}/{name}/pulls",
        token=token,
        method="POST",
        forge="gitea",
        body={
            "title": f"docs: sync charter to {version}",
            "head": branch,
            "base": target.base,
            "body": pr_body(version, target.base, result.local_mods),
        },
    )
    if code in (200, 201) and isinstance(data, dict):
        result.pr_url = data.get("html_url", "")
        result.status = "pr_created"
    else:
        result.status = "pr_failed"
        result.detail = json.dumps(data, ensure_ascii=False)[:500]
    return result


def write_summary(results: list[SyncResult], path: Path) -> None:
    lines = ["# charter sync summary", ""]
    for r in results:
        mods = len(r.local_mods)
        lines.append(
            f"- `{r.forge}:{r.repo}` status=`{r.status}` base=`{r.base}` "
            f"local_mods={mods} pr={r.pr_url or '-'} {r.detail}"
        )
    path.write_text("\n".join(lines) + "\n")
    print(path.read_text())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--targets",
        type=Path,
        default=Path(__file__).resolve().parent / "targets.yaml",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("docs/charter"),
        help="Path to docs/charter to distribute",
    )
    parser.add_argument(
        "--charter-git",
        type=Path,
        default=Path("."),
        help="Git root of b4moss/charter (for release hash comparison)",
    )
    parser.add_argument("--version", required=True, help="Version/tag being synced, e.g. v1.3.0")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only-forge", choices=["github", "gitea"], default=None)
    parser.add_argument("--summary", type=Path, default=Path("charter-sync-summary.md"))
    args = parser.parse_args()

    source = args.source.resolve()
    if not source.is_dir():
        print(f"source charter dir not found: {source}", file=sys.stderr)
        return 2

    gh_token = os.environ.get("SYNC_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    gitea_token = os.environ.get("SYNC_GITEA_TOKEN") or ""
    gitea_url = os.environ.get("SYNC_GITEA_URL") or "https://git.b4m.jp"

    targets = load_targets(args.targets)
    if args.only_forge:
        targets = [t for t in targets if t.forge == args.only_forge]

    print(f"targets={len(targets)} version={args.version} dry_run={args.dry_run}")
    known = release_hashes(args.charter_git.resolve())
    print(f"known release files indexed from {len(set(t for m in known.values() for t in m))} tag entries")

    results: list[SyncResult] = []
    with tempfile.TemporaryDirectory(prefix="charter-sync-work-") as tmp:
        work_root = Path(tmp)
        for target in targets:
            print(f"==> {target.forge}:{target.repo} (base={target.base})", flush=True)
            if target.forge == "github":
                if not gh_token and not args.dry_run:
                    results.append(
                        SyncResult(
                            target.repo,
                            "github",
                            "skipped_no_token",
                            base=target.base,
                            detail="SYNC_GITHUB_TOKEN missing",
                        )
                    )
                    continue
                results.append(
                    sync_github(
                        target,
                        source_charter=source,
                        version=args.version,
                        token=gh_token or "dry-run",
                        known=known,
                        work_root=work_root,
                        dry_run=args.dry_run,
                    )
                )
            else:
                if not gitea_token and not args.dry_run:
                    results.append(
                        SyncResult(
                            target.repo,
                            "gitea",
                            "skipped_no_token",
                            base=target.base,
                            detail="SYNC_GITEA_TOKEN missing",
                        )
                    )
                    continue
                results.append(
                    sync_gitea(
                        target,
                        source_charter=source,
                        version=args.version,
                        token=gitea_token or "dry-run",
                        host=gitea_url,
                        known=known,
                        work_root=work_root,
                        dry_run=args.dry_run,
                    )
                )

    write_summary(results, args.summary)

    # Also emit machine-readable local-mod report
    mods_path = args.summary.with_name("charter-sync-local-mods.json")
    mods_path.write_text(
        json.dumps(
            [{"repo": r.repo, "forge": r.forge, "mods": r.local_mods} for r in results if r.local_mods],
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )

    if any(r.status.endswith("failed") for r in results):
        return 1
    if any(r.status == "skipped_no_token" for r in results) and not args.dry_run:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
