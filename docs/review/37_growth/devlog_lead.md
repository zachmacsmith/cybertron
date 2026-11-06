# Dev log: lead session (coordination of review 37, bench 36 follow-ups)

Branch `wp/lead` from `bench/first-batch`. Format as in README "Development logs and check-ins".

## 2026-10-22 (UTC)

**Doing.** Coordinating the review-37 packages. 37.1 (demography), 37.2 (economy) and 37.4 (environment) run in separate
sessions Zach drives; 37.3 (institutions acting on each other) runs as a sub-agent of this session in worktree
`/home/user/wt-inst-cross`, branch `wp/inst-cross`.

**Decided.**
- The dev-log convention is on `bench/first-batch` (d9acf18) so every package branch inherits it; my own work goes here.
- Next code change in this branch: under `context.aim_framing`, restore the sentence "Any actions you do not use are wasted"
  (36c 15:00: without it Haiku took about half as many actions). It was dropped when the score/game wording was gated.

**Open questions.**
- Q: run a C1 Valley Town pilot now (about $50, laptop), or wait for 37.1-37.4? My recommendation: wait for 37.2 and 37.3,
  since C1 needs the mill/credit economy and cross-institution levies.

**Next.** Restore the sentence with a test; check the 37.3 sub-agent's progress on `wp/inst-cross`; merge package branches into
`bench/first-batch` as they pass their acceptance checks.

## 2026-10-22 17:10 (UTC)

**Found.** The first 37.3 sub-agent was stopped by a safety filter (category "reasoning_extraction") right after my log request,
which asked it to record its thinking. It had changed nothing on `wp/inst-cross`.

**Decided.** Restarted 37.3 with the log described only as a decision record (Doing / Found / Decided / Q / Next). Other
package sessions should use the same wording, not "write what you are thinking".

**Next.** Watch for the first push to `wp/inst-cross`; then the aim_framing sentence fix.
