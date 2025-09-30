# Unreal Engine Console Mod-Manager (Python)

**Mod Manager (Windows-first)** — простий текстовий інтерфейс для управління модами.

---

## ✨ Features

- 🔗 **Symlink Management**  
  - Uses `mklink` for creating symbolic links:  
    - Files → symbolic links  
    - Folders → junctions (`/J`)  
- ⚙️ **Config in JSON**  
  - Stored next to the script  
  - Defines:  
    - Game mods directory  
    - Mods source directory  
    - File types  
- 🔄 **Mod Operations**  
  - Apply / deactivate mods (create/remove links in game dir)  
  - Single **mods menu**:  
    - List & toggle (install/uninstall)  
    - Pagination (20 items per page: `p1`, `p2`, …)  
    - Multi-select via comma-separated indices  
- 📂 **Presets in JSON**  
  - Save current installed set  
  - Apply / deactivate presets  
  - Delete presets  
  - All actions from **one unified presets menu**  
- 🛠️ **Maintenance**  
  - Fix broken links (remove dead ones automatically)  

---

## ⚠️ Notes

- On **Windows**, creating symlinks may require **Administrator rights** or enabling **Developer Mode**.  
- Junctions (`/J`) for directories usually don’t require elevated permissions.  
- Linked names in the game directory always match the source file/folder names.  

---

## 🖥️ Text UI Preview

```text
Mod Manager (mklink) — Menu
========================================
1. Settings
2. Mods (list & toggle)
3. Presets (save/apply/toggle/delete)
4. Open mods SOURCE folder
5. Open GAME mods folder
6. Fix broken links (remove dead ones)
0. Exit

Select [0-6]:
