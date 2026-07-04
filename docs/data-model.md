# Data Model Notes

The current database should not be renamed just to match product language. This pass treats naming as a product/domain layer.

| Product Term | Current/Risk-Safe Backend Basis | Notes |
| --- | --- | --- |
| Signal | Future feed/post model or composed API response | Current web feed uses local Signal data for the merge pass. |
| Move | `hubs.Event` | Keep table/API stable until joins, attendance, and migration needs are clearer. |
| Circle | Community or group concept, not yet a dedicated model | Can begin as tags or filters before a model exists. |
| Crew | Action team concept, not yet a dedicated model | Likely needs membership and task ownership later. |
| Lead | `MentorshipConnection` plus trusted users | Product copy can say Leads while backend keeps mentorship names. |
| Shift | Future fair-work/work-support model | Do not import RiseUp's Unionized identity into fLOKr UI. |

## Recommended Backend Approach

1. Keep existing model names while product copy settles.
2. Add serializer aliases or endpoint aliases where it improves API clarity.
3. Rename database tables only after API consumers and migrations are planned.
