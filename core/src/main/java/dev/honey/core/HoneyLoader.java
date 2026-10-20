package dev.honey.core;

import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassVisitor;
import org.objectweb.asm.Opcodes;

public final class HoneyLoader {

    public static void main(String[] args) {
        System.out.println("Honey " + HoneyLoader.class.getPackage().getImplementationVersion() + " starting");
        // Real work: discover adapters, build Wax implementation, launch game.
        // This is where you will eventually call into the launcher / agent.
    }

    /** Sanity check that ASM is on the classpath. */
    public static void verifyAsm() {
        ClassReader reader = new ClassReader(new byte[0]); // will throw, but proves linkage
    }
}