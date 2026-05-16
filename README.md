# Origin CLI Harness Skill

Build CLI-Anything style command-line harnesses for OriginLab Origin on Windows using COM Automation and LabTalk.

This skill is focused on the CLI integration pattern: make Origin controllable from Codex, Claude Code, OpenCode, PowerShell, or any agent/tool that can call a command-line interface. It avoids brittle GUI coordinate clicking and wraps Origin's native automation surfaces instead.

## Compatibility

Tested environment:

- OriginLab Origin 2024, installed at `D:\Program Files\OriginLab\Origin2024`
- Windows desktop session with Origin COM Automation registered
- Python 3.12
- GitHub CLI 2.92.0 for publishing this repository

Expected compatible environment:

- OriginLab Origin versions that expose `Origin.ApplicationSI`, `Origin.ApplicationCOMSI`, or `Origin.Application`
- Windows with `pywin32`
- Python 3.9+

Origin must be licensed and able to launch interactively. First-run dialogs, license prompts, or update prompts should be cleared manually before unattended CLI use.

## Related Repositories

- This skill repository: <https://github.com/AKI-215/origin-cli-harness>
- CLI-Anything upstream project: <https://github.com/HKUDS/CLI-Anything>
- CLI-Anything OpenCode support documentation: <https://github.com/HKUDS/CLI-Anything/blob/main/README_CN.md#-opencode-%E5%AE%9E%E9%AA%8C%E6%80%A7%E6%94%AF%E6%8C%81>

## What It Provides

- A Codex-compatible `SKILL.md` for triggering Origin CLI harness work.
- A scaffold script that generates an installable `cli-anything-origin` Python package.
- A reference note for Origin COM ProgIDs, LabTalk patterns, path escaping, and common failure modes.
- UI metadata in `agents/openai.yaml`.

## Repository Layout

```text
origin-cli-harness/
  SKILL.md
  README.md
  README_CN.md
  agents/
    openai.yaml
  references/
    origin-com-labtalk.md
  scripts/
    scaffold_origin_harness.py
```

## Install As A Codex Skill

Copy or clone this folder into your Codex skills directory:

```powershell
git clone https://github.com/<your-name>/origin-cli-harness.git "$env:USERPROFILE\.codex\skills\origin-cli-harness"
```

Restart Codex so it discovers the new skill.

## Generate An Origin CLI Harness

```powershell
python "$env:USERPROFILE\.codex\skills\origin-cli-harness\scripts\scaffold_origin_harness.py" `
  --output ".\origin\agent-harness" `
  --install-dir "D:\Program Files\OriginLab\Origin2024"

cd .\origin\agent-harness
python -m pip install -e .
python -m cli_anything.origin --json info
```

If installation succeeds, you can continue with:

```powershell
python -m cli_anything.origin --json status
python -m cli_anything.origin --json labtalk "type -a `"connected`";"
python -m cli_anything.origin --json new-project
python -m cli_anything.origin --json save-project ".\origin-test.opju"
```

## Design Notes

- Use COM Automation first: `Origin.ApplicationSI`, `Origin.ApplicationCOMSI`, then `Origin.Application`.
- Use LabTalk through `app.Execute(...)` for native Origin operations.
- Keep `info` safe: it must not launch Origin.
- Keep `--json` output pure for machine readers.
- Prefer `python -m cli_anything.origin` because Python user script directories are often not on `PATH`.
- Treat `.opju` as the authoritative artifact; figure export can be path-sensitive in Origin.

## Requirements

- Windows
- Licensed OriginLab Origin installation
- Python 3.9+
- `click`
- `pywin32`

The generated harness declares `click` and `pywin32` in `setup.py`.

## Validation

Validate the skill folder itself:

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .\origin-cli-harness
```

Validate a generated harness:

```powershell
python -m cli_anything.origin --json info
python -m cli_anything.origin --json status --no-launch
```

`status --no-launch` should fail cleanly with JSON if Origin is closed.
