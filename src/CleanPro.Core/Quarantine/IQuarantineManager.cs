namespace CleanPro.Core.Quarantine;

public interface IQuarantineManager
{
    Task<string> MoveToQuarantineAsync(string filePath, string category, string sessionId);
    Task RestoreItemAsync(int itemId);
    Task PurgeExpiredAsync();
}
