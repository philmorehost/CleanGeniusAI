namespace CleanPro.Core.Rules;

public enum RiskLevel
{
    Safe,
    Caution,
    Risky
}

public class SafetyGuard
{
    public static readonly IReadOnlyList<string> ProtectedPaths = new List<string>
    {
        @"C:\Windows\System32",
        @"C:\Windows\SysWOW64",
        @"C:\Windows\WinSxS",
        @"C:\Windows\Boot",
        @"C:\Program Files\WindowsApps"
    }.AsReadOnly();

    public static string NormalizePath(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
            return string.Empty;

        string normalized = path.Replace('/', '\\').TrimEnd('\\');
        return normalized;
    }

    public static bool IsProtected(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
            return true;

        string normalized = NormalizePath(path);

        foreach (var protectedPath in ProtectedPaths)
        {
            string normProtected = NormalizePath(protectedPath);
            if (normalized.Equals(normProtected, StringComparison.OrdinalIgnoreCase) ||
                normalized.StartsWith(normProtected + "\\", StringComparison.OrdinalIgnoreCase))
            {
                return true;
            }
        }

        return false;
    }

    public static RiskLevel ClassifyRisk(string path, string category)
    {
        if (IsProtected(path))
            return RiskLevel.Risky;

        if (string.Equals(category, "Registry", StringComparison.OrdinalIgnoreCase) ||
            string.Equals(category, "SystemDriver", StringComparison.OrdinalIgnoreCase))
        {
            return RiskLevel.Caution;
        }

        return RiskLevel.Safe;
    }
}
