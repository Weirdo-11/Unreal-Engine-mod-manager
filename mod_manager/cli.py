from __future__ import annotations

import argparse
from typing import Callable, Dict, List

from app_paths import APP_NAME, APP_VERSION

from . import settings_schema
from .cli_utils import ensure_paths, open_folder, parse_multi_choice
from .mods import (
    add_favorites_to_mods,
    add_label_to_mods,
    apply_mods_page,
    deactivate_mod,
    deactivate_mods_page,
    existing_targets,
    is_copy_install,
    list_broken_links,
    mods_by_indexes,
    mods_view,
    overwrite_message,
    remove_favorites_from_mods,
    remove_label_from_mods,
    toggle_mods_by_indexes,
)
from .presets import (
    delete_presets_by_indexes,
    preset_mods_to_install,
    preset_names_by_indexes,
    presets_view,
    save_preset_from_installed,
    toggle_presets_by_indexes,
)
from .storage import (
    GAME_PROFILE_KEYS,
    create_game_profile,
    delete_game_profile,
    game_abbreviation,
    load_config,
    save_config,
    set_active_game_profile,
    update_game_profile,
)

def _indexes(value: str) -> List[int]:
    return parse_multi_choice(value or "")

def _order(value: str) -> str:
    v = (value or "d").strip().lower()
    aliases = {
        "d": "default",
        "default": "default",
        "default desc": "-default",
        "cd": "created_date",
        "created date": "created_date",
        "created_date": "created_date",
        "created date desc": "-created_date",
        "created_date desc": "-created_date",
        "name": "name",
        "name desc": "-name",
        "label": "label",
        "label desc": "-label",
        "installed": "installed",
        "installed desc": "-installed",
        "last managed": "last_managed",
        "last_managed": "last_managed",
        "last managed desc": "-last_managed",
        "last_managed desc": "-last_managed",
    }
    if v.startswith("-"):
        key = v[1:]
        if key in {"default", "created_date", "created date", "name", "label", "installed", "last_managed", "last managed"}:
            return "-" + aliases.get(key, key.replace(" ", "_"))
    if v in aliases:
        return aliases[v]
    raise argparse.ArgumentTypeError("order must be one of: default, created_date, name, label, installed, last_managed, with optional '-' prefix or ' desc'")

OVERWRITE_HELP = "Replace files that already exist in the game mods folder when the profile installs by copy."

def _add_overwrite_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--overwrite", action="store_true", help=OVERWRITE_HELP)

def _add_profile_args(parser: argparse.ArgumentParser, use_defaults: bool) -> None:
    """Build the per game profile flags from the shared schema so the lists cannot drift."""
    for spec in settings_schema.MODS_FIELDS:
        flag = "--" + spec.key.replace("_", "-")
        if spec.kind == settings_schema.FLAG:
            default = False if use_defaults else None
            parser.add_argument(flag, action=argparse.BooleanOptionalAction, default=default, help=spec.tooltip)
        elif spec.kind == settings_schema.CHOICE:
            default = spec.choices[0] if use_defaults else None
            parser.add_argument(flag, choices=list(spec.choices), default=default, help=spec.tooltip)
        else:
            parser.add_argument(flag, default="" if use_defaults else None, help=spec.tooltip)

def _add_view_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--label", default="")
    parser.add_argument("--search", default="")
    parser.add_argument("--order", type=_order, default="d")
    parser.add_argument("--favorite", action="store_true")

def _filtered_mods_view(cfg: Dict, page: int, label: str, search: str, order: str, favorite_only: bool = False):
    if favorite_only:
        return mods_view(cfg, page, label, search, order, True)
    return mods_view(cfg, page, label, search, order)

def _print_mods(cfg: Dict, page: int, label: str, search: str, order: str, favorite_only: bool = False) -> int:
    items, shown, page, pages, labels = _filtered_mods_view(cfg, page, label, search, order, favorite_only)
    print(f"Page {page}/{pages}")
    for i, mod in enumerate(shown, 1):
        mark = "X" if mod.installed else " "
        label_text = labels.get(mod.name, "-")
        print(f"{i}. [{mark}] {mod.name} [{label_text}]")
    if not items:
        print("No mods.")
    return 0

def _print_presets(cfg: Dict, page: int) -> int:
    presets, keys, page_keys, page, pages = presets_view(cfg, page)
    installed = {m.name for m in mods_view(cfg, 1, "", "", "d")[0] if m.installed}
    print(f"Page {page}/{pages}")
    for i, name in enumerate(page_keys, 1):
        mods = presets.get(name, [])
        mark = "X" if bool(mods) and all(nm in installed for nm in mods) else " "
        print(f"{i}. [{mark}] {name} [{len(mods)}]")
    if not keys:
        print("No presets saved.")
    return 0

OVERWRITE_HINT = "Re-run with --overwrite to replace them."

def _allow_overwrite(cfg: Dict, pending: Callable[[], List], overwrite: bool) -> bool:
    """Print the warning and refuse when a copy install would replace existing files."""
    if overwrite or not is_copy_install(cfg):
        return True
    names = existing_targets(pending())
    if not names:
        return True
    print(overwrite_message(names))
    print(OVERWRITE_HINT)
    return False

def _pending_mods(cfg: Dict, page: int, label: str, search: str, order: str, favorite_only: bool) -> List:
    _items, shown, _page, _pages, _labels = _filtered_mods_view(cfg, page, label, search, order, favorite_only)
    return [m for m in shown if not m.installed]

def _pending_preset_mods(cfg: Dict, args: argparse.Namespace) -> List:
    names = preset_names_by_indexes(cfg, args.page, args.indexes)
    work, _missing = preset_mods_to_install(cfg, names)
    return work

def _selected_mod_names(
    cfg: Dict,
    page: int,
    label: str,
    search: str,
    order: str,
    indexes: List[int],
    favorite_only: bool = False,
) -> List[str]:
    _items, shown, _page, _pages, _labels = _filtered_mods_view(cfg, page, label, search, order, favorite_only)
    return [shown[i - 1].name for i in indexes if 1 <= i <= len(shown)]

def _run_mods(args: argparse.Namespace, cfg: Dict) -> int:
    if not ensure_paths(cfg):
        return 1
    if args.mods_cmd in ["list", "search", "label", "page", "order"]:
        search = args.text if args.mods_cmd == "search" else args.search
        label = args.text if args.mods_cmd == "label" else args.label
        page = args.number if args.mods_cmd == "page" else args.page
        order = args.mode if args.mods_cmd == "order" else args.order
        return _print_mods(cfg, page, label, search, order, args.favorite)
    if args.mods_cmd == "install":
        view_args = (cfg, args.page, args.label, args.search, args.order, args.favorite)
        if not _allow_overwrite(cfg, lambda: _pending_mods(*view_args), args.overwrite):
            return 1
        page, total, err = apply_mods_page(*view_args, args.overwrite)
        print(f"Installed {total - err}/{total} on page {page}. Errors: {err}.")
        return 1 if err else 0
    if args.mods_cmd == "uninstall":
        view_args = (cfg, args.page, args.label, args.search, args.order)
        page, count = deactivate_mods_page(*view_args, True) if args.favorite else deactivate_mods_page(*view_args)
        print(f"Uninstalled {count} on page {page}.")
        return 0
    if args.mods_cmd == "toggle":
        _items, shown, _page, _pages, _labels = _filtered_mods_view(
            cfg, args.page, args.label, args.search, args.order, args.favorite
        )
        pending = [m for m in mods_by_indexes(shown, args.indexes) if not m.installed]
        if not _allow_overwrite(cfg, lambda: pending, args.overwrite):
            return 1
        msg = toggle_mods_by_indexes(shown, args.indexes, args.overwrite)
        print(msg or "No mods toggled.")
        return 0
    if args.mods_cmd == "label-add":
        targets = _selected_mod_names(
            cfg, args.page, args.filter_label, args.search, args.order, args.indexes, args.favorite
        )
        print(add_label_to_mods(args.label, targets) if targets else "Invalid index.")
        return 0 if targets else 1
    if args.mods_cmd == "label-remove":
        targets = _selected_mod_names(
            cfg, args.page, args.filter_label, args.search, args.order, args.indexes, args.favorite
        )
        print(remove_label_from_mods(args.label, targets) if targets else "Invalid index.")
        return 0 if targets else 1
    if args.mods_cmd in {"favorite-add", "favorite-remove"}:
        targets = _selected_mod_names(
            cfg, args.page, args.filter_label, args.search, args.order, args.indexes, args.favorite
        )
        if not targets:
            print("Invalid index.")
            return 1
        action = add_favorites_to_mods if args.mods_cmd == "favorite-add" else remove_favorites_from_mods
        print(action(cfg, targets))
        return 0
    return 1

def _run_presets(args: argparse.Namespace, cfg: Dict) -> int:
    if not ensure_paths(cfg):
        return 1
    if args.presets_cmd in ["list", "page"]:
        page = args.number if args.presets_cmd == "page" else args.page
        return _print_presets(cfg, page)
    if args.presets_cmd == "save":
        ok, msg = save_preset_from_installed(cfg, args.name)
        print(msg)
        return 0 if ok else 1
    if args.presets_cmd == "delete":
        count, missing = delete_presets_by_indexes(cfg, args.page, args.indexes)
        print(f"Deleted: {count}. Missing: {', '.join(missing) if missing else 'none'}")
        return 0
    if args.presets_cmd == "toggle":
        installed = {m.name for m in mods_view(cfg, 1, "", "", "d")[0] if m.installed}
        if not _allow_overwrite(cfg, lambda: _pending_preset_mods(cfg, args), args.overwrite):
            return 1
        msg, messages, has_errors = toggle_presets_by_indexes(
            cfg, args.page, args.indexes, installed, args.overwrite
        )
        print(msg or "No presets toggled.")
        for item in messages:
            print(" - ", item)
        return 1 if has_errors else 0
    return 1

def _run_settings(args: argparse.Namespace, cfg: Dict) -> int:
    if args.settings_cmd == "show":
        for key in sorted(cfg):
            print(f"{key}: {cfg[key]}")
        return 0
    changed = False
    for spec in settings_schema.all_specs():
        value = getattr(args, spec.key, None)
        if value is not None:
            try:
                cfg[spec.key] = settings_schema.coerce_value(spec, value)
            except ValueError as error:
                print(str(error))
                return 2
            changed = True
    if changed:
        save_config(cfg)
        print("Saved.")
    else:
        print("Nothing changed.")
    return 0

def _profile_values_from_args(args: argparse.Namespace) -> Dict:
    values = {}
    if getattr(args, "name", None) is not None:
        values["name"] = args.name
    for key in GAME_PROFILE_KEYS:
        value = getattr(args, key, None)
        if value is not None:
            values[key] = value
    return values

def _run_games(args: argparse.Namespace, cfg: Dict) -> int:
    profiles = cfg.get("game_profiles", []) or []
    if args.games_cmd == "list":
        active_id = cfg.get("active_game_profile_id", "")
        for profile in profiles:
            mark = "*" if profile.get("id") == active_id else " "
            print(f"{mark} {profile.get('id')} {game_abbreviation(profile.get('name', ''))} {profile.get('name')}")
        if not profiles:
            print("No game profiles.")
        return 0
    if args.games_cmd == "select":
        if set_active_game_profile(cfg, args.profile_id):
            save_config(cfg)
            print("Selected.")
            return 0
        print("Game profile not found.")
        return 1
    if args.games_cmd == "add":
        values = _profile_values_from_args(args)
        create_game_profile(values.pop("name"), values, cfg)
        save_config(cfg)
        print("Added.")
        return 0
    if args.games_cmd == "edit":
        if update_game_profile(cfg, args.profile_id, _profile_values_from_args(args)):
            save_config(cfg)
            print("Saved.")
            return 0
        print("Game profile not found.")
        return 1
    if args.games_cmd == "delete":
        if delete_game_profile(cfg, args.profile_id):
            save_config(cfg)
            print("Deleted.")
            return 0
        print("Game profile not found.")
        return 1
    return 1

def _run_open(args: argparse.Namespace, cfg: Dict) -> int:
    key = "mods_source_dir" if args.target == "source" else "game_mods_dir"
    ok, msg = open_folder(cfg.get(key, ""))
    print(f"Open {args.target} folder: {'OK' if ok else 'ERR'} — {msg}")
    return 0 if ok else 1

def _run_broken(args: argparse.Namespace, cfg: Dict) -> int:
    if not ensure_paths(cfg):
        return 1
    broken = list_broken_links(cfg)
    if args.broken_cmd == "list":
        for i, mod in enumerate(broken, 1):
            kind = "DIR" if mod.is_dir else "FILE"
            print(f"{i}. [!] {mod.name} ({kind}) -> missing source: {mod.src}")
        if not broken:
            print("No broken links detected.")
        return 0
    targets = broken if args.all else [broken[i - 1] for i in args.indexes if 1 <= i <= len(broken)]
    for mod in targets:
        ok, msg = deactivate_mod(mod)
        print(f"Remove {mod.dest.name}: {'OK' if ok else 'ERR'} — {msg}")
    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mod-manager.py")
    parser.add_argument("--version", action="version", version=f"{APP_NAME} v{APP_VERSION}")
    sub = parser.add_subparsers(dest="cmd")

    mods = sub.add_parser("mods")
    mods_sub = mods.add_subparsers(dest="mods_cmd", required=True)
    for name in ["list", "install", "uninstall", "toggle"]:
        p = mods_sub.add_parser(name)
        _add_view_args(p)
        if name in {"install", "toggle"}:
            _add_overwrite_arg(p)
    p = mods_sub.add_parser("search")
    p.add_argument("text")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--label", default="")
    p.add_argument("--order", type=_order, default="d")
    p.add_argument("--favorite", action="store_true")
    p = mods_sub.add_parser("label")
    p.add_argument("text")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--search", default="")
    p.add_argument("--order", type=_order, default="d")
    p.add_argument("--favorite", action="store_true")
    p = mods_sub.add_parser("page")
    p.add_argument("number", type=int)
    p.add_argument("--label", default="")
    p.add_argument("--search", default="")
    p.add_argument("--order", type=_order, default="d")
    p.add_argument("--favorite", action="store_true")
    p = mods_sub.add_parser("order")
    p.add_argument("mode", type=_order)
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--label", default="")
    p.add_argument("--search", default="")
    p.add_argument("--favorite", action="store_true")
    mods_sub.choices["toggle"].add_argument("indexes", type=_indexes)
    for name in ["label-add", "label-remove"]:
        p = mods_sub.add_parser(name)
        p.add_argument("label")
        p.add_argument("indexes", type=_indexes)
        p.add_argument("--page", type=int, default=1)
        p.add_argument("--filter-label", default="")
        p.add_argument("--search", default="")
        p.add_argument("--order", type=_order, default="d")
        p.add_argument("--favorite", action="store_true")
    for name in ["favorite-add", "favorite-remove"]:
        p = mods_sub.add_parser(name)
        p.add_argument("indexes", type=_indexes)
        p.add_argument("--page", type=int, default=1)
        p.add_argument("--filter-label", default="")
        p.add_argument("--search", default="")
        p.add_argument("--order", type=_order, default="d")
        p.add_argument("--favorite", action="store_true")

    presets = sub.add_parser("presets")
    presets_sub = presets.add_subparsers(dest="presets_cmd", required=True)
    presets_sub.add_parser("list").add_argument("--page", type=int, default=1)
    presets_sub.add_parser("page").add_argument("number", type=int)
    presets_sub.add_parser("save").add_argument("name")
    for name in ["delete", "toggle"]:
        p = presets_sub.add_parser(name)
        p.add_argument("indexes", type=_indexes)
        p.add_argument("--page", type=int, default=1)
        if name == "toggle":
            _add_overwrite_arg(p)

    settings = sub.add_parser("settings")
    settings_sub = settings.add_subparsers(dest="settings_cmd", required=True)
    settings_sub.add_parser("show")
    settings_set = settings_sub.add_parser("set")
    for spec in settings_schema.all_specs():
        flag = "--" + spec.key.replace("_", "-")
        if spec.kind == settings_schema.FLAG:
            settings_set.add_argument(flag, action=argparse.BooleanOptionalAction, default=None, help=spec.tooltip)
        elif spec.kind == settings_schema.CHOICE:
            settings_set.add_argument(flag, choices=list(spec.choices), help=spec.tooltip)
        elif spec.kind == settings_schema.INT:
            settings_set.add_argument(flag, type=int, help=spec.tooltip)
        else:
            settings_set.add_argument(flag, help=spec.tooltip)

    games = sub.add_parser("games")
    games_sub = games.add_subparsers(dest="games_cmd", required=True)
    games_sub.add_parser("list")
    games_select = games_sub.add_parser("select")
    games_select.add_argument("profile_id")
    games_delete = games_sub.add_parser("delete")
    games_delete.add_argument("profile_id")
    games_add = games_sub.add_parser("add")
    games_add.add_argument("name")
    _add_profile_args(games_add, use_defaults=True)
    games_edit = games_sub.add_parser("edit")
    games_edit.add_argument("profile_id")
    games_edit.add_argument("--name")
    _add_profile_args(games_edit, use_defaults=False)

    open_parser = sub.add_parser("open")
    open_parser.add_argument("target", choices=["source", "game"])

    broken = sub.add_parser("broken")
    broken_sub = broken.add_subparsers(dest="broken_cmd", required=True)
    broken_sub.add_parser("list")
    broken_remove = broken_sub.add_parser("remove")
    broken_remove.add_argument("indexes", nargs="?", type=_indexes, default=[])
    broken_remove.add_argument("--all", action="store_true")

    sub.add_parser("gui")

    help_p = sub.add_parser("help", help="Show help for a command")
    help_p.add_argument("topic", nargs="*", metavar="command", help="Command and optional subcommand (e.g. mods toggle)")

    return parser

def _subparsers_map(parser: argparse.ArgumentParser) -> dict:
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action.choices
    return {}

def _run_help(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    topics = args.topic
    if not topics:
        parser.print_help()
        return 0
    top = _subparsers_map(parser)
    if topics[0] not in top:
        print(f"Unknown command: '{topics[0]}'. Available: {', '.join(top)}")
        return 1
    cmd_parser = top[topics[0]]
    if len(topics) == 1:
        cmd_parser.print_help()
        return 0
    sub = _subparsers_map(cmd_parser)
    if topics[1] not in sub:
        print(f"Unknown subcommand: '{topics[1]}'. Available: {', '.join(sub) or 'none'}")
        cmd_parser.print_help()
        return 1
    sub[topics[1]].print_help()
    return 0

def run_cli(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.cmd == "help":
        return _run_help(args, parser)
    cfg = load_config()
    if args.cmd == "mods":
        return _run_mods(args, cfg)
    if args.cmd == "presets":
        return _run_presets(args, cfg)
    if args.cmd == "settings":
        return _run_settings(args, cfg)
    if args.cmd == "games":
        return _run_games(args, cfg)
    if args.cmd == "open":
        return _run_open(args, cfg)
    if args.cmd == "broken":
        return _run_broken(args, cfg)
    if args.cmd == "gui":
        from .ui import run_gui
        return run_gui()
    parser.print_help()
    return 0
