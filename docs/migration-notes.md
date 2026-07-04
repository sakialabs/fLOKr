# Migration Notes

## What Was Ported From RiseUp

- Inline composer energy, now expressed as `Post a Signal`.
- Reaction language, adapted to Boost, Helpful, Solidarity, and I can help.
- Events/action tone, adapted to Moves.
- Worker-support ideas, adapted to Shifts.
- Stronger grassroots action copy, softened to fit fLOKr's hub-and-care model.

## What Was Not Ported

- RiseUp branding.
- Separate RiseUp routes or product identity.
- FastAPI backend code.
- Unionized public labels.
- Database model renames.

## Current Compatibility Choices

- `/loop` is the primary route.
- `/community` remains usable for old links.
- Existing Django APIs for events, mentorship, feedback, and hub data remain stable.
