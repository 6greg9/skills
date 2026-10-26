// CppSharp 綁定產生器範本
// 用法：dotnet add package CppSharp，然後依專案修改 Setup() 中的路徑與名稱。
using CppSharp;
using CppSharp.AST;
using CppSharp.Generators;
using CppSharp.Passes;

namespace MyLib.Gen;

public class MyLibrary : ILibrary
{
    // 依專案修改
    const string ModuleName = "MyLib";
    const string NativeLibName = "mylib";
    static readonly string IncludeDir = Path.GetFullPath("../native/include");
    static readonly string LibDir = Path.GetFullPath("../native/lib");

    public void Setup(Driver driver)
    {
        var options = driver.Options;
        options.GeneratorKind = GeneratorKind.CSharp;
        options.OutputDir = Path.GetFullPath("Generated");
        options.GenerateDefaultValuesForArguments = true;
        options.MarshalCharAsManagedChar = true;
        options.CheckSymbols = false;
        options.Verbose = true;

        var module = options.AddModule(ModuleName);
        module.SharedLibraryName = NativeLibName;
        module.IncludeDirs.Add(IncludeDir);
        module.Headers.Add("mylib.h");
        module.LibraryDirs.Add(LibDir);
        module.Libraries.Add($"{NativeLibName}.lib");

        var parser = driver.ParserOptions;
        parser.LanguageVersion = CppSharp.Parser.LanguageVersion.CPP17;
        // parser.AddDefines("MYLIB_EXPORTS");
    }

    public void SetupPasses(Driver driver)
    {
        // 例：C 風格名稱 → PascalCase
        // driver.Context.TranslationUnitPasses.RenameDeclsUpperCase(RenameTargets.Any);
    }

    public void Preprocess(Driver driver, ASTContext ctx)
    {
        // ctx.IgnoreHeadersWithName("internal.h");
        // ctx.SetClassAsValueType("Vector3");
        // ctx.GenerateEnumFromMacros("ErrorCode", "MYLIB_ERR_(.*)");
    }

    public void Postprocess(Driver driver, ASTContext ctx)
    {
    }
}

public static class Program
{
    public static void Main() => ConsoleDriver.Run(new MyLibrary());
}
