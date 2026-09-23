using CleanPro.Core.Rules;
using FluentAssertions;
using Xunit;

namespace CleanPro.Tests;

public class SafetyGuardTests
{
    [Theory]
    [InlineData(@"C:\Windows\System32")]
    [InlineData(@"C:\Windows\System32\drivers\etc\hosts")]
    [InlineData(@"C:\Windows\SysWOW64\cmd.exe")]
    [InlineData(@"C:\Program Files\WindowsApps\SomeApp")]
    public void IsProtected_ReturnsTrue_ForProtectedPaths(string path)
    {
        bool result = SafetyGuard.IsProtected(path);
        result.Should().BeTrue();
    }

    [Theory]
    [InlineData(@"C:\Users\TestUser\AppData\Local\Temp\junk.tmp")]
    [InlineData(@"C:\Temp\cache.log")]
    public void IsProtected_ReturnsFalse_ForNormalTempPaths(string path)
    {
        bool result = SafetyGuard.IsProtected(path);
        result.Should().BeFalse();
    }

    [Fact]
    [System.Diagnostics.CodeAnalysis.SuppressMessage("Assertions", "xUnit2013:Do not use boolean check assertion to check for enum value", Justification = "Testing RiskLevel classification")]
    public void ClassifyRisk_ReturnsRisky_ForProtectedPaths()
    {
        var risk = SafetyGuard.ClassifyRisk(@"C:\Windows\System32\file.dll", "Temp");
        risk.Should().Be(RiskLevel.Risky);
    }

    [Fact]
    [System.Diagnostics.CodeAnalysis.SuppressMessage("Assertions", "xUnit2013:Do not use boolean check assertion to check for enum value", Justification = "Testing RiskLevel classification")]
    public void ClassifyRisk_ReturnsCaution_ForRegistryCategory()
    {
        var risk = SafetyGuard.ClassifyRisk(@"C:\Users\TestUser\AppData\Local\Temp\test.reg", "Registry");
        risk.Should().Be(RiskLevel.Caution);
    }

    [Fact]
    [System.Diagnostics.CodeAnalysis.SuppressMessage("Assertions", "xUnit2013:Do not use boolean check assertion to check for enum value", Justification = "Testing RiskLevel classification")]
    public void ClassifyRisk_ReturnsSafe_ForStandardTempFiles()
    {
        var risk = SafetyGuard.ClassifyRisk(@"C:\Users\TestUser\AppData\Local\Temp\test.tmp", "TempFiles");
        risk.Should().Be(RiskLevel.Safe);
    }
}
