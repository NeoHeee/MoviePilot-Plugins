"""MoviePilot V3 MagicPush 迁移的仓库级静态检查。"""

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLUGIN_IDS = {
    "MagicPushMsg": "magicpushmsg",
    "MagicPushControl": "magicpushcontrol",
}


def _class_version(source: Path, class_name: str) -> str:
    tree = ast.parse(source.read_text(encoding="utf-8"))
    plugin_class = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == class_name
    )
    assignment = next(
        node
        for node in plugin_class.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "plugin_version"
            for target in node.targets
        )
    )
    return ast.literal_eval(assignment.value)


def test_v3_index_matches_plugin_versions() -> None:
    package = json.loads((ROOT / "package.v3.json").read_text(encoding="utf-8"))

    assert set(package) == set(PLUGIN_IDS)
    for plugin_id, directory in PLUGIN_IDS.items():
        metadata = package[plugin_id]
        source = ROOT / "plugins.v3" / directory / "__init__.py"
        assert source.is_file()
        assert metadata["system_version"] == ">=3.0.0,<4"
        assert metadata["version"] == _class_version(source, plugin_id)
        assert next(iter(metadata["history"])) == f"v{metadata['version']}"


def test_v2_indexes_disable_v3_fallback() -> None:
    for filename in ("package.json", "package.v2.json"):
        package = json.loads((ROOT / filename).read_text(encoding="utf-8"))
        assert all(package[plugin_id]["v3"] is False for plugin_id in PLUGIN_IDS)


def test_v3_sources_do_not_use_migrated_legacy_imports() -> None:
    legacy_prefixes = (
        "from app.core.",
        "from app.helper.",
        "from app.log ",
        "from app.utils.",
    )
    for directory in PLUGIN_IDS.values():
        source = (ROOT / "plugins.v3" / directory / "__init__.py").read_text(
            encoding="utf-8"
        )
        assert not any(prefix in source for prefix in legacy_prefixes)
