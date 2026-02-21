# CLAUDE.md — sf-quality workspace root

- This is the workspace root for the sf-quality multi-repo system
- This repo contains ONLY workspace-level files: README.md, WORKSPACE-STRUCTURE.md, sf-quality.code-workspace, Setup.ps1, .gitignore, and the Reference_Architecture/ folder
- Reference_Architecture/ is the single source of truth for all reference architecture specs, pattern mapping, and the execution plan — do NOT copy these into child repos; instead distill relevant patterns into phase CONTEXT files
- NEVER modify, create, or delete files inside sf-quality-db/, sf-quality-api/, or sf-quality-app/ from this context — those are independent repos with their own governance
- If a task requires changes to a child repo, stop and tell the user to switch to that repo's context
- When updating README.md or WORKSPACE-STRUCTURE.md, ensure repo status tables and contract descriptions stay consistent with the current state of the child repos
- The Setup.ps1 script references GitHub URLs under Chrisdoubleu/ — update if the org or repo names change
