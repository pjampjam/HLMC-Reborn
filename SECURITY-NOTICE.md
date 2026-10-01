# Original downloads restored - Microsoft review update

On 2026-10-01, the owner explicitly approved restoring the exact original HolyLoisSetup.exe 0.4.0 and HolyLoisReborn.exe 0.4.0 to the public GitHub release after the current scan checks. No binaries were rebuilt, modified or repackaged to avoid detection.

Defender previously flagged the installer as Trojan:Win32/Wacatac.C!ml. The original installer and launcher now pass local custom scans with Defender antivirus and real-time protection enabled, Normal mode and updated definitions 1.459.505.0. Microsoft reports no current cloud/client detection. Its analyst found no positive scanner result or telemetry indicator and says the case will close without further action. The portal's formal final determination still reads Pending, so this is not a final vendor clearance or a guarantee for every PC.

Public files downloaded again after restoration match the scanned originals:

- HolyLoisSetup.exe: 979456 bytes; SHA-256 de1c39ea80fc8369168c07a767c46ee507cb84ca722414d09b077794de68a542
- HolyLoisReborn.exe: 66898158 bytes; SHA-256 26731e55b040147b5609cc9b96d587d03e1fc2e8206efe7d674df1c2c6448d26

Both files remain unsigned. Keep antivirus enabled. If a threat is detected, leave the file blocked and report the detection and Defender definition version. Do not add exclusions, restore quarantined files or disable protection. The diagnostic instructions in Microsoft's reply apply if detection can be reproduced with current definitions; no private diagnostic data has been collected or submitted here.

The owner's approval is limited to these exact checked release files. The build guard continues to block publishing newly built public executables while this notice exists. Future builds require their own checks and a separate decision about the guard. Pack updates remain signed and independent of the launcher executable.

Review: https://www.microsoft.com/en-us/wdsi/filesubmission
Public release: https://github.com/pjampjam/HLMC-Reborn/releases/tag/v0.4.0
