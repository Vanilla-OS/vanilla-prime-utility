<div align="center">
    <img src="data/icons/hicolor/scalable/apps/org.vanillaos.PrimeUtility.svg" height="64">
    <h1>Vanilla PRIME Utility</h1>
    <p>A frontend in GTK 4 and Libadwaita to switch PRIME profiles.</p>
    <br />
    <img src="data/screenshot.png">
</div>

## Build
### Dependencies
- build-essential
- meson
- libadwaita-1-dev
- gettext
- desktop-file-utils
- nvidia-prime

### Build
```bash
meson build
ninja -C build
```

### Install
```bash
sudo ninja -C build install
```

## Run
```bash
vanilla-prime-utility

# embedded mode
vanilla-prime-utility --embedded
```

## Other distributions
This utility works on any Ubuntu-based distribution, just note that `NoDisplay=true` is set
in the desktop file, since Vanilla OS uses the embedded mode. If you want to use the
standalone mode, you can remove this line and the icon will be shown in the applications
menu of your distribution.