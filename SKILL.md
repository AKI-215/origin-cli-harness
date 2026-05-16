---
name: origin-cli-harness
description: Build or refine command-line harnesses for OriginLab Origin on Windows using CLI-Anything patterns, COM Automation, and LabTalk. Use when the user wants Origin controlled from Codex/Claude/OpenCode/terminal; wants a reproducible CLI around Origin; needs to import data, create Origin projects, run LabTalk, plot graphs, save .opj/.opju, or export figures without brittle GUI clicking.
---

# Origin CLI Harness

Use this skill to connect OriginLab Origin to an agent-friendly command line. Prefer COM Automation and LabTalk over coordinate-based GUI automation.

## Workflow

1. Confirm Origin is installed and licensed. Look for `Origin64.exe`, `Origin8.tlb`, `Interop.Origin.dll`, and registered ProgIDs such as `Origin.ApplicationSI`, `Origin.ApplicationCOMSI`, `Origin.Application`.
2. Build or reuse a CLI-Anything style Python harness with `click`, `pywin32`, `--json` output, and a default REPL.
3. Implement a backend module that isolates all Origin calls: COM connect/launch, `Execute`/LabTalk, project load/save, worksheet write/import, plotting, export, quit.
4. Keep shell-facing commands small and composable: `info`, `status`, `labtalk`, `new-project`, `open-project`, `save-project`, `import-data`, `plot`, `export-graph`, `quit`.
5. Validate with safe commands first: `info`, `status --no-launch`, then `status`, then a harmless LabTalk command, then project creation.

## Quick Scaffold

When creating a new harness, run the bundled scaffold script instead of rewriting boilerplate:

```powershell
python <skill-dir>\scripts\scaffold_origin_harness.py --output .\origin\agent-harness --install-dir "D:\Program Files\OriginLab\Origin2024"
cd .\origin\agent-harness
python -m pip install -e .
python -m cli_anything.origin --json info
```

Patch the generated code for project-specific commands after the base connection works.

## Implementation Rules

- Use `win32com.client.GetActiveObject` first when `--no-launch` is requested; use `Dispatch` only when launching/connecting is allowed.
- Prefer `Origin.ApplicationSI` first, then `Origin.ApplicationCOMSI`, then `Origin.Application`.
- Do not let `info` launch Origin. Detect installation and registry state only.
- Use `app.Execute(<LabTalk>)` for Origin-native operations that are hard to express through COM methods.
- Use forward slashes or carefully escaped paths inside LabTalk strings; Windows backslashes can be interpreted as escapes.
- Put global CLI options before the subcommand: `python -m cli_anything.origin --json info`, not `info --json`.
- For machine-readable failures, output pure JSON and exit with code 1; avoid Click's extra `Aborted!` text in `--json` mode.
- Do not assume `cli-anything-origin.exe` is on `PATH`; also support `python -m cli_anything.origin`.

## Data/Plot Pattern

For scientific data workflows:

- Convert source data to an Origin-friendly CSV or write a 2D array with `PutWorksheet`.
- Create a new project and worksheet.
- Assign column long names and designations when practical.
- Use LabTalk `plotxy` to create graphs from worksheet ranges.
- Save `.opju` as the authoritative artifact; figure export can be a second step because Origin export may be path-sensitive.

Read `references/origin-com-labtalk.md` when LabTalk syntax, COM method fallbacks, or export/path behavior matters.

## Validation Checklist

- `python -m cli_anything.origin --json info` reports the expected install path.
- `python -m cli_anything.origin --json status --no-launch` fails cleanly when Origin is closed.
- `python -m cli_anything.origin --json status` connects with a ProgID.
- `python -m cli_anything.origin --json labtalk "type -a \"connected\";"` returns success.
- `new-project` and `save-project <path.opju>` create a valid Origin project.
- Unit tests mock COM and do not require launching Origin.
