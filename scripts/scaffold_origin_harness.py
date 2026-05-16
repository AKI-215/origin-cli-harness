from __future__ import annotations

import argparse
from pathlib import Path
from textwrap import dedent


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(text).lstrip(), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a CLI-Anything Origin harness.")
    parser.add_argument("--output", required=True, help="Output agent-harness directory.")
    parser.add_argument("--install-dir", default=r"D:\Program Files\OriginLab\Origin2024", help="Origin install directory.")
    args = parser.parse_args()

    root = Path(args.output).resolve()
    package = root / "cli_anything" / "origin"

    write(
        root / "setup.py",
        """
        from setuptools import find_namespace_packages, setup

        setup(
            name="cli-anything-origin",
            version="0.1.0",
            packages=find_namespace_packages(include=["cli_anything.*"]),
            install_requires=["click>=8.0", "pywin32>=306; platform_system == 'Windows'"],
            entry_points={"console_scripts": ["cli-anything-origin=cli_anything.origin.origin_cli:main"]},
            python_requires=">=3.9",
        )
        """,
    )
    write(package / "__init__.py", '"""Origin CLI harness."""\n')
    write(package / "__main__.py", "from .origin_cli import main\n\nif __name__ == '__main__':\n    main()\n")
    write(package / "utils" / "__init__.py", "")
    write(package / "utils" / "origin_backend.py", backend_source(args.install_dir))
    write(package / "origin_cli.py", cli_source())
    write(
        root / "ORIGIN.md",
        f"""
        # CLI-Anything Origin Harness

        Origin install directory: `{args.install_dir}`

        This harness controls Origin through COM Automation and LabTalk.
        """,
    )
    print(f"Created Origin harness at {root}")


def backend_source(install_dir: str) -> str:
    return f'''
    from __future__ import annotations

    import os
    import winreg
    from pathlib import Path
    from typing import Any

    DEFAULT_INSTALL_DIR = Path(r"{install_dir}")
    PROG_IDS = ("Origin.ApplicationSI", "Origin.ApplicationCOMSI", "Origin.Application")


    class OriginBackendError(RuntimeError):
        pass


    def detect_origin(install_dir: str | None = None) -> dict[str, Any]:
        root = Path(install_dir) if install_dir else DEFAULT_INSTALL_DIR
        exe = root / "Origin64.exe"
        registered = [progid for progid in PROG_IDS if _progid_available(progid)]
        return {{
            "install_dir": str(root),
            "executable": str(exe) if exe.exists() else None,
            "executable_exists": exe.exists(),
            "registered_progids": registered,
            "pywin32_available": _has_pywin32(),
        }}


    class OriginBackend:
        def __init__(self, install_dir: str | None = None, visible: bool = True):
            self.install_dir = Path(install_dir) if install_dir else DEFAULT_INSTALL_DIR
            self.visible = visible
            self.app = None
            self.progid = None

        def connect(self, launch: bool = True) -> dict[str, Any]:
            import win32com.client

            errors = []
            for progid in PROG_IDS:
                try:
                    self.app = win32com.client.GetActiveObject(progid)
                    self.progid = progid
                    self._set_visible()
                    return self.status()
                except Exception as exc:
                    errors.append(f"{{progid}} active lookup failed: {{exc}}")
            if not launch:
                raise OriginBackendError("No running Origin COM server found.")
            for progid in PROG_IDS:
                try:
                    self.app = win32com.client.Dispatch(progid)
                    self.progid = progid
                    self._set_visible()
                    return self.status()
                except Exception as exc:
                    errors.append(f"{{progid}} dispatch failed: {{exc}}")
            raise OriginBackendError("Unable to connect to Origin. " + " | ".join(errors[-3:]))

        def status(self) -> dict[str, Any]:
            app = self._require_app()
            return {{
                "connected": True,
                "progid": self.progid,
                "visible": getattr(app, "Visible", None),
                "caption": getattr(app, "Caption", None) if hasattr(app, "Caption") else None,
            }}

        def execute_labtalk(self, command: str) -> dict[str, Any]:
            app = self._require_app()
            result = app.Execute(command)
            return {{"command": command, "method": "Execute", "result": bool(result)}}

        def new_project(self) -> dict[str, Any]:
            result = self._require_app().NewProject()
            return {{"created": bool(result), "method": "NewProject"}}

        def save_project(self, path: str | None = None) -> dict[str, Any]:
            app = self._require_app()
            if path:
                target = Path(path).resolve()
                target.parent.mkdir(parents=True, exist_ok=True)
                result = app.Save(str(target))
                return {{"saved": str(target), "result": bool(result)}}
            result = app.Save()
            return {{"saved": True, "result": bool(result)}}

        def quit(self) -> dict[str, Any]:
            result = self._require_app().Exit()
            self.app = None
            return {{"closed": True, "result": bool(result)}}

        def _require_app(self):
            if self.app is None:
                self.connect()
            return self.app

        def _set_visible(self) -> None:
            try:
                self.app.Visible = int(self.visible)
            except Exception:
                pass


    def _has_pywin32() -> bool:
        try:
            import win32com.client  # noqa: F401
            return True
        except Exception:
            return False


    def _progid_available(progid: str) -> bool:
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, rf"{{progid}}\\CLSID") as key:
                value, _ = winreg.QueryValueEx(key, "")
                return bool(value)
        except OSError:
            return False
    '''


def cli_source() -> str:
    return '''
    from __future__ import annotations

    import json
    from typing import Any

    import click

    from .utils.origin_backend import DEFAULT_INSTALL_DIR, OriginBackend, OriginBackendError, detect_origin


    class Context:
        def __init__(self, json_output: bool, install_dir: str, visible: bool):
            self.json_output = json_output
            self.backend = OriginBackend(install_dir=install_dir, visible=visible)


    @click.group(invoke_without_command=True)
    @click.option("--json", "json_output", is_flag=True)
    @click.option("--install-dir", default=str(DEFAULT_INSTALL_DIR), show_default=True)
    @click.option("--hidden/--visible", default=False)
    @click.pass_context
    def main(ctx: click.Context, json_output: bool, install_dir: str, hidden: bool) -> None:
        ctx.obj = Context(json_output, install_dir, not hidden)
        if ctx.invoked_subcommand is None:
            click.echo("cli-anything-origin REPL placeholder. Use --help for commands.")


    @main.command()
    @click.pass_obj
    def info(ctx: Context) -> None:
        emit(detect_origin(str(ctx.backend.install_dir)), ctx.json_output)


    @main.command()
    @click.option("--no-launch", is_flag=True)
    @click.pass_obj
    def status(ctx: Context, no_launch: bool) -> None:
        run(ctx, lambda: ctx.backend.connect(launch=not no_launch))


    @main.command("labtalk")
    @click.argument("command")
    @click.pass_obj
    def labtalk(ctx: Context, command: str) -> None:
        run(ctx, lambda: ctx.backend.execute_labtalk(command))


    @main.command("new-project")
    @click.pass_obj
    def new_project(ctx: Context) -> None:
        run(ctx, ctx.backend.new_project)


    @main.command("save-project")
    @click.argument("path", required=False)
    @click.pass_obj
    def save_project(ctx: Context, path: str | None) -> None:
        run(ctx, lambda: ctx.backend.save_project(path))


    @main.command()
    @click.pass_obj
    def quit(ctx: Context) -> None:
        run(ctx, ctx.backend.quit)


    def run(ctx: Context, action: Any) -> None:
        try:
            payload = action()
            payload = {"ok": True, **payload}
            emit(payload, ctx.json_output)
        except OriginBackendError as exc:
            emit({"ok": False, "error": str(exc)}, ctx.json_output)
            if ctx.json_output:
                raise click.exceptions.Exit(1) from exc
            raise click.Abort() from exc


    def emit(payload: Any, as_json: bool) -> None:
        if as_json:
            click.echo(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            click.echo(payload)
    '''


if __name__ == "__main__":
    main()
