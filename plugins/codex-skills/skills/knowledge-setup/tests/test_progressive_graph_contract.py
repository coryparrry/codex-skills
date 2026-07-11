import json
import unittest
from pathlib import Path


REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "skills.sh.json").is_file()
)
SOURCE_SKILL = REPO_ROOT / "skills" / "knowledge-setup"
MIRROR_SKILL = REPO_ROOT / "plugins" / "codex-skills" / "skills" / "knowledge-setup"


class ProgressiveGraphContractTests(unittest.TestCase):
    def test_source_and_mirror_match(self) -> None:
        for relative_path in (
            "SKILL.md",
            "templates/agents-template.md",
            "templates/graph.json",
            "tests/test_progressive_graph_contract.py",
        ):
            self.assertEqual(
                (SOURCE_SKILL / relative_path).read_text(),
                (MIRROR_SKILL / relative_path).read_text(),
                relative_path,
            )

    def test_agents_template_queries_routes_before_selected_nodes(self) -> None:
        text = (SOURCE_SKILL / "templates" / "agents-template.md").read_text()

        route_catalog = text.index(".routes | to_entries")
        selected_route = text.index(".routes[$route]")
        full_graph_boundary = text.index("Read the full graph only when")

        self.assertLess(route_catalog, selected_route)
        self.assertLess(selected_route, full_graph_boundary)
        self.assertNotIn("2. Read `.repo/graph.json`.", text)

    def test_graph_template_declares_progressive_read_policy(self) -> None:
        graph = json.loads((SOURCE_SKILL / "templates" / "graph.json").read_text())
        read_policy = graph["agent_contract"]["read_policy"]

        self.assertEqual(read_policy["mode"], "progressive")
        self.assertIn("route catalog", read_policy["first"])
        self.assertIn("selected route", read_policy["then"])
        self.assertTrue(read_policy["full_graph_only_when"])

    def test_skill_requires_routable_route_metadata(self) -> None:
        text = (SOURCE_SKILL / "SKILL.md").read_text()

        self.assertIn("`summary`", text)
        self.assertIn("`match`", text)
        self.assertIn("progressive-read", text)


if __name__ == "__main__":
    unittest.main()
