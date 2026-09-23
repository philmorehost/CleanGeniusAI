# CleanPro

Windows disk cleanup utility with deep scan, safe quarantine-based removal, restore capability, and full CCleaner Pro feature parity — no monetization tiers, fully open.

## Key Features

- **Custom Clean**: Fast scanning and cleaning of temp files, caches, and system junk (`Cleanup.CustomClean`)
- **Registry Cleaner**: Read-only scan with mandatory `.reg` backup before applying fixes (`Cleanup.RegistryCleaner`)
- **System Restore Point Integration**: Pre-fix system restore point creation layer (`Advanced.RestorePointManager`)
- **Quarantine & Safety Guard**: No direct permanent file deletions; all removals route through Quarantine with protected path checks (`Quarantine.RestoreManager`, `Rules.SafetyGuard`)
- **Health Check & Smart Cleaning**: 1-click system diagnostic and cleanup (`Automation.HealthCheck`)
- **Software Updater & Startup Manager**: Program uninstallers, startup item controls, and update checker (`Optimize.StartupManager`, `Updater.SoftwareUpdater`)
- **Disk Analyzer & Duplicate Finder**: Visual disk space usage and xxHash/SHA256 duplicate detection (`Analysis.DiskAnalyzer`, `Analysis.DuplicateFinder`)
- **Drive Wiper**: Secure free-space wipe (`Advanced.DriveWiper`)
- **File Recovery**: Deleted file scan and undelete (`Recovery.FileRecovery`)
- **Dev Cache Cleaner**: Target developer caches including `node_modules`, `__pycache__`, `.pytest_cache`, IDE caches, and package manager stores (`Cleanup.DevCacheCleaner`)

## Tech Stack

- **Runtime**: .NET 8 (C#)
- **UI**: WPF (MVVM with `CommunityToolkit.Mvvm`)
- **Database**: SQLite (`Microsoft.Data.Sqlite`)
- **Installer**: WiX Toolset v4
- **Testing**: xUnit + FluentAssertions
- **CI/CD**: GitHub Actions

## Building and Testing

To build the solution:
```bash
dotnet build CleanPro.sln
```

To run unit tests:
```bash
dotnet test CleanPro.sln
```

## Safety & Contribution Guidelines

For safety rules, quarantine specifications, and AI developer agent instructions, see [AGENTS.md](AGENTS.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

## License

CleanPro is licensed under the [MIT License](LICENSE).
