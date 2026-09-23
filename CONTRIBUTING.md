# Contributing to CleanPro

Thank you for contributing to CleanPro!

## Development Guidelines
- All code changes must adhere to `AGENTS.md` rules.
- Ensure `dotnet build CleanPro.sln` passes.
- Ensure `dotnet test CleanPro.sln` passes before creating a Pull Request.
- All file deletions MUST route through `QuarantineManager.MoveToQuarantineAsync()`.
- Bulk actions (Registry fixing, Drive Wiper, Health Check) MUST prompt or trigger System Restore Point creation via `IRestorePointService`.

## Pull Request Process
1. Create a branch prefixed with `jules/` or `feature/`.
2. Commit changes with clear, concise commit messages.
3. Open a Pull Request targeting `main`.
4. Continuous Integration will build and test your changes automatically.
