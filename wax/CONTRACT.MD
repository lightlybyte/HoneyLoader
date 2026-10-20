# Wax Contract

**Status:** DRAFT — not yet stable
**Applies to:** Honey `0.1.x` and the `mc26_3` adapter
**Normative language:** MUST / MUST NOT / SHOULD / MAY per RFC 2119

---

## 1. Purpose

Wax is the stable boundary between Honey mods and Minecraft. A mod compiled against
Wax MUST continue to run, without recompilation, across Minecraft versions supported
by the loader, provided the adapter for the new version implements this contract.

Wax is **not** a Minecraft API. It is a deliberately small set of operations whose
*meaning* is version-independent. The adapter is responsible for mapping those
operations onto whatever Minecraft happens to do internally in a given version.

If an operation cannot be described without naming a Minecraft class, method, or
field, it does not belong in Wax.

---

## 2. What Wax MUST NOT contain

These rules are hard constraints, not style preferences.

- **No Minecraft types.** Wax MUST NOT reference any class, method, or field from
  `net.minecraft.*`, Mojang mappings, or intermediary names. Opaque handles
  (e.g. `PlayerRef`) are the only way to refer to game entities.
- **No ASM types.** Wax MUST NOT depend on `org.objectweb.asm.*`. Bytecode work is
  an engine concern, not a contract concern.
- **No version identifiers in signatures.** No method may take or return a value
  whose meaning is tied to a specific Minecraft version (e.g. no `int` that happens
  to be a protocol number unless Wax defines it).
- **No implementation leakage.** If removing the `mc26_3` adapter would still let
  this file compile, the file is correct. If not, something in Wax depends on the
  adapter and MUST be moved out.

The `wax` Gradle module SHOULD have zero dependencies. If it ever gains one, this
contract is violated and the dependency MUST be justified in this file first.

---

## 3. Core concepts

### 3.1 Opaque handles

Wax refers to game objects through opaque interfaces. A handle MUST expose only
stable, version-independent accessors.

| Handle       | Meaning                                   | Required accessors        |
|--------------|-------------------------------------------|---------------------------|
| `PlayerRef`  | A player, connected or not                | `name()`                  |
| `WorldRef`   | A loaded dimension/world                  | `id()` (stable string)    |
| `BlockPos`   | An integer block coordinate               | `x()`, `y()`, `z()`       |

Handles MUST NOT expose the underlying Minecraft object. Adapters MAY cast
internally; mods MUST NOT be able to.

### 3.2 Events

Events are typed callbacks delivered by the Nectar event bus. An event interface:

- MUST be declared in Wax.
- MUST carry only Wax types and Java primitives.
- MUST be documented with the exact moment it fires, in version-independent terms.
- MUST specify whether it is cancellable, and what cancellation means.

### 3.3 Cancellation

A cancellable event MUST expose a single `cancel()` method and a `isCancelled()`
query. The adapter MUST honour cancellation before the underlying game action
takes effect. An event that claims to be cancellable but fires after the action
has already happened MUST be marked non-cancellable instead.

---

## 4. Required operations (v0.1)

Each entry below is a contract item. "Stable meaning" is what mods are allowed to
rely on. "Adapter obligation" is what every adapter must do to satisfy it.

### 4.1 `OnPlayerJoin` — cancellable: **no**

- **Stable meaning:** Fires once, after a player has fully joined the server or
  entered a singleplayer world, and before the player can interact with the world.
- **Payload:** `PlayerRef player`
- **Adapter obligation:** Must fire exactly once per join. Must NOT fire on
  respawn, dimension change, or reconnect-within-session unless the player
  object is a new join.
- **Why it's in Wax:** It's the canonical event; every adapter must be able to
  provide it, and mods need it before any other gameplay event is meaningful.

### 4.2 `OnPlayerLeave` — cancellable: **no**

- **Stable meaning:** Fires once when a player disconnects or leaves the world,
  after which the `PlayerRef` MUST be considered invalid.
- **Payload:** `PlayerRef player`
- **Adapter obligation:** Must fire exactly once per leave. Calls to the
  `PlayerRef` after this event MAY throw, and mods MUST NOT rely on them.

### 4.3 `OnBlockPlace` — cancellable: **yes**

- **Stable meaning:** Fires when a player attempts to place a block, before the
  world is modified. Cancellation prevents the placement.
- **Payload:** `PlayerRef player`, `BlockPos pos`
- **Adapter obligation:** Must fire before any world mutation caused by the
  placement. If cancelled, the block MUST NOT appear and the player's inventory
  MUST NOT lose the item.
- **Note:** The item/block identity is intentionally not in the payload for v0.1.
  Adding it requires a Wax-level block identity type, which is not yet defined.

### 4.4 `OnBlockBreak` — cancellable: **yes**

- **Stable meaning:** Fires when a player attempts to break a block, before the
  world is modified. Cancellation prevents the break.
- **Payload:** `PlayerRef player`, `BlockPos pos`
- **Adapter obligation:** Same pre-mutation requirement as `OnBlockPlace`.

### 4.5 `OnServerTick` — cancellable: **no**

- **Stable meaning:** Fires once per server tick, at the start of the tick.
- **Payload:** none
- **Adapter obligation:** Must fire exactly once per tick, even when no players
  are connected. Must NOT be used to schedule delayed work — use Nectar
  scheduling for that (out of scope for v0.1).

### 4.6 `OnEntitySpawn` — cancellable: **yes**

- **Stable meaning:** Fires when any non-player entity is about to be added to
  the world. Cancellation prevents the spawn.
- **Payload:** `EntityRef entity`, `WorldRef world`
- **Adapter obligation:** Must fire before the entity is added. If cancelled, the
  entity MUST NOT exist in the world and MUST NOT tick.
- **Note:** `EntityRef` is introduced by this item; see §3.1. Its required
  accessors are deliberately minimal for v0.1.

### 4.7 `OnPlayerChat` — cancellable: **yes**

- **Stable meaning:** Fires when a player sends a chat message, before it is
  broadcast. Cancellation prevents delivery.
- **Payload:** `PlayerRef player`, `String message`
- **Adapter obligation:** Must fire before any recipient receives the message.

### 4.8 `OnDimensionChange` — cancellable: **no**

- **Stable meaning:** Fires after a player has moved to a different dimension.
- **Payload:** `PlayerRef player`, `WorldRef from`, `WorldRef to`
- **Adapter obligation:** Must fire after the move completes, with both world
  references valid at the time of the event.

### 4.9 `OnInventoryChange` — cancellable: **no**

- **Stable meaning:** Fires after a player's inventory contents have changed, for
  any reason (pickup, drop, craft, trade, manual move).
- **Payload:** `PlayerRef player`
- **Adapter obligation:** Must fire at most once per tick per player, even if
  multiple slots changed. Coalescing is required to keep event volume bounded.

### 4.10 `OnPlayerDeath` — cancellable: **no**

- **Stable meaning:** Fires after a player has died, before the respawn screen is
  shown.
- **Payload:** `PlayerRef player`
- **Adapter obligation:** Must fire before respawn logic runs. Must not fire more
  than once per death.

---

## 5. Guarantees across Minecraft versions

These are the promises that make Wax worth having.

1. **Binary compatibility.** A mod compiled against Wax `0.1.x` MUST load and
   run against any adapter that implements this contract, without recompilation.
2. **Event ordering.** For a single player, `OnPlayerJoin` MUST precede every
   other event concerning that player. `OnPlayerLeave` MUST follow them all.
3. **Exactly-once semantics.** Events marked "exactly once" MUST NOT be delivered
   twice for the same logical occurrence, even if the adapter internally observes
   the occurrence through multiple hooks.
4. **Pre-mutation for cancellable events.** A cancellable event MUST fire before
   the world/player state it concerns is mutated. This is the single most
   important guarantee; violating it makes cancellation meaningless.
5. **Handle validity.** A handle MUST remain valid from the event that produced
   it until the corresponding "end" event (`OnPlayerLeave` for players, world
   unload for worlds). After that, behavior is undefined and mods MUST NOT rely
   on it.

---

## 6. Adapter obligations (checklist)

An adapter claiming to implement this contract MUST:

- [ ] Provide a `PlayerRef`, `WorldRef`, `BlockPos` implementation with the
      accessors in §3.1.
- [ ] Implement every event in §4 with the documented firing moment.
- [ ] Honour cancellation for §4.3, §4.4, §4.6, §4.7 before mutation.
- [ ] Coalesce `OnInventoryChange` per §4.9.
- [ ] Pass the Wax conformance tests (see §7) for the Minecraft version it
      targets.
- [ ] Declare the Minecraft version it targets in its own metadata, not in Wax.

An adapter MAY provide additional, non-Wax APIs. Those are not covered by this
contract and mods MUST NOT assume they exist across adapters.

---

## 7. Conformance tests

The `wax` module SHOULD eventually ship a test kit that adapters run against.
For v0.1, the minimum bar is:

1. **Join/leave pairing:** a simulated join produces exactly one `OnPlayerJoin`,
   and a leave produces exactly one `OnPlayerLeave`.
2. **Cancellation is pre-mutation:** cancelling `OnBlockPlace` leaves the world
   unchanged and the inventory intact.
3. **Ordering:** for a scripted player session, the event order matches §5.2.
4. **No duplicates:** a single logical occurrence produces one event, not two,
   even when the adapter has multiple internal hooks for it.

These tests do not exist yet. Writing them is the next task after the interfaces
in §4 are declared in Java.

---

## 8. Change policy

- Adding a new event or handle is a **minor** change.
- Adding a required accessor to an existing handle is a **minor** change, but
  only if it can be implemented by every adapter without game-version-specific
  work. Otherwise it is a **major** change.
- Changing an event's firing moment, payload, or cancellability is a **major**
  change.
- Removing anything is a **major** change.
- Loosening a guarantee in §5 is a **major** change.

Until Honey reaches `1.0.0`, every change is permitted and the version stays in
`0.x`. After `1.0.0`, this policy is binding.

---

## 9. Open questions (must be resolved before `1.0.0`)

- **Block identity.** `OnBlockPlace`/`OnBlockBreak` carry only a position. Mods
  that care *what* was placed/broken cannot use them yet. A Wax-level block
  identity type is needed; it MUST NOT be a Minecraft class.
- **Scheduling.** `OnServerTick` exists, but there is no Wax-level way to run
  code after N ticks. This is likely required before real mods are possible.
- **Threading.** The contract does not yet say which thread events fire on.
  Adapters are free to choose, which is a portability hazard. This MUST be
  specified before `1.0.0`.
- **Error handling.** What happens when a mod throws inside an event handler?
  The contract is silent. A policy is required.