# Unreal Engine console mod-manager (Python)

Mod Manager (Windows-first) — text interface for managing mods.

Features:

1. Create symlinks for mods using mklink (files — symbolic links, folders — junction /J)
2. Config stored in JSON (next to the script): game mods dir, mods source dir, file types
3. All operations use config
4. Apply/deactivate mods (create/remove links in game dir)
5. ONE mods menu: list & toggle (install/uninstall) with pagination & multi-select
6. Presets in JSON: save current installed set, toggle (apply/deactivate), and DELETE presets — all from ONE presets menu
7. Pagination by 20 items per page with p1, p2, ... navigation
8. Multi-select via comma-separated indices everywhere

Notes:

-   On Windows, creating symlinks may require Administrator rights or Developer Mode. Junctions (/J) for directories usually don’t.
-   Link names in game dir match source file/folder names.

## Text UI

#### Mod Manager (mklink) — Menu

========================================
   1. Settings
   2. Mods (list & toggle)
   3. Presets (save/apply/toggle/delete)
   4. Open mods SOURCE folder
   5. Open GAME mods folder
   6. Fix broken links (remove dead ones)
   7. Exit

Select [1-7]:

