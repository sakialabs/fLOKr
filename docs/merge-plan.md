# fLOKr + RiseUp Merge Plan

## Rationale

RiseUp explored stronger feed, event, reaction, organizing, and worker-support patterns. fLOKr already has the stronger hub, inventory, reservation, account, and community foundation. The merge keeps fLOKr as the base and ports only the useful product ideas.

## Phase 1: Language and Navigation

- Use Loop for the main feed surface.
- Use Signals for updates, asks, offers, welcomes, hub updates, Moves, and Shifts.
- Use Moves instead of Events in public UI.
- Use Shifts instead of Unionized or worker-only branding.
- Use Circles, Crews, and Leads where those terms are more precise than generic community wording.

## Phase 2: Route Alignment

- Add `/loop` as the main route for the feed surface.
- Keep `/community` available as a compatibility surface while old links exist.
- Keep existing backend API paths stable for now.

## Phase 3: Feature Migration

- Port the inline composer concept as `Post a Signal`.
- Port reaction energy as Boost, Helpful, Solidarity, and I can help.
- Fold event/action copy into Moves.
- Fold fair-work copy into Shifts.

## Phase 4: Backend Review

Do not rename database models until the product behavior is stable. Prefer serializers, aliases, frontend language, and docs first.
