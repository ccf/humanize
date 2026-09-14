Traceback (most recent call last):
  File "/Users/ccf/.local/bin/hermes", line 10, in <module>
    sys.exit(main())
             ^^^^^^
  File "/Users/ccf/.hermes/hermes-agent/hermes_cli/main.py", line 10068, in main
    sys.exit(run_oneshot(
             ^^^^^^^^^^^^
  File "/Users/ccf/.hermes/hermes-agent/hermes_cli/oneshot.py", line 80, in run_oneshot
    response = _run_agent(prompt, model=model, provider=provider)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/ccf/.hermes/hermes-agent/hermes_cli/oneshot.py", line 149, in _run_agent
    runtime = resolve_runtime_provider(
              ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/ccf/.hermes/hermes-agent/hermes_cli/runtime_provider.py", line 1008, in resolve_runtime_provider
    creds = resolve_codex_runtime_credentials()
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/ccf/.hermes/hermes-agent/hermes_cli/auth.py", line 2376, in resolve_codex_runtime_credentials
    tokens = _refresh_codex_auth_tokens(tokens, refresh_timeout_seconds)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/ccf/.hermes/hermes-agent/hermes_cli/auth.py", line 2302, in _refresh_codex_auth_tokens
    refreshed = refresh_codex_oauth_pure(
                ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/ccf/.hermes/hermes-agent/hermes_cli/auth.py", line 2257, in refresh_codex_oauth_pure
    raise AuthError(
hermes_cli.auth.AuthError: Codex token refresh failed: Could not validate your refresh token. Please try signing in again.
