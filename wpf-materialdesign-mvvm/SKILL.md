---
name: wpf-materialdesign-mvvm
description: Build or refactor a WPF project into a MaterialDesignInXaml MVVM practice shell. Use when a user wants a WPF app with MaterialDesignThemes, CommunityToolkit.Mvvm, Microsoft.Extensions.DependencyInjection, light/dark theme switching, a collapsible left navigation shell, ViewModel-only DI registration, and ContentControl-based page navigation using DataTemplates.
---

# WPF MaterialDesign MVVM

## Goal

Create a lightweight WPF architecture for practicing MaterialDesignInXaml:

- WPF owns `Window` and `UserControl` creation.
- DI owns ViewModels and Services only.
- `MainWindow` is a shell with fixed top bar, collapsible left navigation, and a central `ContentControl`.
- Page switching changes `CurrentViewModel`; XAML `DataTemplate`s map ViewModels to Views.
- MaterialDesign resources are loaded globally and UI colors use `DynamicResource`.

## Initial Setup

For a new WPF project, install:

```xml
<PackageReference Include="CommunityToolkit.Mvvm" Version="8.4.2" />
<PackageReference Include="MaterialDesignThemes" Version="5.3.2" />
<PackageReference Include="Microsoft.Extensions.DependencyInjection" Version="10.0.8" />
```

Create these folders:

```text
Converters/
Services/
ViewModels/
Views/
```

Use `MaterialDesign3.Defaults.xaml` for MaterialDesignThemes 5.x:

```xml
<Application x:Class="YourApp.App"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:local="clr-namespace:YourApp"
             xmlns:materialDesign="http://materialdesigninxaml.net/winfx/xaml/themes"
             StartupUri="MainWindow.xaml">
    <Application.Resources>
        <ResourceDictionary>
            <local:ViewModelLocator x:Key="Locator" />
            <ResourceDictionary.MergedDictionaries>
                <materialDesign:BundledTheme BaseTheme="Light"
                                             PrimaryColor="DeepPurple"
                                             SecondaryColor="Lime" />
                <ResourceDictionary Source="pack://application:,,,/MaterialDesignThemes.Wpf;component/Themes/MaterialDesign3.Defaults.xaml" />
            </ResourceDictionary.MergedDictionaries>
        </ResourceDictionary>
    </Application.Resources>
</Application>
```

Do not use `MaterialDesignTheme.Defaults.xaml` with this package line; it is not present in 5.3.2.

## DI Pattern

Keep DI intentionally narrow. Register Services and ViewModels, not `MainWindow` or Views.

```csharp
public partial class App : Application
{
    public static ServiceProvider ServiceProvider { get; private set; } = null!;

    public App()
    {
        ServiceProvider = ConfigureServices();
    }

    protected override void OnExit(ExitEventArgs e)
    {
        ServiceProvider.Dispose();
        base.OnExit(e);
    }

    private static ServiceProvider ConfigureServices()
    {
        var services = new ServiceCollection();

        services.AddSingleton<INavigationService, NavigationService>();
        services.AddSingleton<MainWindowViewModel>();
        services.AddSingleton<DashboardViewModel>();
        services.AddSingleton<AnalyticsViewModel>();
        services.AddSingleton<CustomersViewModel>();
        services.AddSingleton<TasksViewModel>();
        services.AddSingleton<SettingsViewModel>();

        return services.BuildServiceProvider();
    }
}
```

Expose the root VM through a locator:

```csharp
public class ViewModelLocator
{
    public MainWindowViewModel MainWindowVM
        => App.ServiceProvider.GetRequiredService<MainWindowViewModel>();
}
```

Then bind `MainWindow`:

```xml
DataContext="{Binding MainWindowVM, Source={StaticResource Locator}}"
```

## Navigation

Use a service that stores the active ViewModel:

```csharp
public interface INavigationService
{
    ObservableObject? CurrentViewModel { get; }
    event EventHandler? CurrentViewModelChanged;
    void NavigateTo<TViewModel>() where TViewModel : ObservableObject;
}
```

```csharp
public class NavigationService : INavigationService
{
    private readonly IServiceProvider serviceProvider;

    public NavigationService(IServiceProvider serviceProvider)
    {
        this.serviceProvider = serviceProvider;
    }

    public ObservableObject? CurrentViewModel { get; private set; }
    public event EventHandler? CurrentViewModelChanged;

    public void NavigateTo<TViewModel>() where TViewModel : ObservableObject
    {
        CurrentViewModel = serviceProvider.GetRequiredService<TViewModel>();
        CurrentViewModelChanged?.Invoke(this, EventArgs.Empty);
    }
}
```

`MainWindowViewModel` should:

- inherit `ObservableObject`
- expose `CurrentViewModel`
- call `NavigateTo<DashboardViewModel>()` at startup
- provide `[RelayCommand]` methods for left navigation
- track `CurrentPageKey` for selected nav styling
- expose `IsNavigationExpanded` and `ToggleNavigationCommand`
- expose `IsDarkTheme` and `ToggleThemeCommand`

Theme switching:

```csharp
private void ApplyTheme()
{
    var paletteHelper = new PaletteHelper();
    var theme = paletteHelper.GetTheme();

    theme.SetBaseTheme(IsDarkTheme ? BaseTheme.Dark : BaseTheme.Light);
    paletteHelper.SetTheme(theme);
}
```

## Shell Layout

Use `MainWindow` as a stable shell:

```text
MainWindow
+- Left navigation, collapsible
+- Top bar, fixed
+- ContentControl bound to CurrentViewModel
```

Define VM-to-View templates in `MainWindow.Resources`:

```xml
<DataTemplate DataType="{x:Type vm:DashboardViewModel}">
    <views:DashboardView />
</DataTemplate>

<DataTemplate DataType="{x:Type vm:AnalyticsViewModel}">
    <views:PlaceholderView />
</DataTemplate>
```

Central content:

```xml
<ContentControl Grid.Row="1"
                Margin="28"
                Content="{Binding CurrentViewModel}" />
```

Left nav buttons should bind commands:

```xml
<Button Command="{Binding NavigateDashboardCommand}"
        ToolTip="Home">
    <StackPanel Orientation="Horizontal">
        <materialDesign:PackIcon Kind="HomeOutline" Width="22" Height="22" />
        <TextBlock Text="Home" />
    </StackPanel>
</Button>
```

For collapsed navigation, bind sidebar width to a boolean converter:

```csharp
public class BooleanToDoubleConverter : IValueConverter
{
    public double TrueValue { get; set; }
    public double FalseValue { get; set; }

    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        => value is true ? TrueValue : FalseValue;

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        => value is double number && Math.Abs(number - TrueValue) < Math.Abs(number - FalseValue);
}
```

Use the top-left brand icon as the navigation toggle so it remains visible when collapsed.

## MaterialDesign Resources

Prefer `DynamicResource` over fixed colors so dark mode works. Common keys in MaterialDesignThemes 5.3.2:

```xml
Background="{DynamicResource MaterialDesign.Brush.Background}"
Background="{DynamicResource MaterialDesign.Brush.Card.Background}"
BorderBrush="{DynamicResource MaterialDesign.Brush.Card.Border}"
Foreground="{DynamicResource MaterialDesign.Brush.Foreground}"
Foreground="{DynamicResource MaterialDesign.Brush.ForegroundLight}"
Foreground="{DynamicResource MaterialDesign.Brush.Primary}"
Background="{DynamicResource MaterialDesign.Brush.Primary.Dark}"
Foreground="{DynamicResource MaterialDesign.Brush.Primary.Dark.Foreground}"
Background="{DynamicResource MaterialDesign.Brush.Primary.Light}"
Foreground="{DynamicResource MaterialDesign.Brush.Primary.Light.Foreground}"
```

Avoid hard-coded `White`, dark text, card borders, and page backgrounds in Views. Keep fixed colors only when deliberately designing a brand accent that should not react to theme changes.

## Recommended File Shape

```text
Converters/
+- BooleanToDoubleConverter.cs

Services/
+- INavigationService.cs
+- NavigationService.cs

ViewModels/
+- MainWindowViewModel.cs
+- DashboardViewModel.cs
+- AnalyticsViewModel.cs
+- CustomersViewModel.cs
+- TasksViewModel.cs
+- SettingsViewModel.cs

Views/
+- DashboardView.xaml
+- DashboardView.xaml.cs
+- PlaceholderView.xaml
+- PlaceholderView.xaml.cs
```

Keep `Views/Pages` only if the app intentionally uses `Frame`/`Page`. For this shell pattern, prefer `UserControl` Views with `ContentControl`.

## Validation

Run:

```powershell
dotnet build
dotnet run --no-build
```

If `dotnet run` times out because the WPF window stays open, stop the app process after confirming it launched:

```powershell
Get-Process WpfAppMaterialDesign -ErrorAction SilentlyContinue | Stop-Process -Force
```
