# Origin CLI Harness Skill

这是一个用于把 OriginLab Origin 接入命令行/Agent 工作流的 Codex Skill。核心目标是：用 CLI-Anything 风格生成可安装的 `cli-anything-origin` 命令，让 Codex、Claude Code、OpenCode、PowerShell 或其他工具可以通过命令行控制 Origin。

重点是 **CLI 接入方式**，不是 GUI 坐标点击。优先使用 Origin 原生的 COM Automation 和 LabTalk。

## 适用版本

已实测环境：

- OriginLab Origin 2024，安装路径为 `D:\Program Files\OriginLab\Origin2024`
- 已注册 Origin COM Automation 的 Windows 桌面会话
- Python 3.12
- GitHub CLI 2.92.0，用于发布本仓库

预期兼容环境：

- 暴露 `Origin.ApplicationSI`、`Origin.ApplicationCOMSI` 或 `Origin.Application` 的 OriginLab Origin 版本
- Windows + `pywin32`
- Python 3.9+

注意：Origin 必须已经授权并且能在当前桌面会话中正常启动。首次运行弹窗、许可证提示、更新提示等，需要先手动处理，再交给 CLI 自动化。

## 相关库地址

- 本 Skill 仓库：<https://github.com/AKI-215/origin-cli-harness>
- CLI-Anything 上游项目：<https://github.com/HKUDS/CLI-Anything>
- CLI-Anything OpenCode 实验性支持说明：<https://github.com/HKUDS/CLI-Anything/blob/main/README_CN.md#-opencode-%E5%AE%9E%E9%AA%8C%E6%80%A7%E6%94%AF%E6%8C%81>

## 提供内容

- `SKILL.md`：Codex skill 触发说明和工作流。
- `scripts/scaffold_origin_harness.py`：一键生成 Origin CLI harness 骨架。
- `references/origin-com-labtalk.md`：COM ProgID、LabTalk 语法、路径转义和常见坑点。
- `agents/openai.yaml`：界面元信息。

## 目录结构

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

## 安装为 Codex Skill

把本仓库复制或克隆到 Codex skills 目录：

```powershell
git clone https://github.com/AKI-215/origin-cli-harness.git "$env:USERPROFILE\.codex\skills\origin-cli-harness"
```

然后重启 Codex，让它重新发现 skill。

## 生成 Origin CLI Harness

```powershell
python "$env:USERPROFILE\.codex\skills\origin-cli-harness\scripts\scaffold_origin_harness.py" `
  --output ".\origin\agent-harness" `
  --install-dir "D:\Program Files\OriginLab\Origin2024"

cd .\origin\agent-harness
python -m pip install -e .
python -m cli_anything.origin --json info
```

如果能识别 Origin 安装路径和 COM ProgID，就可以继续测试：

```powershell
python -m cli_anything.origin --json status
python -m cli_anything.origin --json labtalk "type -a `"connected`";"
python -m cli_anything.origin --json new-project
python -m cli_anything.origin --json save-project ".\origin-test.opju"
```

## 设计原则

- 优先使用 COM Automation：`Origin.ApplicationSI`、`Origin.ApplicationCOMSI`、`Origin.Application`。
- 通过 `app.Execute(...)` 执行 LabTalk，完成 Origin 原生操作。
- `info` 命令只能检测环境，不能启动 Origin。
- `--json` 模式必须输出纯 JSON，方便机器读取。
- 推荐支持 `python -m cli_anything.origin`，因为 Windows 上 Python scripts 目录经常不在 `PATH`。
- `.opju` 是最可靠的成果文件；图片导出可能受 Origin 当前图页和路径转义影响。

## 环境要求

- Windows
- 已授权且可启动的 OriginLab Origin
- Python 3.9+
- `click`
- `pywin32`

生成的 harness 会在 `setup.py` 里声明 `click` 和 `pywin32` 依赖。

## 验证

验证 skill 结构：

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .\origin-cli-harness
```

验证生成的 harness：

```powershell
python -m cli_anything.origin --json info
python -m cli_anything.origin --json status --no-launch
```

如果 Origin 没有运行，`status --no-launch` 应该以纯 JSON 形式干净失败。
