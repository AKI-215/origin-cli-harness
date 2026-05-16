# Origin COM and LabTalk Notes

## COM Surface

Common COM ProgIDs:

- `Origin.ApplicationSI`
- `Origin.ApplicationCOMSI`
- `Origin.Application`

Useful methods observed on Origin 2024:

- `GetActiveObject` / `Dispatch` from `win32com.client`
- `NewProject`, `Load`, `Save`
- `CreatePage`, `PutWorksheet`, `GetWorksheet`
- `Execute` for LabTalk
- `Exit`

Prefer a backend wrapper so CLI commands never directly manipulate COM.

## Safe Detection

Do not call `EnsureDispatch` or `Dispatch` in an `info` command because it can launch Origin. Use filesystem checks and registry checks such as `HKCR\<ProgID>\CLSID`.

## LabTalk Patterns

Create a multi-Y line plot from worksheet columns:

```text
plotxy iy:=[BookName]Sheet1!(1,2:5) plot:=200 ogl:=[<new template:=line name:=XRD_Stacked>];
```

Import ASCII/CSV:

```text
impASC fname:="C:/path/to/data.csv";
```

Export active graph:

```text
expGraph type:=png filename:="C:/path/to/figure.png";
```

Windows backslashes can behave badly inside LabTalk strings. Prefer `C:/path/file.png` for LabTalk commands, or double-escape backslashes.

## Practical CLI Shape

Recommended commands:

- `info`: detect install path, executable, registered ProgIDs, pywin32
- `status`: connect to running Origin or launch it
- `labtalk COMMAND`: execute raw LabTalk
- `new-project`
- `open-project PATH`
- `save-project [PATH]`
- `import-data PATH`
- `plot line|scatter|line-symbol|column`
- `export-graph PATH`
- `quit`

## Common Failure Modes

- First-run/license/update dialogs block automation.
- Origin requires an interactive desktop session for some operations.
- `expGraph` may return success but not write the file if path escaping is wrong or no graph page is active.
- Some axis/label styling LabTalk commands vary by Origin version; treat beautification as best-effort.
