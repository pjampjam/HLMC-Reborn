# Distribution paused - Microsoft Defender review

Do not download, run or share HolyLoisSetup.exe 0.4.0 while this notice is present. Do not restore quarantined copies, add antivirus exclusions or disable protection.

On 2026-10-01, Microsoft Defender Antivirus detected the published installer as Trojan:Win32/Wacatac.C!ml. Defender also blocked the original local installer copies. Its reported status is inactive and not executed. The source audit has not identified malicious behavior, but a false positive is not yet confirmed. Vendor review is required.

The 0.4.0 public installer and main app downloads have been withdrawn. Signed app catalog files stay available for installed clients; no replacement executable has been published to evade this detection. Existing Minecraft profiles, worlds and the game server are unaffected by this distribution hold. You can open Minecraft through your usual Minecraft Launcher or SKlauncher rather than the blocked Holy Lois checker.

Affected installer:
- Version: 0.4.0
- Size: 979456 bytes
- SHA-256 recorded before the detection and on the GitHub asset: de1c39ea80fc8369168c07a767c46ee507cb84ca722414d09b077794de68a542
- Detection: Trojan:Win32/Wacatac.C!ml
- Microsoft review: submitted on 2026-10-01. Final determination is pending; no clearance exists.

Microsoft's developer guidance requires submitting the detected file and waiting for a final determination: https://learn.microsoft.com/en-us/defender-xdr/developer-faq

## Review update on 2026-10-01

Microsoft's portal currently reports no positive detection in cloud/client scanning. The analyst message says no positive scanner result or telemetry indicator was found. The portal still shows In progress and Final determination Pending; this is not a final clearance.

The exact original installer and main app also passed local Defender custom scans with protection enabled and definitions 1.459.503.0. They remain unsigned. No exclusion or protection disabling was used. The owner explicitly chose to keep public executable downloads paused until the final result. Pack/source updates are separate and do not replace the withdrawn binaries.
