# code standards

<!-- When: writing or reviewing code in this repo. -->

- Prefer object-oriented design: small types with one responsibility, behaviour on the type that owns the data.
- Do not add single-line comments, multi-line comments, or docstrings. Names and tests carry the meaning.
- Keep modules, types, and functions small enough to read in one pass.
- Make gates deterministic: the same command, on the same tree, returns the same result.
- Record how this repo's gates enforce these rules in the root `AGENTS.md` `## Done` section.
