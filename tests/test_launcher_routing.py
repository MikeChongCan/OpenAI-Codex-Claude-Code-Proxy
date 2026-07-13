import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LauncherRoutingTests(unittest.TestCase):
    def run_launcher(self, launcher_name="claudex", extra_env=None):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            launcher = temp_root / launcher_name
            shutil.copy2(ROOT / launcher_name, launcher)

            ensure_proxy = temp_root / "ensure-cliproxy.sh"
            ensure_proxy.write_text("#!/usr/bin/env bash\nexit 0\n")
            ensure_proxy.chmod(0o755)

            fake_bin = temp_root / "bin"
            fake_bin.mkdir()
            fake_claude = fake_bin / "claude"
            fake_claude.write_text(
                """#!/usr/bin/env python3
import json
import os
import sys

keys = (
    "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL",
    "CLAUDE_CODE_SUBAGENT_MODEL",
)
print(json.dumps({
    "args": sys.argv[1:],
    "env": {key: os.environ[key] for key in keys if key in os.environ},
}))
"""
            )
            fake_claude.chmod(0o755)

            env = os.environ.copy()
            env.update(
                {
                    "PATH": f"{fake_bin}{os.pathsep}{env['PATH']}",
                    "CLIPROXY_LOCAL_TOKEN": "test-token",
                }
            )
            if extra_env:
                env.update(extra_env)

            result = subprocess.run(
                [launcher, "prompt"],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )
            return json.loads(result.stdout)

    def test_azure_launcher_maps_model_families(self):
        launcher = (ROOT / "claudex").read_text()

        self.assertIn(
            'ANTHROPIC_DEFAULT_OPUS_MODEL="azure-gpt-5.6-sol"', launcher
        )
        self.assertIn(
            'ANTHROPIC_DEFAULT_SONNET_MODEL="azure-gpt-5.6-terra"', launcher
        )
        self.assertIn(
            'ANTHROPIC_DEFAULT_HAIKU_MODEL="azure-gpt-5.6-luna"', launcher
        )
        self.assertIn(
            '--model "${CLAUDEX_MODEL:-azure-gpt-5.6-sol}"', launcher
        )

    def test_azure_launcher_preserves_per_subagent_model_selection(self):
        result = self.run_launcher(
            extra_env={"CLAUDE_CODE_SUBAGENT_MODEL": "stale-parent-value"}
        )

        self.assertEqual(result["args"][:2], ["--model", "azure-gpt-5.6-sol"])
        self.assertEqual(result["args"][2], "--append-system-prompt")
        self.assertEqual(result["args"][-1], "prompt")
        self.assertEqual(
            result["env"],
            {
                "ANTHROPIC_DEFAULT_OPUS_MODEL": "azure-gpt-5.6-sol",
                "ANTHROPIC_DEFAULT_SONNET_MODEL": "azure-gpt-5.6-terra",
                "ANTHROPIC_DEFAULT_HAIKU_MODEL": "azure-gpt-5.6-luna",
            },
        )

    def test_azure_launcher_can_force_one_subagent_tier(self):
        result = self.run_launcher(extra_env={"CLAUDEX_SUBAGENT_MODEL": "haiku"})

        self.assertEqual(result["env"]["CLAUDE_CODE_SUBAGENT_MODEL"], "haiku")

    def test_azure_launcher_appends_delegation_policy(self):
        result = self.run_launcher()
        prompt_index = result["args"].index("--append-system-prompt") + 1
        system_prompt = result["args"][prompt_index]

        self.assertIn("Sol by default", system_prompt)
        self.assertIn("model `sonnet` (Terra)", system_prompt)
        self.assertIn("model `haiku` (Luna)", system_prompt)
        self.assertIn("Do not invoke or load the `claude-api` skill", system_prompt)

    def test_oauth_launcher_routes_subagent_model_families(self):
        result = self.run_launcher(
            "claudex-oai",
            {"CLAUDE_CODE_SUBAGENT_MODEL": "stale-parent-value"},
        )

        self.assertEqual(result["args"][:2], ["--model", "gpt-5.6-sol"])
        self.assertEqual(
            result["env"],
            {
                "ANTHROPIC_DEFAULT_OPUS_MODEL": "gpt-5.6-sol",
                "ANTHROPIC_DEFAULT_SONNET_MODEL": "gpt-5.6-terra",
                "ANTHROPIC_DEFAULT_HAIKU_MODEL": "gpt-5.6-luna",
            },
        )

    def test_oauth_launcher_appends_delegation_policy(self):
        result = self.run_launcher("claudex-oai")
        prompt_index = result["args"].index("--append-system-prompt") + 1
        system_prompt = result["args"][prompt_index]

        self.assertIn("model `sonnet` (Terra)", system_prompt)
        self.assertIn("model `haiku` (Luna)", system_prompt)
        self.assertIn("Do not invoke or load the `claude-api` skill", system_prompt)


if __name__ == "__main__":
    unittest.main()
