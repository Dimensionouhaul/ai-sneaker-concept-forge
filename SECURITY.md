# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.9.x   | yes       |
| 0.8.x   | security fixes only |
| < 0.8   | no        |

## Reporting a vulnerability

Email `security@forge.local` with a description, a repro, and the affected
version. We aim to acknowledge within 72 hours. Please do not open public
issues for exploitable bugs.

In scope:
- Remote code execution via a malicious plugin entry point
- Path traversal in the concept export pipeline
- Model file parsing (ONNX / GGUF / safetensors) memory-safety issues
- Sandbox escape from the plugin worker process

Out of scope:
- The fact that plugins can read files on disk — that's by design, they're
  trusted local code. If you want to run untrusted plugins, use the
  `--sandbox` flag which runs them in a subprocess with a reduced token.
- Generated concepts looking weird. That's the model.

## Plugin trust model

Plugins are **trusted local code**. Installing a plugin is equivalent to
running a script. The host does not sign or verify plugin wheels. The
`forge-cli plugin list` command shows the resolved entry point and the
wheel hash so you can eyeball what you're about to run.

## Hardening notes

- Concept exports are written under `generated_concepts/` and never outside
  it unless the user passes an explicit absolute path.
- The HTTP client used for model pulls (`services/model_registry.py`) pins
  TLS to the forge CDN and refuses redirects to non-forge hosts.
- Model files are checksummed against a signed manifest before load.