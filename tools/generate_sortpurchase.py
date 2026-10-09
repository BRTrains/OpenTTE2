"""Regenerate OpenTTE2's hand-ordered purchase list from the build's own items.

The project orders its purchase list by hand (`purchase_list.file` in `src/grf/GRF.yaml`),
because no derived rule expresses "the NWR characters first, in their number order, then the
unnumbered engines by power, then coaches, then wagons". This tool rebuilds that file from
the vehicles the build actually produced, so a new unit cannot leave the list stale:

1. engines carrying an `NWR/<number>` tag, by number — numeric numbers ascending, then the
   `D`-numbered diesels — taking the first number where a tag lists two (Donald and Douglas
   are `NWR/9,10`);
2. the engines with no such tag, by ascending power;
3. coaches, by name;
4. wagons, by name.

Road vehicles are ordered by the same rules; every road vehicle in the set falls in the
first two groups. A unit's own variants stay together in the build's order (profile-outer,
livery-inner), so a unit's liveries never interleave with another unit's.

`build.py` runs this after every successful build, so the file in the repository is always
the build's own item set. Run it by hand with `--dry-run` to see the result without writing.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TARGET = PROJECT_ROOT / "src" / "grf" / "custom_nml" / "append" / "sortpurchase.pnml"
NML = PROJECT_ROOT / "Build" / "OpenTTE2.nml"
REGISTRY = PROJECT_ROOT / "src" / "grf" / "VehicleIDData.yaml"
VEHICLES = PROJECT_ROOT / "src" / "vehicles"

#: `NWR/1`, `NWR/9,10`, `NWR/D2` — the number is what orders the first group.
NWR_TAG = re.compile(r"(?i)^\s*NWR\s*/\s*D?(\d+)")
NWR_DIESEL_TAG = re.compile(r"(?i)^\s*NWR\s*/\s*D\s*(\d+)\s*$")

ITEM = re.compile(r"^item\s*\(\s*FEAT_(\w+)\s*,\s*(\w+)\s*,\s*(\d+)\s*\)", re.M)

#: The features the file carries a `sort` block for.
FEATURES = ("TRAINS", "ROADVEHS")

HEADER = """\
// Purchase-list order for OpenTTE2, maintained by hand (purchase_list.file).
//
// 1. NWR-numbered engines, by number (numeric numbers, then the `D` diesel numbers).
// 2. The engines without an NWR number, by power (lowest first).
// 3. Coaches, by name.
// 4. Wagons, by name.
//
// The block names the item symbols the build produced, so a new or renamed candidate has to
// be added here by hand. A unit typed `types: [TRAM, TRAIN]` appears in both blocks: the tram
// side is ordered by the same rule.
//
// Rebuilt from the build's own items by tools/generate_sortpurchase.py, which build.py runs
// after every successful build.
"""

SECTIONS = {
    "numbered": "  // -- engines with an NWR number, by number --",
    "power": "  // -- engines with no NWR number, lowest power first --",
    "coaches": "  // -- coaches, by name --",
    "wagons": "  // -- wagons, by name --",
}

TRAIN_FOOTER = "// The tram side of the units typed for both features (Toby, Mavis)."
ROADVEH_SECTIONS = {"numbered": SECTIONS["numbered"], "power": SECTIONS["power"]}


def vehicle_metadata() -> dict[str, dict]:
    """Read every vehicle definition, keyed by its identifier (casefolded)."""
    found: dict[str, dict] = {}

    for path in sorted(VEHICLES.rglob("*")):
        # A contributor's file may be named `Van.Yaml`, so match the suffix case-insensitively.
        if path.suffix.lower() not in (".yaml", ".yml") or not path.is_file():
            continue

        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

        if not isinstance(data, dict) or "info" not in data:
            continue

        info = data.get("info") or {}
        stats = data.get("stats") or {}
        identifier = str(info.get("identifier") or path.stem)

        number = None
        diesel = None

        for tag in data.get("special_tags") or []:
            text = str(tag)
            match = NWR_TAG.match(text)
            if match:
                number = int(match.group(1))
            match = NWR_DIESEL_TAG.match(text)
            if match:
                diesel = int(match.group(1))

        found[identifier.casefold()] = {
            "name": str(info.get("name") or identifier),
            "train_type": str(stats.get("train_type") or "").upper(),
            "power": stats.get("power"),
            "number": number,
            "diesel": diesel,
        }

    return found


def built_items() -> dict[str, dict[str, int]]:
    """The features and item symbols the last build produced, with their ids."""
    if not NML.is_file():
        raise SystemExit(f"No build output to read: {NML}")

    items: dict[str, dict[str, int]] = {}

    for feature, symbol, item_id in ITEM.findall(NML.read_text(encoding="utf-8")):
        items.setdefault(feature, {})[symbol] = int(item_id)

    return items


def variant_vehicles() -> dict[str, str]:
    """Map each built variant's identifier to the vehicle it belongs to."""
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}

    return {
        variant["identifier"]: str(variant.get("vehicle", ""))
        for variant in registry.get("variants", [])
    }


def sort_key(vehicle: dict) -> tuple:
    """The four rules, as one key: numbered engines, unnumbered engines, coaches, wagons."""
    train_type = vehicle["train_type"]

    if train_type == "COACH":
        return (3, 0, 0, 0, vehicle["name"].casefold())

    if train_type == "WAGON":
        return (4, 0, 0, 0, vehicle["name"].casefold())

    if vehicle["diesel"] is not None:
        # The `D` numbers are a separate series, so they follow the numeric ones.
        return (1, 1, vehicle["diesel"], 0, "")

    if vehicle["number"] is not None:
        return (1, 0, vehicle["number"], 0, "")

    return (2, 0, 0, vehicle["power"] if vehicle["power"] is not None else 0, vehicle["name"].casefold())


def section_of(vehicle: dict) -> str:
    """Which of the four groups a vehicle belongs to."""
    if vehicle["train_type"] == "COACH":
        return "coaches"

    if vehicle["train_type"] == "WAGON":
        return "wagons"

    return "numbered" if vehicle["number"] is not None or vehicle["diesel"] is not None else "power"


def describe(vehicle: dict) -> str:
    """The per-entry comment: the name, then the number or power that placed it."""
    name = vehicle["name"]

    if vehicle["train_type"] in ("COACH", "WAGON"):
        return name

    if vehicle["diesel"] is not None:
        return f"{name} (D{vehicle['diesel']})"

    if vehicle["number"] is not None:
        power = vehicle["power"]

        return f"{name} (NWR {vehicle['number']}, {power} hp)" if power else f"{name} (NWR {vehicle['number']})"

    return f"{name} ({vehicle['power']} hp)" if vehicle["power"] is not None else name


def build_file() -> str:
    metadata = vehicle_metadata()
    owners = variant_vehicles()
    items = built_items()

    def vehicle_of(unit: str) -> dict:
        for key in (unit.casefold(), unit.replace("_", "").casefold()):
            if key in metadata:
                return metadata[key]

        raise SystemExit(f"No vehicle definition found for '{unit}'")

    lines = [HEADER]

    for feature in FEATURES:
        built = items.get(feature, {})

        if not built:
            continue

        units: dict[str, list[str]] = {}

        for symbol in sorted(built, key=lambda symbol: built[symbol]):
            vehicle = owners.get(symbol)

            if vehicle is None:
                raise SystemExit(f"'{symbol}' is in the build but not in the registry")

            units.setdefault(vehicle, []).append(symbol)

        ordered = sorted(units, key=lambda unit: (sort_key(vehicle_of(unit)), unit))

        if feature == "TRAINS":
            lines.append("sort(FEAT_TRAINS, [\n")
            sections = SECTIONS
        else:
            lines.append(TRAIN_FOOTER + "\n")
            lines.append("sort(FEAT_ROADVEHS, [\n")
            sections = ROADVEH_SECTIONS

        last_section = None

        for unit in ordered:
            vehicle = vehicle_of(unit)
            section = section_of(vehicle)

            if section != last_section:
                if last_section is not None:
                    lines.append("\n")
                lines.append(sections[section] + "\n")
                last_section = section

            lines.append(f"  // {describe(vehicle)}\n")

            for symbol in units[unit]:
                lines.append(f"  {symbol},\n")

        # The block's last entry carries no trailing comma.
        lines[-1] = lines[-1].rstrip(",\n") + "\n"
        lines.append("]);\n\n")

    return "".join(lines).rstrip("\n") + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print the file instead of writing it")
    args = parser.parse_args()

    content = build_file()

    if args.dry_run:
        sys.stdout.write(content)
        return 0

    if TARGET.read_text(encoding="utf-8") == content:
        print(f"Purchase list already in step with the build: {TARGET}")
        return 0

    TARGET.write_text(content, encoding="utf-8")
    print(f"Rebuilt the purchase list: {TARGET} ({len(content.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
