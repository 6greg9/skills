---
name: cppsharp
description: 使用 CppSharp 從 C/C++ 標頭檔自動產生 C# (P/Invoke) 或 C++/CLI 綁定。當使用者提到 CppSharp、要把 C/C++ DLL/函式庫包成 .NET/C# 可呼叫的 API、撰寫 ILibrary 綁定產生器、設定 CppSharp 的 Driver/Module/Pass，或排除 CppSharp 產生/編譯/執行期錯誤（找不到 symbol、parser 失敗、x86/x64 不符、template/inline 函式缺失）時使用。Use for any C++ → C# interop binding generation with CppSharp.
---

# CppSharp 綁定產生 Skill

CppSharp 用 Clang 解析 C/C++ 標頭檔，產生 C#（P/Invoke + 原生記憶體配置）或 C++/CLI 包裝程式碼。
典型流程：**寫一個產生器 Console 專案 → 執行產生 .cs → 把 .cs 放入正式的 C# 類別庫 → 執行時載入原生 DLL**。

## 1. 開工前先確認

向使用者（或從專案中）確認以下資訊，缺什麼就問：

| 項目 | 為什麼重要 |
|---|---|
| 目標是 C# (P/Invoke) 還是 C++/CLI | 決定 `GeneratorKind`；C++/CLI 只能在 Windows + MSVC 編譯 |
| 標頭檔清單與 include 路徑 | `module.Headers` / `module.IncludeDirs` |
| 原生函式庫名稱（.dll/.so/.dylib）與 .lib 位置 | `module.SharedLibraryName`、`LibraryDirs`、`Libraries`（啟用 `CheckSymbols` 時需要） |
| 平台架構（x64 / arm64） | 產生器程式、原生 DLL、最終 C# 程式三者架構必須一致 |
| C++ 標準與必要的 #define | `ParserOptions.LanguageVersion`、`AddDefines` |
| 是否大量使用 template / inline / STL | 需要額外編譯 Symbols 原生庫（見第 5 節） |

## 2. 建立產生器專案

```bash
dotnet new console -n MyLib.Gen
cd MyLib.Gen
dotnet add package CppSharp
```

`.csproj` 必須指定平台（CppSharp 內含原生 `CppSharp.CppParser.dll`，AnyCPU 會在載入時失敗）：

```xml
<PropertyGroup>
  <OutputType>Exe</OutputType>
  <TargetFramework>net8.0</TargetFramework>
  <PlatformTarget>x64</PlatformTarget>
  <RuntimeIdentifier>win-x64</RuntimeIdentifier>
</PropertyGroup>
```

套件版本請以 `dotnet add package` 取得的最新版為準；若專案已有版本就沿用，不要擅自升級。

## 3. 撰寫 ILibrary

完整範本見 [templates/BindingGenerator.cs](templates/BindingGenerator.cs)。四個生命週期方法：

- `Setup(Driver)`：設定輸出、模組、標頭檔、parser 選項（**必寫**）
- `SetupPasses(Driver)`：加入自訂或內建 Pass（例如命名規則）
- `Preprocess(Driver, ASTContext)`：產生前修改 AST——忽略、改名、把巨集轉 enum、把 class 設為 value type
- `Postprocess(Driver, ASTContext)`：產生後的最終調整

進入點：`ConsoleDriver.Run(new MyLibrary());`

### 常用設定速查

```csharp
var options = driver.Options;
options.GeneratorKind = GeneratorKind.CSharp;     // 或 GeneratorKind.CLI
options.OutputDir = "Generated";
options.GenerateDefaultValuesForArguments = true;
options.MarshalCharAsManagedChar = true;          // char → C# char
options.CheckSymbols = false;                     // true 時會檢查 DLL 匯出符號，需設定 LibraryDirs/Libraries
options.Verbose = true;

var module = options.AddModule("MyLib");          // 產生的 namespace / 檔名
module.SharedLibraryName = "mylib";               // DllImport 使用的名稱
module.IncludeDirs.Add(@"C:\path\to\include");
module.Headers.Add("mylib.h");
module.LibraryDirs.Add(@"C:\path\to\lib");
module.Libraries.Add("mylib.lib");

var parser = driver.ParserOptions;
parser.LanguageVersion = CppSharp.Parser.LanguageVersion.CPP17;
parser.AddDefines("MYLIB_EXPORTS");
// parser.TargetTriple = "x86_64-pc-win32-msvc";
```

### Preprocess 常用操作（ASTContext 擴充方法）

```csharp
ctx.IgnoreHeadersWithName("internal_detail.h");
ctx.IgnoreClassWithName("PrivateImpl");
ctx.IgnoreFunctionWithName("debug_dump");
ctx.SetClassAsValueType("Vector3");                    // 產生 struct 而非 class
ctx.GenerateEnumFromMacros("ErrorCode", "ERR_(.*)");   // #define 常數 → enum（regex）
ctx.SetNameOfEnumWithMatchingItem("FLAG_A", "Flags");  // 為匿名 enum 命名
```

## 4. 執行與整合

1. `dotnet run -c Release` 執行產生器，輸出在 `OutputDir`（通常是 `MyLib.cs`，可能還有 `Std.cs`、`MyLib-symbols.cpp`）。
2. 讀產生的 log——**Warning 也要看**，被跳過的宣告會列在裡面。
3. 建立正式的 C# 類別庫，加入產生的 `.cs`，並設定：
   - `<AllowUnsafeBlocks>true</AllowUnsafeBlocks>`（產生的程式碼使用 unsafe）
   - 與原生 DLL 相同的 `PlatformTarget`
4. 把原生 DLL 複製到輸出目錄（或用 `NativeLibrary.SetDllImportResolver` 指定路徑）。
5. 寫一個最小的測試呼叫，確認能真正載入並執行，而不只是能編譯。

建議把產生器做成可重複執行的步驟（script 或 MSBuild target），標頭更新時重新產生，**不要手改產生的 .cs**——需要調整就寫到 Preprocess/Pass 裡。

## 5. Template、inline 與 STL

C++ 的 template 實例、inline 函式、隱式產生的建構/解構子在原生 DLL 中可能沒有匯出符號。CppSharp 會產生 `<Module>-symbols.cpp`：

- 用與原函式庫相同的編譯器與設定，把它編譯成一個額外的原生 DLL（例如 `MyLib-symbols.dll`）並連結原函式庫。
- 執行時與原生 DLL 放在一起。
- 若不需要這些 API，可在 Preprocess 中忽略相關 class/function，避免額外編譯。

`std::string`、`std::vector` 等 STL 型別的支援因平台/ABI 而異；能改 API 的話，優先在 C++ 側提供 C 風格介面（`const char*`、指標 + 長度）。

## 6. 疑難排解

| 症狀 | 可能原因與處理 |
|---|---|
| `DllNotFoundException: CppSharp.CppParser` / `BadImageFormatException` | 產生器專案是 AnyCPU 或 x86 → 設 `PlatformTarget=x64` |
| Parser 錯誤：找不到 `stddef.h` 等內建標頭 | NuGet 輸出目錄缺少 `lib/clang/...` 內建標頭，確認套件的 content 有被複製；或沒裝 MSVC/Windows SDK（Windows 下 CppSharp 依賴它們找系統標頭） |
| Parser 錯誤：找不到專案標頭 | 補 `module.IncludeDirs`；檢查巨集條件是否需要 `AddDefines` |
| 執行期 `EntryPointNotFoundException` | 函式未匯出（缺 `__declspec(dllexport)`）、inline/template 符號 → 第 5 節；或啟用 `CheckSymbols` 讓產生器自動過濾 |
| 執行期 `DllNotFoundException`（你的函式庫） | `SharedLibraryName` 與實際檔名不符，或 DLL 及其相依 DLL 不在搜尋路徑 |
| `BadImageFormatException`（你的函式庫） | C# 程式與原生 DLL 架構不一致 |
| 某些宣告沒有被產生 | 看產生 log；常見原因：使用了不支援的型別、在被忽略的標頭中、或被 `CheckSymbols` 過濾 |
| 字串亂碼 | 檢查 `MarshalCharAsManagedChar`，以及 C++ 端是 UTF-8 還是 `wchar_t` |
| 記憶體洩漏 / 雙重釋放 | 產生的類別實作 `IDisposable`；釐清所有權——由 C# 建立的物件要 `Dispose`，C++ 回傳、由 C++ 擁有的物件不要釋放 |

排錯時優先：開 `options.Verbose = true`、讀完整 log、用最小標頭重現問題。

## 7. 交付前檢查

- [ ] 產生器可重複執行，且路徑沒有寫死在個人機器上（或已集中在設定處）
- [ ] 產生的 log 沒有未處理的 Error，Warning 已檢視
- [ ] C# 類別庫可編譯，平台設定一致
- [ ] 最小測試能實際呼叫原生函式並得到正確結果
- [ ] 需要的 symbols DLL 已編譯並與原生 DLL 一起部署
