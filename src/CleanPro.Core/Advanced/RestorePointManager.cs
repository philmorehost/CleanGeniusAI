namespace CleanPro.Core.Advanced;

public class RestorePointManager : IRestorePointService
{
    public Task<bool> CreateRestorePointAsync(string description)
    {
        throw new NotImplementedException("System Restore Point creation via WMI/PowerShell will be implemented in subsequent milestone.");
    }

    public Task<IEnumerable<string>> ListRestorePointsAsync()
    {
        throw new NotImplementedException("System Restore Point enumeration will be implemented in subsequent milestone.");
    }

    public Task<bool> RestoreToPointAsync(int sequenceNumber)
    {
        throw new NotImplementedException("System Restore execution will be implemented in subsequent milestone.");
    }

    public Task<bool> IsSystemRestoreEnabledAsync()
    {
        throw new NotImplementedException("System Restore status check will be implemented in subsequent milestone.");
    }
}
