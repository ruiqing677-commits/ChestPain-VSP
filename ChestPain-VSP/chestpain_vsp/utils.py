import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def load_env_file(path: str | Path = ".env") -> None:
    """Load simple KEY=VALUE environment variables if a local .env exists."""
    env_path = Path(path)
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :]
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, data: Any) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def compact_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return "; ".join(compact_text(item) for item in value if compact_text(item))
    if isinstance(value, dict):
        return "; ".join(f"{key}: {compact_text(item)}" for key, item in value.items() if compact_text(item))
    return str(value).strip()


def dedupe_keep_order(items: Iterable[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for item in items:
        normalized = compact_text(item)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def case_id(case_data: Dict[str, Any], fallback: str = "case") -> str:
    return str(case_data.get("case_id") or case_data.get("caseId") or fallback)


def list_json_files(path: str | Path) -> List[Path]:
    root = Path(path)
    if root.is_file() and root.suffix.lower() == ".json":
        return [root]
    return sorted(root.glob("*.json"))


def get_openai_client(api_key: Optional[str] = None, base_url: Optional[str] = None):
    """Create an OpenAI-compatible client.

    The repository intentionally supports OpenAI-compatible APIs so users can
    run OpenAI, Azure OpenAI, Gemini OpenAI-compatible endpoints, DashScope,
    vLLM, or other compatible backends without code changes.
    """
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Install dependencies first: pip install -r requirements.txt") from exc

    load_env_file()
    resolved_key = api_key or os.environ.get("CHESTPAIN_VSP_API_KEY") or os.environ.get("OPENAI_API_KEY")
    resolved_base_url = base_url or os.environ.get("CHESTPAIN_VSP_BASE_URL")
    if not resolved_key:
        raise RuntimeError("CHESTPAIN_VSP_API_KEY or OPENAI_API_KEY is required.")
    kwargs = {"api_key": resolved_key}
    if resolved_base_url:
        kwargs["base_url"] = resolved_base_url
    return OpenAI(**kwargs)


def normalize_label(text: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", text.strip().lower()).strip("_")
