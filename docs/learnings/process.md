# process (cross-cutting)

<!-- When: planning or running build-loop for a ticket. -->

- **Feedback that changes the work after VERIFY: add an AC with a `## Plan amendments` line, then `T go <TICKET> ci_red_code --note "<feedback>"`.** — it is the only REVIEW exit back to IMPLEMENT and works with green CI; the loop re-verifies and the same PR is refreshed (regenerate the proof block, push, `gh pr edit --body-file`). src: CAM-16
- **The `## Proof` block of the PR is judged by how little it shows: one line per AC, one collapsed block of ≤ 6-line excerpts.** — the first two renderings (an excerpt per AC, 60 then 10 lines) read as walls of text to the user; screenshots and videos are published to `evidence/<TICKET>` (images inline, videos as a link: GitHub strips `<video>` for repository files). src: CAM-16, CAM-19
- **A DONE ticket cannot be reopened; feedback on its open PR becomes a follow-up ticket stacked on that branch.** — DONE has no exit besides blocked / cancelled and frontmatter stage is never hand-edited; branch from the PR branch, `T init --base-sha <that HEAD>` so scope and docs checks diff only the new ticket, and open the PR with the first branch as its base. src: CAM-19
