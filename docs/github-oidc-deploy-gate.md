# GitHub OIDC deploy gate

Production Railway deploys from `Garrettc123/APEX-AI-ENGINE` must pass `github-oidc-verify` on Supabase project `sqnckbvdqofoirgtwwxt` before `railway up`.

## Function contract

- URL: `https://sqnckbvdqofoirgtwwxt.supabase.co/functions/v1/github-oidc-verify`
- JWT gate: disabled
- Caller gate: `X-Internal-Auth`
- Issuer: `https://token.actions.githubusercontent.com`
- Audience: `garcar-supabase-production`
- Repository: `Garrettc123/APEX-AI-ENGINE`
- Ref: `refs/heads/main`
- Environment: `production`
- Workflow: `.github/workflows/deploy.yml@refs/heads/main`

Expected success body (allowlisted fields only):

```json
{
  "verified": true,
  "repository": "Garrettc123/APEX-AI-ENGINE",
  "ref": "refs/heads/main",
  "environment": "production"
}
```

## Repo setup before the first protected deploy

1. Create GitHub Environment `production` on this repository and protect it.
2. Put these secrets on that environment (not in the workflow file):
   - `GARCAR_INTERNAL_AUTH` — same value the Edge Function expects in `X-Internal-Auth`
   - `SUPABASE_PUBLISHABLE_KEY` — gateway `apikey` only; never a service-role key
   - `RAILWAY_TOKEN`
3. Merge this change to `main`. The verifier pins `workflow_ref` to `.github/workflows/deploy.yml@refs/heads/main`, so a branch run will fail by design.
4. Dispatch the workflow from `main` / Environment `production` and confirm the verify step prints `verified: true` before Railway starts.

## Failure paths the function should keep

- Missing `X-Internal-Auth` → `401 unauthorized`
- Wrong internal secret → `401 unauthorized`
- No JSON token → `400 invalid_token`
- Wrong audience → `401 invalid_or_expired_token`
- Non-`main` ref → `403 ref_mismatch`
- Outside `production` → `403 environment_mismatch`
- Different workflow file → `403 workflow_ref_mismatch`

Do not remove `public.verify_github_oidc(text)` or the `http` extension until no callers remain and a dependency sweep is done.
