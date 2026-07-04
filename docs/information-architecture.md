# Information Architecture

## MVP Navigation

The primary app navigation should stay focused:

- Home
- Reservations
- Items
- Hubs
- Loop
- Settings

## Loop Structure

Loop is the place where users see and post Signals. The first version exposes Circles, Crews, Moves, and Shifts as filters and cards inside Loop rather than expanding the sidebar too early.

Recommended Loop filters:

- All Signals
- Asks
- Offers
- Welcomes
- Moves
- Hub Updates
- Shifts
- My Signals

## Compatibility

`/loop` is the primary route. `/community` can remain during migration so old links and backend assumptions keep working.
