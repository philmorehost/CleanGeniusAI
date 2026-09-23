namespace CleanPro.Core.Advanced;

public interface IRestorePointService
{
    Task<bool> CreateRestorePointAsync(string description);
    Task<IEnumerable<string>> ListRestorePointsAsync();
    Task<bool> RestoreToPointAsync(int sequenceNumber);
    Task<bool> IsSystemRestoreEnabledAsync();
}
