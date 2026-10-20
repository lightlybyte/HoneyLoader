package dev.honey.wax;

/**
 * Stable contract between Honey mods and the Minecraft adapter.
 * Everything here must be expressible without referencing Minecraft classes directly.
 */
public interface WaxContract {

    /** Fired when a player joins. Argument type must remain stable across MC versions. */
    interface OnPlayerJoin {
        void onJoin(PlayerRef player);
    }

    /** Opaque handle to a player. The adapter maps this to the real MC entity. */
    interface PlayerRef {
        String name();
    }

    // TODO: add the remaining 8–18 operations from the 26.3 spec.
}