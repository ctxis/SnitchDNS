$inputFile = $args[0]
$outputFile = $args[1]

if ([string]::IsNullOrEmpty($inputFile) -Or [string]::IsNullOrEmpty($outputFile))
{
    Write-Host "Syntax: .\convert.ps1 [FILE] [OUTPUT]"
    break
}

$inputFile = (Resolve-Path -Path $inputFile)
$outputFile = Resolve-Path $outputFile -ErrorAction SilentlyContinue -ErrorVariable _frperror

if (-not($outputFile)) {
    $outputFile = $_frperror[0].TargetObject
}

$csv = Import-Csv $inputFile
$lines = $csv.domain | sort
$data = ''
Foreach ($line in $lines) {
    $data = $data + $line.split('.')[1]
}

$bytes = [byte[]]::new($data.Length / 2)
For($i = 0; $i -lt $data.Length; $i += 2) {
    $bytes[$i / 2] = [Convert]::ToByte($data.Substring($i, 2), 16)
}

[IO.File]::WriteAllBytes($outputFile, $bytes)