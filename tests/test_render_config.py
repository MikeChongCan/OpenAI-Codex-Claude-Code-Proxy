import unittest

from scripts.render_config import normalized_base_url, render


TEMPLATE = """port: __CLIPROXY_PORT__
base: __AZURE_API_BASE__
key: __AZURE_API_KEY__
local: __CLIPROXY_LOCAL_TOKEN__
auth: __CLIPROXY_AUTH_DIR__
models: [__AZURE_OPUS_DEPLOYMENT__, __AZURE_SONNET_DEPLOYMENT__, __AZURE_HAIKU_DEPLOYMENT__]
"""


class RenderConfigTests(unittest.TestCase):
    def test_renders_and_yaml_quotes_untrusted_values(self):
        result = render(
            TEMPLATE,
            {
                "AZURE_API_BASE": "https://example.test/openai/v1/",
                "AZURE_API_KEY": "key: with # yaml",
                "CLIPROXY_LOCAL_TOKEN": "local-secret",
                "AZURE_DEFAULT_DEPLOYMENT": "deployment",
                "CLIPROXY_PORT": "9000",
            },
        )
        self.assertIn('key: "key: with # yaml"', result)
        self.assertIn("port: 9000", result)
        self.assertNotIn("__", result)

    def test_requires_secrets(self):
        with self.assertRaisesRegex(ValueError, "AZURE_API_KEY"):
            render(TEMPLATE, {"AZURE_API_BASE": "https://example.test/openai/v1"})

    def test_rejects_legacy_or_wrong_endpoint(self):
        with self.assertRaisesRegex(ValueError, "/openai/v1"):
            normalized_base_url("https://example.test/openai/deployments/foo")


if __name__ == "__main__":
    unittest.main()
