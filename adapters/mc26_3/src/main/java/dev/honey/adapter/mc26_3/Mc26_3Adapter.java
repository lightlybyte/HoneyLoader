package dev.honey.adapter.mc26_3;

import dev.honey.wax.WaxContract;

/**
 * Implements the Wax contract against Minecraft 26.3 internals.
 * Nothing here yet — this is where you map Wax calls to 26.3 classes/methods.
 */
public final class Mc26_3Adapter {

    public static final String MC_VERSION = "26.3";

    public WaxContract.PlayerRef wrapPlayer(Object mcPlayer) {
        throw new UnsupportedOperationException("26.3 adapter not implemented yet");
    }
}