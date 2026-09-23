using CleanPro.Core.Rules;

namespace CleanPro.Core.Quarantine;

public class QuarantineManager : IQuarantineManager
{
    public Task<string> MoveToQuarantineAsync(string filePath, string category, string sessionId)
    {
        if (SafetyGuard.IsProtected(filePath))
        {
            throw new InvalidOperationException($"Cannot quarantine protected path: {filePath}");
        }

        throw new NotImplementedException("Full QuarantineManager logic will be implemented in subsequent milestone.");
    }

    public Task RestoreItemAsync(int itemId)
    {
        throw new NotImplementedException("Full QuarantineManager logic will be implemented in subsequent milestone.");
    }

    public Task PurgeExpiredAsync()
    {
        throw new NotImplementedException("Full QuarantineManager logic will be implemented in subsequent milestone.");
    }
}
