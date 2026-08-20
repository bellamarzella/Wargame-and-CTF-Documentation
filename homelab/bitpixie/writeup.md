# Verifying the BitPixie BitLocker Bypass on a Decommissioned Machine

> **Disclaimer:** I didn't discover this vulnerability, and I didn't write the exploit. I used an existing proof-of-concept ([andigandhi/bitpixie](https://github.com/andigandhi/bitpixie), CVE-2023-21563) on hardware I own, largely following an existing walkthrough. This is a lab notebook entry about that experience, plus notes on mitigation.

## Background

A decommissioned enterprise mini PC was given to me. But instead of a clean slate, it still had its original Windows install with **TPM-bound BitLocker** active. This was a prime example of a failure in asset disposition and the kind of scenario an attacker might exploit, so before wiping it, I used it to see how far a physical-access attacker gets.

Target:
- Decommissioned enterprise mini PC
- TPM-only BitLocker (no PIN); auto-unlocks at boot
- Legacy boot manager (dated **2019**, never revoked via the March 2024 DBX update)
- Secure Boot enabled, PXE boot available

## TLDR

The BitPixie attack works in two phases: first you grab a modified copy of the target's BCD boot configuration, then you PXE-boot the machine with it so the BitLocker Volume Master Key gets leaked from memory.

**Phase 1: grab the BCD.** I booted the machine into WinRE (Shift+Restart → Command Prompt), connected to a small SMB share on my attacker box, and ran a script that exported and modified the BCD. It uploaded the modded BCD back to me.

**Phase 2: PXE boot.** With the modded BCD in place, I booted the target over the network. The boot chain (bootmgfw → shimx64 → grub → initramfs) dropped me into a minimal Linux environment.

**Phase 3: unlock.** From there I ran the exploit to pull the VMK out of memory, decrypted the drive, and mounted it read-write. Full file system access. To demonstrate the impact, I reset the local Administrator password with `chntpw` and logged straight into Windows on the next boot.

## What I Did

The exploit itself is a tool you run, most of my time went into the surrounding environment.

### Fixing WinRE first
The machine's recovery environment was broken, `winre.wim` was missing entirely (there were remnants of a prior failed attack on the machine). Before I could even reach the command prompt the attack needs, I had to rebuild WinRE. I extracted `winre.wim` and `boot.sdi` from a Windows install image with 7-Zip, copied them into the recovery partition, and re-wired the BCD to point at it.

### WSL2 as the attacker box
My attacker machine runs Windows 11, so the PXE/DHCP/SMB servers ran inside **WSL2 with mirrored networking**. This was the source of most of the friction:

- **Port 445 conflict.** Windows' own SMB service was already listening on port 445, and WSL shares the host's network stack, so the exploit's SMB server couldn't bind. I had to stop the Windows Server service, and even then the kernel kept the port open until a full stop. Also had to remember to restore it afterwards.
- **ARP is answered by Windows, not WSL.** The target couldn't reach the attacker's IP (`10.13.37.100`) even though WSL had it assigned because Windows answers ARP for the physical NIC, and Windows didn't have that address. Adding the IP to the Windows adapter itself fixed it. "Destination host unreachable" in a case like this doesn't mean the cable's bad.
- **DHCP over a point-to-point cable.** A direct ethernet link has no DHCP server, so both machines fell back to `169.254.x.x` (APIPA) addresses. That's expected and healthy, but it took me a while to stop seeing it as a failure. In the end I set a static IP on the target's WinRE and skipped DHCP entirely.

### The hibernation issue
In the middle of the exploit, I decided to go for a walk at precisely the worst possible time. I came back, ran the exploit which unlocked the volume, but mounted **read-only** because Windows had been hibernating. `ntfs-3g`'s `remove_hiberfile` option cleared the hibernation flag and gave me read-write access. (You need to remount the *decrypted image* the exploit creates, not the raw encrypted partition.)

### Restoring the attacker afterwards
The attack left a few loose ends on my own machine: the temp IP on the ethernet adapter, extra firewall rules, and a stopped SMB service. The ethernet adapter ended up stuck on APIPA because removing the temporary static IP left IPv4 without DHCP. Re-enabling DHCP on the adapter fixed it. Good reminder to clean up after yourself.

## Key Takeaways

- Physical access to unpatched legacy hardware can bypass BitLocker entirely if the boot manager was never revoked and there's no pre-boot authentication.
- Incomplete asset disposition leaves working encryption as a speed bump, not a wall.
- Running this from Windows/WSL2 was most of the actual challenge. The quirks above (ARP ownership, port conflicts, APIPA confusion) are what trip you up on real hardware.

## Mitigations

- **Use pre-boot authentication (TPM + PIN)**: the TPM key is then never released without a PIN.
- **Apply UEFI Secure Boot revocation (DBX) updates** via patch management.
- **Harden UEFI:** password-protect the BIOS and remove PXE/network boot options.
- **Wipe storage properly before disposal**: BitLocker is not a substitute for a clean wipe.

## Credits

- Original research: Rairii (CVE-2023-21563), first public demo at 38C3 by th0mas
- [BitPixie PoC repository](https://github.com/andigandhi/bitpixie)
- [Th0mas' writeup](https://neodyme.io/en/blog/bitlocker_screwed_without_a_screwdriver/)