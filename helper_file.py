import shutil
import sys
import tomllib
from pathlib import Path


class FileHelper:

    @staticmethod
    def _get_app_base_dir() -> Path:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS)
        return Path(__file__).resolve().parent

    @staticmethod
    def get_version_from_pyproject() -> str:
        pyproject_path = FileHelper._get_app_base_dir() / "pyproject.toml"
        try:
            data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
            return data.get("project", {}).get("version", "unknown")
        except FileNotFoundError:
            return "unknown"
        except (OSError, tomllib.TOMLDecodeError):
            return "unknown"

    @staticmethod
    def get_resource_path(relative_path: str) -> Path:
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).parent.absolute()
        return base_path / relative_path

    @staticmethod
    def validate_cli_tools(tools) -> dict:
        results = {}
        for tool in tools:
            tool_path = shutil.which(tool)
            results[tool] = tool_path is not None
        return results