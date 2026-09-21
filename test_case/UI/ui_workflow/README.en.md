# API / UI Workflow Scripts

This directory stores Python workflow scripts callable from YAML. They allow QA to invoke backend APIs for test preconditions or perform operations that are difficult to achieve via UI.

## Invocation Methods

### Method 1: Dedicated Action (Recommended)

Use the dedicated action registered in `actions/base.py`. It **automatically uses the Playwright browser's authentication state** (cookie + JS-generated auth header) — no manual token configuration needed:

```yaml
test_step:
    # Duplicate Post (two steps: verify + execute)
    duplicate_post: { post_id: "xxx", capture_key: "cloned_post_id" }

    # Subsequent steps can reference the return value via ${cloned_post_id}
    # (variable substitution in base.py coming soon)
```

**Why not subprocess + requests?**

Katana's backend generates JWT tokens dynamically via JS on every request. They cannot be read statically from cookies/localStorage. The dedicated action uses Playwright's `page.request` API, which automatically shares the browser page's authentication state.

### Method 2: Generic Wrapper (Deprecated)

```yaml
test_step:
    run_workflow_script: { script: "xxx.py", args: { key: "value" } }
```

> The subprocess + requests approach no longer supports dynamic token fetching and is not recommended for new scripts.

## Directory Structure

```
api/
└── ui_workflow/
    ├── README.md / README.en.md  # Documentation (bilingual)
    ├── __init__.py              # Package init (do not delete)
    ├── api_token.txt             # Token file (gitignored, do not commit)
    └── *.py                     # Workflow scripts
```

## Adding a New Dedicated Action

1. Define the function in `actions/base.py`: `def xxx_action(page: Page, v: dict)`
2. Import and register it in `actions/__init__.py` under the `ACTIONS` dictionary

## Available Actions / Scripts

| Action / Script | Purpose | Parameters |
|---------------|---------|------------|
| `duplicate_post` **(action)** | Duplicates a Post (verify + execute) | `post_id` (required), `capture_key` (optional, defaults to `cloned_post_id`) |
| `duplicate_post.py` **(deprecated)** | Old script — use the action above instead | — |

## Token Configuration (Legacy Scripts Only)

New scripts do not need manual token configuration.

Legacy scripts require an auth token (two options, by priority):

1. **Playwright browser** (automatic): Actions use `page.request`, automatically carrying browser auth
2. **Local file** (fallback): `api_token.txt` (do not commit — it's in `.gitignore`)

## Token Pitfalls

> Katana's frontend uses Passport.js to serialize JWT into a cookie (`release_katana_web_auth_token`). The frontend JS deserializes it and dynamically injects the `Authorization: Bearer eyJ...` header into API requests.
>
> Therefore:
> - The `release_katana_web_auth_token` cookie value is a **serialized object**, not a JWT — using it directly results in 401
> - The real JWT exists only in the **browser's runtime JS memory** and cannot be read statically
> - **Solution**: Use Playwright's `page.request` API to intercept requests, automatically carrying the JS-dynamic header
