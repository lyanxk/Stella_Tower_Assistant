from __future__ import annotations

from ..config.settings import RESOURCE_DIR, TEMPLATES


def list_templates() -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for key, filename in sorted(TEMPLATES.items()):
        path = RESOURCE_DIR / filename
        items.append(
            {
                "key": key,
                "filename": filename,
                "path": str(path),
                "exists": path.is_file(),
            }
        )
    return items
