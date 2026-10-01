# Security

Generated programs are untrusted input. The local executor uses isolated subprocesses, a restricted environment, timeouts, output-size limits, and selected OS resource limits. These controls are defense-in-depth and are not a complete security boundary.

For untrusted candidates, use a container or VM with:
- no network access;
- a restricted filesystem;
- non-privileged execution;
- CPU and memory quotas;
- a short wall-clock timeout;
- explicit output limits.

The historical repository previously contained provider API keys in source code. The active VEPO-LLM tree removes those literals and uses environment-based configuration. Because old keys may still exist in Git history, the repository owner should revoke/rotate those credentials and separately consider a history rewrite if complete secret removal is required.

Never commit secrets. Keep .env ignored.
