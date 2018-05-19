# [Where is the DirectX SDK?](https://msdn.microsoft.com/en-us/library/windows/desktop/ee663275)
Starting with Windows 8, **the DirectX SDK is included as part of the Windows SDK.**

We originally created the DirectX SDK as a high-performance platform for game development on top of Windows. As DirectX technologies matured, they became relevant to a broader range of applications. Today, the availability of Direct3D hardware in computers drives even traditional desktop applications to use **graphics hardware acceleration**. In parallel, DirectX technologies are more integrated with Windows. _DirectX is now a fundamental part of Windows._
Because the Windows SDK is the primary developer SDK for Windows, DirectX is now included in it. You can now use the Windows SDK to build great games for Windows. To download the Windows 8 SDK, see Windows SDK and emulator archive.

The following technologies and tools, formerly part of the DirectX SDK, are now part of the Windows SDK:

### Windows Graphics Components
The headers and libraries for Direct3D and other Windows graphics APIs, like Direct2D, are available in the Windows SDK.

Note  D3DX is only available for download in previous versions of the DirectX SDK. The D3DCSX DirectCompute utility library is available in the Windows SDK.

### HLSL compiler (FXC.EXE)
The HLSL compiler is a tool in the appropriate architecture subdirectory under the bin folder in the Windows SDK.

Note  The D3DCompiler API is available in the Windows SDK.

### PIX for Windows
A replacement for the PIX for Windows tool is now a feature in Microsoft Visual Studio, called **Visual Studio Graphics Debugger**. This new feature has greatly improved usability, support for Windows 8, and Direct3D 11.1, and integration with traditional Microsoft Visual Studio features such as call stacks and debugging windows for HLSL debugging. For more info about this new feature, see [Debugging DirectX Graphics](https://docs.microsoft.com/en-us/previous-versions/visualstudio/visual-studio-2012/hh315751(v=vs.110)).

### XAudio2/XInput for Windows
now a system component in Windows 8. The headers and libraries in the Windows SDK.

### XNAMATH
The most recent version of XNAMATH, which is updated for Windows 8, is now **DirectXMath**. The headers for DirectXMath are available in the Windows SDK.

### DirectX Control Panel and DirectX Capabilities Viewer
The DirectX Control Panel and DirectX Capabilities Viewer utilities are included in the appropriate architecture subdirectory under the bin folder in the Windows SDK.

### XACT
no longer supported for use on Windows.

### Games Explorer and GDFMAKER
The Games Explorer API presents games to users of Windows. The Games Explorer API is supported only on Windows Vista and Windows 7. Use the Games Definition File Maker tool (GDFMAKER.EXE) to declare game ratings for Windows Store apps.

The Game Definition File Maker tool (GDFMaker.exe) is included in the x86 subdirectory under the bin folder in the Windows SDK, and supports both Windows Store apps and Win32 desktop applications.

Note  The Game Definition File Validator tool (gdftrace.exe) and Gameux Install Helper sample are both available in the MSDN Code Gallery.

### Samples
All new samples that highlight DirectX technologies on Windows are online in the [Windows SDK Samples Gallery](http://go.microsoft.com/fwlink/p/?LinkID=246562). Most samples for older versions of Direct3D are only available for download in previous versions of the DirectX SDK although a number of them are online as well. For more info about these samples, see DirectX SDK Samples Catalog.

### Managed DirectX 1.1
The .NET DirectX assemblies are deprecated and are not recommended for use by new applications. There are a number of alternatives available. See DirectX and .NET.

---
