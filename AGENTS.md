# Agent Instructions for CleanPro

## Build & Test
- Build: `dotnet build CleanPro.sln`
- Test: `dotnet test CleanPro.sln`
- All PRs must pass `dotnet test` before merge.

## Safety Rules (NON-NEGOTIABLE)
- Never write code that permanently deletes a file directly.
  All deletions MUST go through `QuarantineManager.MoveToQuarantineAsync()`.
- Any bulk operation (Registry Cleaner batch fix, Drive Wiper, Health Check auto-fix) MUST call `IRestorePointService.CreateRestorePointAsync()` before execution. This is in addition to, not a replacement for, `QuarantineManager`.
- Any change to `Cleanup/RegistryCleaner/*` or `Advanced/DriveWiper/*` must include: (a) a unit test, (b) a dry-run mode, (c) update to `SafetyGuard.ProtectedPaths`.
- Do not touch files under `%SystemRoot%\System32` in any test or code path.
- Every new cleanup category must be added via `config/cleanup-rules.json`, not hardcoded paths in C#.

## Style
- Follow MVVM strictly: no business logic in code-behind (.xaml.cs).
- Use async/await for all I/O.
- Add XML doc comments to public methods.

## Task Workflow
- Each issue maps to one PR.
- Keep PRs scoped to a single module/folder when possible.
- Update CHANGELOG.md with every PR.
