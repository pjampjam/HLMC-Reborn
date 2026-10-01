# Distribution paused again - browser download detection reproduced

On 2026-10-01 at 22:18 Europe/Riga, Windows Defender removed the original HolyLoisSetup.exe downloaded through the browser from GitHub. Detection: Trojan:Win32/Wacatac.C!ml, threat ID 2147749372, definitions 1.459.505.0. Both public 0.4.0 executable assets have been withdrawn again. Do not use earlier installer download links or ask friends to whitelist them.

Local custom scans previously reported no threats for the same bytes. That did not establish browser-download safety. The machine currently also has a non-remediating Allow rule for this threat ID; its creation time is not established, so earlier clean scans cannot settle this issue. The strengthened release check refuses to report success while explicit non-remediating threat rules are present. No protection settings were changed by the agent.

Microsoft's submitted-sample page reports no positive cloud/client detection, but its formal final result is still Pending. The reproduced download event is contrary evidence requiring the requested diagnostic follow-up. The suspected false positive remains unconfirmed. Trusted Authenticode signing can help Microsoft identify the publisher, but it does not guarantee that this detection disappears.

The 0.4.0 files were restored briefly with explicit owner approval after clean local checks and then withdrawn when browser detection recurred. No binaries were rebuilt, renamed, rehosted or repackaged to avoid detection. Signed pack/source updates and the game server are independent of this hold. Existing Minecraft Launcher and SKlauncher profiles can still be used.

The owner removed the Allow rule and generated Defender MPSupportFiles.cab in an administrator terminal. With explicit owner approval, the diagnostics and follow-up report were submitted privately to Microsoft at 22:35 Europe/Riga on 2026-10-01, referencing the original case. The follow-up is Submitted with a Pending result. The diagnostic file was not uploaded to GitHub or sent to friends. Public executable distribution remains paused while the reproduced browser detection is investigated.

Affected installer: version 0.4.0, 979456 bytes, SHA-256 de1c39ea80fc8369168c07a767c46ee507cb84ca722414d09b077794de68a542.
Accompanying launcher: version 0.4.0, 66898158 bytes, SHA-256 26731e55b040147b5609cc9b96d587d03e1fc2e8206efe7d674df1c2c6448d26.
Both are unsigned. Keep antivirus and cloud protection enabled. Leave quarantined copies blocked.

Official developer guidance: https://learn.microsoft.com/en-us/defender-xdr/developer-faq
Review: https://www.microsoft.com/en-us/wdsi/filesubmission
