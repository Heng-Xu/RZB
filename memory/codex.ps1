<#
.SYNOPSIS
  Export local OpenAI Codex session transcripts to Markdown on Windows.

.DESCRIPTION
  Reads Codex JSONL session files from CODEX_HOME (default: %USERPROFILE%\.codex).
  This script is fully local: it does not call Codex, OpenAI APIs, or consume quota.

.EXAMPLES
  # Export the latest active session
  .\Export-CodexChats.ps1

  # Export all active sessions
  .\Export-CodexChats.ps1 -All

  # Export active and archived sessions
  .\Export-CodexChats.ps1 -All -IncludeArchived

  # Export sessions updated within the last 30 days (-Days implies -All)
  .\Export-CodexChats.ps1 -Days 30

  # Export one specified rollout JSONL file
  .\Export-CodexChats.ps1 -InputPath "C:\Users\you\.codex\sessions\2026\07\31\rollout-xxx.jsonl"

  # Also copy the original JSONL files
  .\Export-CodexChats.ps1 -All -BackupRaw
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$InputPath,

    [string]$OutputDir = (Join-Path ([Environment]::GetFolderPath("Desktop")) "Codex-Export"),

    [switch]$All,

    # Only export sessions whose file was last written within the past N days.
    # Implies -All for the matched range.
    [int]$Days = 0,

    [switch]$IncludeArchived,

    [switch]$BackupRaw
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-CodexHome {
    if (-not [string]::IsNullOrWhiteSpace($env:CODEX_HOME)) {
        return $env:CODEX_HOME
    }
    return (Join-Path $HOME ".codex")
}

function Get-TextFromContent {
    param([object]$Content)

    $parts = New-Object System.Collections.Generic.List[string]
    foreach ($item in @($Content)) {
        if ($null -eq $item) { continue }

        $type = if ($item.PSObject.Properties.Name -contains "type") {
            [string]$item.type
        } else {
            ""
        }

        if ($type -in @("input_text", "output_text", "text")) {
            if ($item.PSObject.Properties.Name -contains "text" -and
                -not [string]::IsNullOrWhiteSpace([string]$item.text)) {
                $parts.Add([string]$item.text)
            }
        }
    }
    return ($parts -join "`n")
}

function Test-RuntimeNoise {
    # Detect IDE/runtime-injected pseudo-user messages. Sessions recorded with
    # disable_response_storage lack event_msg/user_message records, so user text
    # falls back to response_item entries which can carry environment context.
    param([string]$Text)

    if ([string]::IsNullOrWhiteSpace($Text)) { return $true }
    $stripped = $Text.TrimStart()
    return ($stripped.StartsWith("<environment_context>") -or
            $stripped.StartsWith("<user_instructions>") -or
            $stripped.StartsWith("<INSTRUCTIONS>") -or
            $stripped.StartsWith("# AGENTS.md instructions") -or
            $Text.Contains("<environment_context>") -or
            $Text.Contains("<turn_aborted>"))
}

function Convert-CodexSessionToMarkdown {
    param(
        [Parameter(Mandatory = $true)]
        [System.IO.FileInfo]$File,

        [Parameter(Mandatory = $true)]
        [string]$DestinationDirectory
    )

    $records = New-Object System.Collections.Generic.List[object]
    $lineNumber = 0

    foreach ($line in [System.IO.File]::ReadLines($File.FullName)) {
        $lineNumber++
        if ([string]::IsNullOrWhiteSpace($line)) { continue }

        try {
            $record = $line | ConvertFrom-Json
            $records.Add($record)
        }
        catch {
            Write-Warning "Skipped malformed JSON at $($File.FullName):$lineNumber"
        }
    }

    if ($records.Count -eq 0) {
        Write-Warning "No readable JSON records found: $($File.FullName)"
        return
    }

    $sessionId = ""
    $cwd = ""
    $sessionTimestamp = ""
    $threadTitle = ""

    foreach ($record in $records) {
        if ([string]$record.type -eq "session_meta") {
            $payload = $record.payload
            if ($payload) {
                if ($payload.PSObject.Properties.Name -contains "id") {
                    $sessionId = [string]$payload.id
                } elseif ($payload.PSObject.Properties.Name -contains "session_id") {
                    $sessionId = [string]$payload.session_id
                }

                if ($payload.PSObject.Properties.Name -contains "cwd") {
                    $cwd = [string]$payload.cwd
                }

                if ($payload.PSObject.Properties.Name -contains "timestamp") {
                    $sessionTimestamp = [string]$payload.timestamp
                }
            }
            if ([string]::IsNullOrWhiteSpace($sessionTimestamp) -and
                $record.PSObject.Properties.Name -contains "timestamp") {
                $sessionTimestamp = [string]$record.timestamp
            }
            break
        }
    }

    # Prefer event_msg/user_message for user text because response_item/user can
    # contain IDE/runtime context that the user did not type.
    $hasUserEvents = $false
    $hasAssistantResponses = $false

    foreach ($record in $records) {
        if ([string]$record.type -eq "event_msg" -and
            $record.payload -and
            [string]$record.payload.type -eq "user_message") {
            $hasUserEvents = $true
        }

        if ([string]$record.type -eq "response_item" -and
            $record.payload -and
            [string]$record.payload.type -eq "message" -and
            [string]$record.payload.role -eq "assistant") {
            $hasAssistantResponses = $true
        }
    }

    $messages = New-Object System.Collections.Generic.List[object]

    foreach ($record in $records) {
        $recordType = [string]$record.type
        $timestamp = if ($record.PSObject.Properties.Name -contains "timestamp") {
            [string]$record.timestamp
        } else {
            ""
        }

        if ($recordType -eq "event_msg" -and $record.payload) {
            $eventType = [string]$record.payload.type

            if ($eventType -eq "user_message") {
                $text = if ($record.payload.PSObject.Properties.Name -contains "message") {
                    [string]$record.payload.message
                } else {
                    ""
                }

                if (-not [string]::IsNullOrWhiteSpace($text) -and
                    -not (Test-RuntimeNoise $text)) {
                    $messages.Add([pscustomobject]@{
                        Timestamp = $timestamp
                        Role      = "用户"
                        Text      = $text.Trim()
                    })
                }
            }
            elseif (-not $hasAssistantResponses -and $eventType -eq "agent_message") {
                $text = if ($record.payload.PSObject.Properties.Name -contains "message") {
                    [string]$record.payload.message
                } else {
                    ""
                }

                if (-not [string]::IsNullOrWhiteSpace($text)) {
                    $messages.Add([pscustomobject]@{
                        Timestamp = $timestamp
                        Role      = "Codex"
                        Text      = $text.Trim()
                    })
                }
            }

            if ($eventType -in @("thread_name_updated", "thread_title_updated")) {
                foreach ($nameField in @("name", "title", "thread_name")) {
                    if ($record.payload.PSObject.Properties.Name -contains $nameField) {
                        $candidate = [string]$record.payload.$nameField
                        if (-not [string]::IsNullOrWhiteSpace($candidate)) {
                            $threadTitle = $candidate.Trim()
                            break
                        }
                    }
                }
            }
        }
        elseif ($recordType -eq "response_item" -and $record.payload) {
            if ([string]$record.payload.type -ne "message") { continue }

            $role = [string]$record.payload.role
            if ($role -eq "assistant" -or ($role -eq "user" -and -not $hasUserEvents)) {
                $text = Get-TextFromContent -Content $record.payload.content
                if (-not [string]::IsNullOrWhiteSpace($text) -and
                    -not (Test-RuntimeNoise $text)) {
                    $messages.Add([pscustomobject]@{
                        Timestamp = $timestamp
                        Role      = if ($role -eq "assistant") { "Codex" } else { "用户" }
                        Text      = $text.Trim()
                    })
                }
            }
        }
    }

    # Remove exact adjacent duplicates sometimes emitted by multiple Codex surfaces.
    $deduped = New-Object System.Collections.Generic.List[object]
    $previousKey = $null
    foreach ($message in $messages) {
        $key = "$($message.Role)`n$($message.Text)"
        if ($key -ne $previousKey) {
            $deduped.Add($message)
        }
        $previousKey = $key
    }

    if ([string]::IsNullOrWhiteSpace($threadTitle)) {
        $firstUser = $deduped | Where-Object { $_.Role -eq "用户" } | Select-Object -First 1
        if ($firstUser) {
            $singleLine = ($firstUser.Text -replace "\s+", " ").Trim()
            $threadTitle = if ($singleLine.Length -gt 60) {
                $singleLine.Substring(0, 60) + "…"
            } else {
                $singleLine
            }
        }
    }

    if ([string]::IsNullOrWhiteSpace($threadTitle)) {
        $threadTitle = "Codex 会话"
    }

    New-Item -ItemType Directory -Force -Path $DestinationDirectory | Out-Null

    $safeId = if ([string]::IsNullOrWhiteSpace($sessionId)) {
        [System.IO.Path]::GetFileNameWithoutExtension($File.Name)
    } else {
        $sessionId
    }

    $datePrefix = $File.LastWriteTime.ToString("yyyy-MM-dd_HHmmss")
    $outputName = "$datePrefix-$safeId.md"
    foreach ($invalid in [System.IO.Path]::GetInvalidFileNameChars()) {
        $outputName = $outputName.Replace($invalid, "_")
    }
    $outputPath = Join-Path $DestinationDirectory $outputName

    $builder = New-Object System.Text.StringBuilder
    [void]$builder.AppendLine("# $threadTitle")
    [void]$builder.AppendLine()
    [void]$builder.AppendLine("- 会话 ID：``$safeId``")
    if (-not [string]::IsNullOrWhiteSpace($sessionTimestamp)) {
        [void]$builder.AppendLine("- 会话时间：$sessionTimestamp")
    }
    if (-not [string]::IsNullOrWhiteSpace($cwd)) {
        [void]$builder.AppendLine("- 工作目录：``$cwd``")
    }
    [void]$builder.AppendLine("- 原始文件：``$($File.FullName)``")
    [void]$builder.AppendLine("- 导出时间：$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')")
    [void]$builder.AppendLine()
    [void]$builder.AppendLine("---")
    [void]$builder.AppendLine()

    foreach ($message in $deduped) {
        $heading = "## $($message.Role)"
        if (-not [string]::IsNullOrWhiteSpace($message.Timestamp)) {
            $heading += " · $($message.Timestamp)"
        }
        [void]$builder.AppendLine($heading)
        [void]$builder.AppendLine()
        [void]$builder.AppendLine($message.Text)
        [void]$builder.AppendLine()
    }

    [System.IO.File]::WriteAllText(
        $outputPath,
        $builder.ToString(),
        [System.Text.UTF8Encoding]::new($false)
    )

    if ($BackupRaw) {
        $rawDir = Join-Path $DestinationDirectory "raw-jsonl"
        New-Item -ItemType Directory -Force -Path $rawDir | Out-Null
        Copy-Item -LiteralPath $File.FullName -Destination $rawDir -Force
    }

    Write-Host "Exported: $outputPath"
}

$codexHome = Get-CodexHome

if (-not (Test-Path -LiteralPath $codexHome)) {
    throw "Codex home directory not found: $codexHome"
}

$files = @()

if (-not [string]::IsNullOrWhiteSpace($InputPath)) {
    $resolved = Resolve-Path -LiteralPath $InputPath
    $item = Get-Item -LiteralPath $resolved
    if ($item.PSIsContainer) {
        $files = @(Get-ChildItem -LiteralPath $item.FullName -Recurse -File -Filter "*.jsonl")
    } else {
        $files = @($item)
    }
}
else {
    $searchRoots = New-Object System.Collections.Generic.List[string]

    $activeRoot = Join-Path $codexHome "sessions"
    if (Test-Path -LiteralPath $activeRoot) {
        $searchRoots.Add($activeRoot)
    }

    if ($IncludeArchived) {
        $archivedRoot = Join-Path $codexHome "archived_sessions"
        if (Test-Path -LiteralPath $archivedRoot) {
            $searchRoots.Add($archivedRoot)
        }
    }

    foreach ($root in $searchRoots) {
        $files += Get-ChildItem -LiteralPath $root -Recurse -File -Filter "rollout-*.jsonl"
    }

    $files = @($files | Sort-Object LastWriteTime -Descending)

    if ($Days -gt 0) {
        $cutoff = (Get-Date).AddDays(-$Days)
        $files = @($files | Where-Object { $_.LastWriteTime -ge $cutoff })
    }

    if (-not $All -and $Days -le 0 -and $files.Count -gt 0) {
        $files = @($files[0])
    }
}

if ($files.Count -eq 0) {
    throw "No Codex session JSONL files found under: $codexHome"
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

foreach ($file in $files) {
    try {
        Convert-CodexSessionToMarkdown -File $file -DestinationDirectory $OutputDir
    }
    catch {
        Write-Warning "Failed to export $($file.FullName): $($_.Exception.Message)"
    }
}

Write-Host ""
Write-Host "Done. Output directory: $OutputDir"
