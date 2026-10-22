$sig = '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint esFlags);'
$k = Add-Type -MemberDefinition $sig -Name Veille -Namespace Slmsp -PassThru
# ES_CONTINUOUS | ES_SYSTEM_REQUIRED (pas d'écran requis)
while ($true) { [void]$k::SetThreadExecutionState([uint32]"0x80000001"); Start-Sleep -Seconds 50 }
