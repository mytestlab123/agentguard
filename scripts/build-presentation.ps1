param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePath,
    [Parameter(Mandatory = $true)]
    [string]$OutputPath,
    [Parameter(Mandatory = $true)]
    [string]$PreviewDir,
    [Parameter(Mandatory = $true)]
    [string]$ValidationPath
)

$ErrorActionPreference = 'Stop'

$msoFalse = 0
$msoTrue = -1
$msoTextOrientationHorizontal = 1
$msoShapeRectangle = 1
$msoShapeRoundedRectangle = 5
$msoPicture = 13
$ppAlignLeft = 1
$ppAlignCenter = 2
$ppLayoutBlank = 12
$ppSaveAsOpenXMLPresentation = 24

function Get-OfficeColor {
    param([Parameter(Mandatory = $true)][string]$Hex)
    $value = $Hex.TrimStart('#')
    if ($value.Length -ne 6) {
        throw "invalid color: $Hex"
    }
    $red = [Convert]::ToInt32($value.Substring(0, 2), 16)
    $green = [Convert]::ToInt32($value.Substring(2, 2), 16)
    $blue = [Convert]::ToInt32($value.Substring(4, 2), 16)
    return $red + ($green * 256) + ($blue * 65536)
}

$colors = @{
    Background = Get-OfficeColor '#f7f9fc'
    Surface = Get-OfficeColor '#ffffff'
    Text = Get-OfficeColor '#132238'
    Muted = Get-OfficeColor '#5b6b7c'
    Teal = Get-OfficeColor '#0f766e'
    Cyan = Get-OfficeColor '#0369a1'
    Border = Get-OfficeColor '#cbd5e1'
    Green = Get-OfficeColor '#15803d'
    Amber = Get-OfficeColor '#b45309'
    Red = Get-OfficeColor '#b91c1c'
}

function Convert-InlineMarkdown {
    param([Parameter(Mandatory = $true)][string]$Text)
    $result = $Text.Replace('**', '').Replace('`', '')
    $result = $result.Replace('&rarr;', [string][char]0x2192)
    return $result.Trim()
}

function Get-SlideSources {
    param([Parameter(Mandatory = $true)][string]$Path)

    $raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
    $parts = [regex]::Split($raw, '(?m)^---\s*$') |
        Where-Object { $_.Trim().Length -gt 0 }
    if ($parts.Count -ne 10) {
        throw "expected one front matter block and nine slides; found $($parts.Count) blocks"
    }

    $slides = @()
    foreach ($block in $parts | Select-Object -Skip 1) {
        $noteMatch = [regex]::Match(
            $block,
            '(?s)<!--\s*Speaker note:\s*(.*?)\s*-->'
        )
        if (-not $noteMatch.Success) {
            throw 'every slide requires one Speaker note comment'
        }
        $note = $noteMatch.Groups[1].Value.Trim()

        $imageMatch = [regex]::Match($block, '!\[[^\]]*\]\(([^)]+)\)')
        $imagePath = $null
        if ($imageMatch.Success) {
            $imagePath = Join-Path (Split-Path -Parent $Path) $imageMatch.Groups[1].Value
        }

        $visible = [regex]::Replace($block, '(?s)<!--.*?-->', '')
        $visible = [regex]::Replace($visible, '!\[[^\]]*\]\([^)]+\)', '')
        $title = $null
        $subtitle = $null
        $items = New-Object System.Collections.Generic.List[object]
        $currentType = $null
        $currentText = ''

        foreach ($rawLine in ($visible -split "`r?`n")) {
            $line = $rawLine.TrimEnd()
            if ($line -match '^# (.+)$') {
                $title = Convert-InlineMarkdown $Matches[1]
                continue
            }
            if ($line -match '^## (.+)$') {
                $subtitle = Convert-InlineMarkdown $Matches[1]
                continue
            }
            if ($line.Trim().Length -eq 0) {
                if ($currentType) {
                    $items.Add([pscustomobject]@{
                        Type = $currentType
                        Text = Convert-InlineMarkdown $currentText
                    })
                    $currentType = $null
                    $currentText = ''
                }
                continue
            }
            if ($line -match '^\s*-\s+(.+)$') {
                if ($currentType) {
                    $items.Add([pscustomobject]@{
                        Type = $currentType
                        Text = Convert-InlineMarkdown $currentText
                    })
                }
                $currentType = 'bullet'
                $currentText = $Matches[1]
                continue
            }
            if (-not $currentType) {
                $currentType = 'paragraph'
                $currentText = $line.Trim()
            } else {
                $currentText = "$currentText $($line.Trim())"
            }
        }
        if ($currentType) {
            $items.Add([pscustomobject]@{
                Type = $currentType
                Text = Convert-InlineMarkdown $currentText
            })
        }
        if (-not $title) {
            throw 'every slide requires one level-one heading'
        }
        $slides += [pscustomobject]@{
            Title = $title
            Subtitle = $subtitle
            Items = $items.ToArray()
            ImagePath = $imagePath
            Note = $note
        }
    }
    return $slides
}

function Add-Text {
    param(
        [Parameter(Mandatory = $true)]$Slide,
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][double]$Left,
        [Parameter(Mandatory = $true)][double]$Top,
        [Parameter(Mandatory = $true)][double]$Width,
        [Parameter(Mandatory = $true)][double]$Height,
        [Parameter(Mandatory = $true)][double]$Size,
        [Parameter(Mandatory = $true)][int]$Color,
        [bool]$Bold = $false,
        [int]$Align = $ppAlignLeft
    )
    $shape = $Slide.Shapes.AddTextbox(
        $msoTextOrientationHorizontal,
        $Left,
        $Top,
        $Width,
        $Height
    )
    $shape.Fill.Visible = $msoFalse
    $shape.Line.Visible = $msoFalse
    $shape.TextFrame2.MarginLeft = 0
    $shape.TextFrame2.MarginRight = 0
    $shape.TextFrame2.MarginTop = 0
    $shape.TextFrame2.MarginBottom = 0
    $shape.TextFrame2.WordWrap = $msoTrue
    $shape.TextFrame2.TextRange.Text = $Text
    $shape.TextFrame2.TextRange.Font.Name = 'Arial'
    $shape.TextFrame2.TextRange.Font.Size = $Size
    $shape.TextFrame2.TextRange.Font.Bold = if ($Bold) { $msoTrue } else { $msoFalse }
    $shape.TextFrame2.TextRange.Font.Fill.ForeColor.RGB = $Color
    $shape.TextFrame2.TextRange.ParagraphFormat.Alignment = $Align
    return $shape
}

function Add-Card {
    param(
        [Parameter(Mandatory = $true)]$Slide,
        [Parameter(Mandatory = $true)][double]$Left,
        [Parameter(Mandatory = $true)][double]$Top,
        [Parameter(Mandatory = $true)][double]$Width,
        [Parameter(Mandatory = $true)][double]$Height,
        [int]$Fill = $colors.Surface,
        [int]$Line = $colors.Border
    )
    $shape = $Slide.Shapes.AddShape(
        $msoShapeRoundedRectangle,
        $Left,
        $Top,
        $Width,
        $Height
    )
    $shape.Fill.Solid()
    $shape.Fill.ForeColor.RGB = $Fill
    $shape.Line.ForeColor.RGB = $Line
    $shape.Line.Weight = 1
    return $shape
}

function Add-SlideChrome {
    param(
        [Parameter(Mandatory = $true)]$Slide,
        [Parameter(Mandatory = $true)][int]$Number,
        [Parameter(Mandatory = $true)][string]$Title
    )
    $background = $Slide.Background.Fill
    $background.Solid()
    $background.ForeColor.RGB = $colors.Background
    $accent = $Slide.Shapes.AddShape($msoShapeRectangle, 0, 0, 12, 540)
    $accent.Fill.Solid()
    $accent.Fill.ForeColor.RGB = $colors.Teal
    $accent.Line.Visible = $msoFalse
    Add-Text $Slide $Title 42 24 790 48 28 $colors.Teal $true | Out-Null
    Add-Text $Slide 'Compliance Guard' 795 29 125 20 11 $colors.Muted $true $ppAlignCenter | Out-Null
    Add-Text $Slide ([string]$Number) 905 508 20 16 9 $colors.Muted $false $ppAlignCenter | Out-Null
}

function Get-BodyText {
    param([Parameter(Mandatory = $true)]$Items)
    $bullet = [string][char]0x2022
    return (($Items | ForEach-Object {
        if ($_.Type -eq 'bullet') { "$bullet $($_.Text)" } else { $_.Text }
    }) -join "`r`n`r`n")
}

function Add-PictureContained {
    param(
        [Parameter(Mandatory = $true)]$Slide,
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][double]$Left,
        [Parameter(Mandatory = $true)][double]$Top,
        [Parameter(Mandatory = $true)][double]$Width,
        [Parameter(Mandatory = $true)][double]$Height
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "missing presentation image: $Path"
    }
    Add-Card $Slide $Left $Top $Width $Height | Out-Null
    $picture = $Slide.Shapes.AddPicture($Path, $msoFalse, $msoTrue, 0, 0, -1, -1)
    $scale = [Math]::Min(($Width - 16) / $picture.Width, ($Height - 16) / $picture.Height)
    $picture.Width = $picture.Width * $scale
    $picture.Height = $picture.Height * $scale
    $picture.Left = $Left + (($Width - $picture.Width) / 2)
    $picture.Top = $Top + (($Height - $picture.Height) / 2)
    return $picture
}

function Set-SpeakerNote {
    param(
        [Parameter(Mandatory = $true)]$Slide,
        [Parameter(Mandatory = $true)][string]$Note
    )
    $noteShape = $null
    foreach ($placeholder in @($Slide.NotesPage.Shapes.Placeholders)) {
        if ($placeholder.PlaceholderFormat.Type -eq 2) {
            $noteShape = $placeholder
            break
        }
    }
    if (-not $noteShape) {
        throw "speaker-note placeholder is unavailable on slide $($Slide.SlideIndex)"
    }
    $noteShape.TextFrame.TextRange.Text = $Note
}

function Set-SafeCoreProperties {
    param([Parameter(Mandatory = $true)][string]$Path)
    Add-Type -AssemblyName System.IO.Compression
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [System.IO.Compression.ZipFile]::Open(
        $Path,
        [System.IO.Compression.ZipArchiveMode]::Update
    )
    try {
        $entry = $archive.GetEntry('docProps/core.xml')
        if (-not $entry) {
            throw 'PowerPoint core properties are missing'
        }
        $reader = New-Object System.IO.StreamReader($entry.Open())
        try {
            $core = $reader.ReadToEnd()
        } finally {
            $reader.Dispose()
        }
        $core = [regex]::Replace(
            $core,
            '<dc:creator>.*?</dc:creator>',
            '<dc:creator>AgentGuard</dc:creator>'
        )
        $core = [regex]::Replace(
            $core,
            '<cp:lastModifiedBy>.*?</cp:lastModifiedBy>',
            '<cp:lastModifiedBy>AgentGuard</cp:lastModifiedBy>'
        )
        $entry.Delete()
        $safeEntry = $archive.CreateEntry('docProps/core.xml')
        $writer = New-Object System.IO.StreamWriter($safeEntry.Open())
        try {
            $writer.Write($core)
        } finally {
            $writer.Dispose()
        }
        return $core
    } finally {
        $archive.Dispose()
    }
}

function Add-ProofSlide {
    param(
        [Parameter(Mandatory = $true)]$Slide,
        [Parameter(Mandatory = $true)]$Source,
        [Parameter(Mandatory = $true)][int]$Index,
        [Parameter(Mandatory = $true)][int]$DecisionColor
    )
    Add-SlideChrome $Slide $Index $Source.Title
    $bodyItems = @($Source.Items | Where-Object {
        -not ($_.Type -eq 'paragraph' -and $_.Text -like 'DEMO-PROVEN*')
    })
    $body = Get-BodyText $bodyItems
    Add-Text $Slide $body 42 105 252 310 17 $colors.Text | Out-Null
    Add-PictureContained $Slide $Source.ImagePath 310 78 615 420 | Out-Null
    $label = if ($Index -eq 7) { 'APPROVED + VERIFIED' } elseif ($Index -eq 8) { 'BYPASS DENIED' } else { 'APPROVAL REQUIRED' }
    Add-Text $Slide $label 42 444 280 34 17 $DecisionColor $true | Out-Null
    Add-Text $Slide 'DEMO-PROVEN | LOCAL SYNTHETIC POC' 42 486 280 18 9 $colors.Muted $true | Out-Null
}

function Add-DeckSlide {
    param(
        [Parameter(Mandatory = $true)]$Presentation,
        [Parameter(Mandatory = $true)]$Source,
        [Parameter(Mandatory = $true)][int]$Index
    )
    $slide = $Presentation.Slides.Add($Index, $ppLayoutBlank)
    $slide.Background.Fill.Solid()
    $slide.Background.Fill.ForeColor.RGB = $colors.Background

    switch ($Index) {
        1 {
            $bar = $slide.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 16)
            $bar.Fill.Solid()
            $bar.Fill.ForeColor.RGB = $colors.Teal
            $bar.Line.Visible = $msoFalse
            Add-Text $slide $Source.Title 70 120 820 90 44 $colors.Teal $true $ppAlignCenter | Out-Null
            Add-Text $slide $Source.Subtitle 120 220 720 46 24 $colors.Text $true $ppAlignCenter | Out-Null
            Add-Text $slide (Get-BodyText $Source.Items) 150 292 660 110 21 $colors.Muted $false $ppAlignCenter | Out-Null
            Add-Text $slide 'LOCAL SYNTHETIC POC' 380 455 200 24 11 $colors.Cyan $true $ppAlignCenter | Out-Null
        }
        2 {
            Add-SlideChrome $slide $Index $Source.Title
            Add-Text $slide $Source.Items[0].Text 42 88 875 58 22 $colors.Text $true | Out-Null
            Add-Card $slide 42 160 875 68 $colors.Surface $colors.Teal | Out-Null
            Add-Text $slide $Source.Subtitle 62 176 835 38 17 $colors.Teal $true $ppAlignCenter | Out-Null
            Add-Text $slide (Get-BodyText ($Source.Items | Select-Object -Skip 1)) 62 252 820 210 19 $colors.Text | Out-Null
        }
        3 {
            Add-SlideChrome $slide $Index $Source.Title
            $bullets = @($Source.Items | Where-Object Type -eq 'bullet')
            Add-Card $slide 42 100 415 128 | Out-Null
            Add-Text $slide $bullets[0].Text 66 126 365 72 22 $colors.Teal $true | Out-Null
            Add-Card $slide 500 100 415 128 | Out-Null
            Add-Text $slide $bullets[1].Text 524 126 365 72 22 $colors.Cyan $true | Out-Null
            $remaining = @($Source.Items | Where-Object Type -eq 'paragraph')
            Add-Text $slide (Get-BodyText $remaining) 62 270 830 155 19 $colors.Text | Out-Null
            Add-Text $slide 'Sources: CISA / NSA (2023) | Verizon DBIR (2026)' 62 460 830 22 11 $colors.Muted | Out-Null
        }
        4 {
            Add-SlideChrome $slide $Index $Source.Title
            Add-Text $slide $Source.Subtitle 42 82 875 44 24 $colors.Cyan $true | Out-Null
            $bullets = @($Source.Items | Where-Object Type -eq 'bullet')
            for ($i = 0; $i -lt $bullets.Count; $i++) {
                $top = 145 + ($i * 70)
                Add-Card $slide 62 $top 835 56 | Out-Null
                Add-Text $slide $bullets[$i].Text 84 ($top + 13) 790 34 17 $colors.Text | Out-Null
            }
            $last = @($Source.Items | Where-Object Type -eq 'paragraph')[-1]
            Add-Text $slide $last.Text 62 445 835 30 18 $colors.Teal $true $ppAlignCenter | Out-Null
        }
        5 {
            Add-SlideChrome $slide $Index $Source.Title
            Add-Card $slide 42 100 875 92 $colors.Surface $colors.Teal | Out-Null
            Add-Text $slide $Source.Subtitle 62 125 835 50 23 $colors.Teal $true $ppAlignCenter | Out-Null
            Add-Text $slide (Get-BodyText $Source.Items) 62 230 835 225 20 $colors.Text | Out-Null
        }
        6 { Add-ProofSlide $slide $Source $Index $colors.Amber }
        7 { Add-ProofSlide $slide $Source $Index $colors.Green }
        8 { Add-ProofSlide $slide $Source $Index $colors.Red }
        9 {
            Add-SlideChrome $slide $Index $Source.Title
            $bullets = @($Source.Items | Where-Object Type -eq 'bullet')
            Add-Text $slide (Get-BodyText $bullets) 52 95 400 260 19 $colors.Text | Out-Null
            Add-Card $slide 500 100 415 310 $colors.Surface $colors.Teal | Out-Null
            Add-Text $slide $Source.Subtitle 528 125 360 130 23 $colors.Teal $true $ppAlignCenter | Out-Null
            $paragraphs = @($Source.Items | Where-Object Type -eq 'paragraph')
            Add-Text $slide 'DIRECTION APPROVAL ONLY' 528 280 360 34 18 $colors.Cyan $true $ppAlignCenter | Out-Null
            Add-Text $slide $paragraphs[0].Text 528 330 360 58 13 $colors.Muted $false $ppAlignCenter | Out-Null
            Add-Text $slide $paragraphs[1].Text 500 435 415 62 13 $colors.Muted $false $ppAlignCenter | Out-Null
        }
        default { throw "unsupported slide index: $Index" }
    }
    Set-SpeakerNote $slide $Source.Note
}

if (-not (Test-Path -LiteralPath $SourcePath)) {
    throw "source deck is missing: $SourcePath"
}
$slides = Get-SlideSources $SourcePath
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutputPath) | Out-Null
New-Item -ItemType Directory -Force -Path $PreviewDir | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $ValidationPath) | Out-Null
if (Test-Path -LiteralPath $OutputPath) {
    Remove-Item -LiteralPath $OutputPath -Force
}

$powerPoint = $null
$presentation = $null
try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $powerPoint.Visible = $msoTrue
    $presentation = $powerPoint.Presentations.Add()
    $presentation.PageSetup.SlideWidth = 960
    $presentation.PageSetup.SlideHeight = 540

    for ($i = 0; $i -lt $slides.Count; $i++) {
        Add-DeckSlide $presentation $slides[$i] ($i + 1)
    }
    foreach ($property in @('Author', 'Last Save By', 'Company', 'Manager')) {
        try {
            $presentation.BuiltInDocumentProperties.Item($property).Value = 'AgentGuard'
        } catch {
            # Some Office versions do not expose every built-in property.
        }
    }
    $presentation.SaveAs($OutputPath, $ppSaveAsOpenXMLPresentation)
    $presentation.Close()
    $presentation = $null
    $powerPoint.Quit()
    $powerPoint = $null

    $safeCore = Set-SafeCoreProperties $OutputPath
    if ($safeCore -notmatch '<dc:creator>AgentGuard</dc:creator>' -or
        $safeCore -notmatch '<cp:lastModifiedBy>AgentGuard</cp:lastModifiedBy>') {
        throw 'PowerPoint core metadata was not sanitized'
    }

    $powerPoint = New-Object -ComObject PowerPoint.Application
    $powerPoint.Visible = $msoTrue
    $presentation = $powerPoint.Presentations.Open($OutputPath, $msoTrue, $msoFalse, $msoFalse)
    if ($presentation.Slides.Count -ne 9) {
        throw "generated deck has $($presentation.Slides.Count) slides, expected 9"
    }

    $editableTextShapes = 0
    $pictureShapes = 0
    $notesSlides = 0
    $titlesFound = @()
    foreach ($slide in @($presentation.Slides)) {
        $titleFound = $false
        foreach ($shape in @($slide.Shapes)) {
            if ($shape.Type -eq $msoPicture) {
                $pictureShapes++
            }
            if ($shape.HasTextFrame -eq $msoTrue -and $shape.TextFrame.HasText -eq $msoTrue) {
                $editableTextShapes++
                if ($shape.TextFrame.TextRange.Text.Contains($slides[$slide.SlideIndex - 1].Title)) {
                    $titleFound = $true
                }
            }
        }
        if (-not $titleFound) {
            throw "title not found on slide $($slide.SlideIndex)"
        }
        $titlesFound += $slides[$slide.SlideIndex - 1].Title
        foreach ($placeholder in @($slide.NotesPage.Shapes.Placeholders)) {
            if ($placeholder.PlaceholderFormat.Type -eq 2 -and
                $placeholder.TextFrame.TextRange.Text.Trim().Length -gt 0) {
                $notesSlides++
                break
            }
        }
    }
    if ($editableTextShapes -lt 25) {
        throw "generated deck has too few editable text shapes: $editableTextShapes"
    }
    if ($pictureShapes -ne 3) {
        throw "generated deck has $pictureShapes pictures, expected 3"
    }
    if ($notesSlides -ne 9) {
        throw "generated deck has speaker notes on $notesSlides slides, expected 9"
    }

    $presentation.Export($PreviewDir, 'PNG', 1920, 1080)
    $validation = [ordered]@{
        result = 'PASS'
        slideCount = $presentation.Slides.Count
        slideSize = '16:9'
        editableTextShapes = $editableTextShapes
        pictureShapes = $pictureShapes
        speakerNoteSlides = $notesSlides
        metadataSanitized = $true
        titles = $titlesFound
        previewCount = @(Get-ChildItem -LiteralPath $PreviewDir -Filter '*.PNG').Count
        outputFile = Split-Path -Leaf $OutputPath
    }
    $validation | ConvertTo-Json -Depth 4 |
        Set-Content -LiteralPath $ValidationPath -Encoding UTF8
    if ($validation.previewCount -ne 9) {
        throw "PowerPoint exported $($validation.previewCount) previews, expected 9"
    }
} finally {
    if ($presentation) {
        try { $presentation.Close() } catch {}
    }
    if ($powerPoint) {
        try { $powerPoint.Quit() } catch {}
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

Write-Output "PPTX_RESULT=PASS"
Write-Output "PPTX_SLIDES=9"
Write-Output "PPTX_OUTPUT=$OutputPath"
