# Phase 0: Hooks Infrastructure

**Branch:** `refactor/0-hooks-infrastructure`

**New files to create (copy from `assets/` directory):**

1. Copy `assets/pre-commit-config.yaml` to `.pre-commit-config.yaml` (project root)
2. Copy `assets/ruff.toml` to `.ruff.toml` (project root)
3. Copy `assets/ci-workflow.yml` to `.github/workflows/ci.yml`

**Commits:**
1. `ci(hooks): add pre-commit framework with Ruff and conventional commits`
2. `ci(github): add CI workflow for lint and C compilation`

**Verification:**
Run `bash .cursor/skills/jaccuracyscope-refactor/scripts/verify-phase.sh`
