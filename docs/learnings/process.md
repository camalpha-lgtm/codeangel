# process (cross-cutting)

<!-- When: planning or running build-loop for a ticket. -->

- **Feedback that changes the work after VERIFY: add an AC with a `## Plan amendments` line, then `T go <TICKET> ci_red_code --note "<feedback>"`.** — it is the only REVIEW exit back to IMPLEMENT and works with green CI; the loop re-verifies and the same PR is refreshed (regenerate the proof block, push, `gh pr edit --body-file`). src: CAM-16
- **The `## Proof` block of the PR is judged by how little it shows: one line per AC, one collapsed block of ≤ 6-line excerpts.** — the first two renderings (an excerpt per AC, 60 then 10 lines) read as walls of text to the user; screenshots cannot be embedded without committing a file. src: CAM-16
