from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any


class FileCache:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path_for_key(self, namespace: str, key: str) -> Path:
        digest = sha256(key.encode("utf-8")).hexdigest()
        namespace_dir = self.root / namespace
        namespace_dir.mkdir(parents=True, exist_ok=True)
        return namespace_dir / f"{digest}.json"

    def get(self, namespace: str, key: str) -> Any | None:
        path = self._path_for_key(namespace, key)
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def set(self, namespace: str, key: str, value: Any) -> Path:
        path = self._path_for_key(namespace, key)
        path.write_text(json.dumps(value, indent=2, sort_keys=True))
        return path
