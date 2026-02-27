# CLAUDE.md — sf-quality workspace root

- This is the workspace root for the sf-quality multi-repo system
- This repo contains ONLY workspace-level files: README.md, WORKSPACE-STRUCTURE.md, sf-quality.code-workspace, Setup.ps1, .gitignore, and the Reference_Architecture/ folder
- Reference_Architecture/ is the single source of truth for all reference architecture specs, pattern mapping, and the execution plan — do NOT copy these into child repos; instead distill relevant patterns into phase CONTEXT files
- NEVER modify SOURCE CODE files (src/, database/, scripts/, config files, package.json, *.csproj, etc.) inside sf-quality-db/, sf-quality-api/, or sf-quality-app/ from this context — those are independent repos with their own code governance (CLAUDE.md, AGENTS.md)
- The workspace MAY write planning bridge files to child repos: `.planning/phases/*/CONTEXT.md` only — these are cross-repo coordination artifacts that distill phase requirements, adjudication decisions, and success criteria from the workspace ROADMAP.md into each child repo's planning directory
- If a task requires SOURCE CODE changes to a child repo, stop and tell the user to switch to that repo's context — the child repo's CLAUDE.md governs all code execution
- When updating README.md or WORKSPACE-STRUCTURE.md, ensure repo status tables and contract descriptions stay consistent with the current state of the child repos
- The Setup.ps1 script references GitHub URLs under Chrisdoubleu/ — update if the org or repo names change
