# MUMU 光标

Windows 桌面光标美化工具：把「小指针 + 人物主体」合成一张图装成**系统光标**，再在桌面上叠一层会甩的**装饰层**（连接线 + 悬挂物，带单摆物理）。

单文件 C# 5 + WinForms，用系统自带 `csc` 编译，零第三方依赖。

## 两条铁律

1. **永远不要用透明/近透明光标替换系统光标。** 曾经的实现把系统箭头换成全透明指针、靠覆盖层画假光标，一旦覆盖层出任何问题，屏幕上就一个光标都没有。现在系统光标永远是「① 小指针 + ② 主体」合成出来的真光标。
2. **所有换光标（`SetSystemCursor`）只能在 UI 线程做。** 渲染线程上调用会卡死（作者原注释见 `MainForm.Apply()`）。渲染线程只置标志位。

## 结构

- **系统光标**：`CursorSwitch.ApplyStatic()` → `CurArt.Compose()` 把指针和主体合成 N×N 图 → `WriteCurEx()` 写成 .cur → `SetBaseSize()` 再 `SetSystemCursor()`（顺序不能反，否则 `SPI_SETCURSORS` 会把刚换的光标冲掉）。
- **装饰层**：`Overlay.Run()` 一个独立线程 + 分层窗口，只画 ③ 连接线和 ④ 悬挂物；`CheckSysCursor()` 判定进全屏游戏时整层隐藏。
- **点击音效**：在渲染循环里、`SysCursorHidden` 分支**之前**处理，保证游戏里也有声音。
- **恢复**：`CursorSwitch.Restore()` + `%LOCALAPPDATA%\MUMUCursor\backup\`，外加三重保险（关窗自动恢复、启动时检查 `active.flag`、`恢复光标.bat`）。

## 编译

```bat
python build_exe.py
```

或手动（等价）：

```bat
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /target:winexe /optimize+ ^
  /out:MUMU光标.exe /win32icon:assets\app.ico ^
  /r:System.Drawing.dll /r:System.Windows.Forms.dll /r:System.Xaml.dll ^
  /r:C:\Windows\Microsoft.NET\Framework64\v4.0.30319\WPF\PresentationCore.dll ^
  /r:C:\Windows\Microsoft.NET\Framework64\v4.0.30319\WPF\WindowsBase.dll ^
  /resource:assets\body_default.png /resource:assets\body_avatar.png ^
  ... 其余 assets 下的 png/wav/cur ...
  MumuCursor.cs
```

注意是**老 csc（C# 5）**：不能用 `?.`、局部函数、`$"..."` 插值、`nameof`。

详细的目录说明、调试开关（`--test` / `--shot` / `--applystatic` 等）和踩坑记录见 [重建与调试说明.md](重建与调试说明.md)。

## 改代码的约定

- 只改 `MumuCursor.cs`；`assets/` 是素材，除非确实要换图，否则不要动。
- 不要重命名已有方法和字段（调试脚本、说明文档都按名字引用）。
- 改完请自己编译一遍，并至少验证：变身 → 桌面点击 → 进全屏 → 退出全屏 → 恢复，五步都正常。
- 提交 PR 时在描述里写清「改了哪个方法、为什么」。
