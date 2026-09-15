"""Fund/quarter path resolution for dashboard and history builds.

No financial logic. Resolves stamped parsed/classified/market_data
paths so a rebuild does not need the shared working copies
(data/parsed_rows.json, data/classified_rows.json, data/market_data.json).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPTS_DIR / "data"
REPO_ROOT = SCRIPTS_DIR.parent
REGISTRY_PATH = REPO_ROOT / "references" / "manager_registry.json"

# Short HTML/filename slugs for the accepted four-fund set. Other
# registry names fall back to a slugified registry key.
FUND_SLUGS = {
    "armistice capital": "armistice",
    "pinnbrook capital management": "pinnbrook",
    "scge management": "scge",
    "melqart asset management": "melqart",
}

ALL_REGISTRY_KEYS = tuple(FUND_SLUGS.keys())

ALIASES = {
    "armistice": "armistice capital",
    "pinnbrook": "pinnbrook capital management",
    "scge": "scge management",
    "melqart": "melqart asset management",
}

CLASSIFIED_NAME_RE = re.compile(
    r"^classified_rows_(.+)_(\d{4}-\d{2}-\d{2})\.json$"
)
QUARTER_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class FundBuildError(Exception):
    """User-facing build failure -- missing/mismatched inputs, not a crash."""


@dataclass(frozen=True)
class Manager:
    registry_key: str
    cik: str
    full_name: str
    slug: str


def normalize_cik(value) -> str:
    if value is None or value == "":
        raise FundBuildError("Missing CIK")
    text = str(value).strip()
    if not text.isdigit():
        raise FundBuildError(f"Invalid CIK {value!r}")
    return str(int(text))


def parse_quarter(value: str) -> str:
    text = (value or "").strip()
    if not QUARTER_RE.fullmatch(text):
        raise FundBuildError(
            f"Invalid --quarter {value!r}; expected YYYY-MM-DD "
            f"(the filing period_of_report, e.g. 2026-06-30)."
        )
    return text


def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        raise FundBuildError(f"Manager registry not found: {REGISTRY_PATH}")
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return json.load(f)


def _slug_for(registry_key: str) -> str:
    if registry_key in FUND_SLUGS:
        return FUND_SLUGS[registry_key]
    return re.sub(r"[^a-z0-9]+", "_", registry_key).strip("_")


def manager_from_key(registry_key: str, registry: dict | None = None) -> Manager:
    registry = registry if registry is not None else load_registry()
    if registry_key not in registry:
        raise FundBuildError(
            f"Registry key {registry_key!r} is not in {REGISTRY_PATH}"
        )
    entry = registry[registry_key]
    return Manager(
        registry_key=registry_key,
        cik=normalize_cik(entry["cik"]),
        full_name=entry.get("full_name") or registry_key,
        slug=_slug_for(registry_key),
    )


def resolve_manager(query: str) -> Manager:
    """Resolve a manager from a registry key, alias, legal name, or CIK.

    Ambiguous names fail rather than picking a guess.
    """
    raw = (query or "").strip()
    q = re.sub(r"\s+", " ", raw.lower())
    if not q:
        raise FundBuildError("--manager is empty")

    registry = load_registry()

    if q.isdigit():
        cik = normalize_cik(q)
        hits = [
            key for key, entry in registry.items()
            if normalize_cik(entry.get("cik")) == cik
        ]
        if len(hits) == 1:
            return manager_from_key(hits[0], registry)
        if not hits:
            raise FundBuildError(
                f"CIK {cik} is not in {REGISTRY_PATH}. Add the manager "
                f"to the registry before building a dashboard."
            )
        raise FundBuildError(
            f"CIK {cik} matches multiple registry entries: {', '.join(hits)}"
        )

    if q in registry:
        return manager_from_key(q, registry)
    if q in ALIASES:
        return manager_from_key(ALIASES[q], registry)

    full_hits = [
        key for key, entry in registry.items()
        if (entry.get("full_name") or "").strip().lower() == q
    ]
    if len(full_hits) == 1:
        return manager_from_key(full_hits[0], registry)
    if len(full_hits) > 1:
        raise FundBuildError(
            f"{raw!r} matches multiple legal names: {', '.join(full_hits)}"
        )

    hits = []
    for key, entry in registry.items():
        name = (entry.get("full_name") or "").strip().lower()
        if q == key or q in key or key.startswith(q) or q in name or name.startswith(q):
            hits.append(key)
    hits = list(dict.fromkeys(hits))
    if len(hits) == 1:
        return manager_from_key(hits[0], registry)
    if not hits:
        raise FundBuildError(
            f"{raw!r} is not in {REGISTRY_PATH}. Use a registry key, "
            f"legal name, short alias (armistice/pinnbrook/scge/melqart), "
            f"or CIK."
        )
    raise FundBuildError(
        f"{raw!r} matches multiple managers: {', '.join(hits)}. "
        f"Use a more specific name or a CIK."
    )


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def split_market_payload(raw, source="market data"):
    """Accept a legacy JSON list or a {bloombergPulledAt, records} wrapper.

    Provenance only. Returns (records, meta). Historical list files stay
    valid and carry empty meta — never invent a pull date.
    """
    if isinstance(raw, list):
        return raw, {}
    if isinstance(raw, dict) and isinstance(raw.get("records"), list):
        meta = {}
        pulled = raw.get("bloombergPulledAt")
        if isinstance(pulled, str) and pulled.strip():
            meta["bloombergPulledAt"] = pulled.strip()
        return raw["records"], meta
    raise ValueError(
        f"{source}: market data must be a JSON list or an object with a records list"
    )


def market_payload_dump(records, meta=None):
    """Serialize market data. Wrapper is used only when a pull timestamp exists."""
    pulled = (meta or {}).get("bloombergPulledAt")
    if isinstance(pulled, str) and pulled.strip():
        return {
            "bloombergPulledAt": pulled.strip(),
            "records": records,
        }
    return records


def write_market_snapshot(path: Path, records, meta=None) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(market_payload_dump(records, meta), indent=2),
        encoding="utf-8",
    )


def read_market_meta(path: Path) -> dict:
    path = Path(path)
    if not path.exists():
        return {}
    try:
        _records, meta = split_market_payload(load_json(path), str(path))
    except (ValueError, json.JSONDecodeError, OSError):
        return {}
    return meta


def validate_classified(rows, cik: str, period: str, path: Path) -> None:
    if not rows:
        raise FundBuildError(f"{path}: classified file is empty")
    row_cik = normalize_cik(rows[0].get("_source_cik"))
    row_period = rows[0].get("_source_period_of_report")
    if row_cik != cik:
        raise FundBuildError(
            f"{path}: classified rows are CIK {row_cik}, not {cik}. "
            f"Refusing to use another fund's file."
        )
    if row_period != period:
        raise FundBuildError(
            f"{path}: classified rows are period {row_period!r}, not "
            f"{period!r}. Refusing to fall back to another quarter."
        )


def classified_candidates(cik: str, slug: str, period: str) -> list[Path]:
    return [
        DATA_DIR / f"classified_rows_{cik}_{period}.json",
        DATA_DIR / f"classified_rows_{slug}_{period}.json",
    ]


def resolve_classified_path(manager: Manager, period: str) -> Path:
    tried = classified_candidates(manager.cik, manager.slug, period)
    for path in tried:
        if path.exists():
            return path
    names = ", ".join(p.name for p in tried)
    raise FundBuildError(
        f"No classified rows for {manager.full_name} (CIK {manager.cik}) "
        f"period {period}.\n"
        f"  looked in {DATA_DIR} for: {names}\n"
        f"  The shared data/classified_rows.json is not used."
    )


def resolve_market_path(manager: Manager, period: str) -> Path:
    path = DATA_DIR / f"market_data_{manager.cik}_{period}.json"
    if not path.exists():
        raise FundBuildError(
            f"No Bloomberg market-data snapshot for {manager.full_name} "
            f"(CIK {manager.cik}) period {period}.\n"
            f"  expected: {path}\n"
            f"  Import a refreshed Bloomberg workbook into that stamped "
            f"file before building this dashboard. The shared "
            f"data/market_data.json is not used."
        )
    return path


def load_classified(manager: Manager, period: str) -> tuple[Path, list]:
    path = resolve_classified_path(manager, period)
    rows = load_json(path)
    validate_classified(rows, manager.cik, period, path)
    return path, rows


def load_market_records(path: Path) -> list:
    try:
        records, _meta = split_market_payload(load_json(path), str(path))
    except ValueError as exc:
        raise FundBuildError(str(exc)) from None
    if not records:
        raise FundBuildError(f"{path} has no securities")
    if not any(r.get("cusip") for r in records if isinstance(r, dict)):
        raise FundBuildError(f"{path} has no CUSIPs")
    return records


def iter_classified_stamps(manager: Manager):
    """Yield (period, path) for stamped classified files of this fund."""
    found = {}
    for path in DATA_DIR.glob("classified_rows_*.json"):
        match = CLASSIFIED_NAME_RE.match(path.name)
        if not match:
            continue
        token, period = match.group(1), match.group(2)
        if token not in (manager.cik, manager.slug):
            continue
        previous = found.get(period)
        if previous is None or token == manager.cik:
            found[period] = path
    for period in sorted(found):
        yield period, found[period]


def discover_prior_classified(manager: Manager, current_period: str) -> list[tuple[str, Path, list]]:
    """Prior quarters for this fund only, oldest first. No other-fund files."""
    priors = []
    for period, path in iter_classified_stamps(manager):
        if period >= current_period:
            continue
        rows = load_json(path)
        validate_classified(rows, manager.cik, period, path)
        priors.append((period, path, rows))
    return priors


def latest_buildable_quarter(manager: Manager) -> str:
    """Latest period that has both classified rows and a market snapshot."""
    periods = []
    for period, _path in iter_classified_stamps(manager):
        market = DATA_DIR / f"market_data_{manager.cik}_{period}.json"
        if market.exists():
            periods.append(period)
    if not periods:
        raise FundBuildError(
            f"No classified + market-data pair for {manager.full_name} "
            f"(CIK {manager.cik}) under {DATA_DIR}."
        )
    return max(periods)


def dashboard_output_path(manager: Manager, period: str) -> Path:
    return SCRIPTS_DIR / f"dashboard_{manager.slug}_{period}.html"


def parsed_path(manager: Manager, period: str) -> Path:
    return DATA_DIR / f"parsed_rows_{manager.cik}_{period}.json"


def classified_write_path(manager: Manager, period: str) -> Path:
    """Canonical classified stamp. CIK, not slug -- slug files still readable."""
    return DATA_DIR / f"classified_rows_{manager.cik}_{period}.json"


def bloomberg_template_path(manager: Manager, period: str) -> Path:
    return DATA_DIR / f"bloomberg_template_{manager.cik}_{period}.xlsx"


def market_write_path(manager: Manager, period: str) -> Path:
    """Canonical market snapshot. CIK stamp only -- slug names are not used."""
    return DATA_DIR / f"market_data_{manager.cik}_{period}.json"


def raw_filings_dir() -> Path:
    return DATA_DIR / "raw_filings"


def shared_working_files() -> tuple[Path, Path, Path]:
    return (
        DATA_DIR / "parsed_rows.json",
        DATA_DIR / "classified_rows.json",
        DATA_DIR / "market_data.json",
    )


def validate_parsed(rows, cik: str, period: str, path: Path) -> None:
    if not rows:
        raise FundBuildError(f"{path}: parsed file is empty")
    row_cik = normalize_cik(rows[0].get("_source_cik"))
    row_period = rows[0].get("_source_period_of_report")
    if row_cik != cik:
        raise FundBuildError(
            f"{path}: parsed rows are CIK {row_cik}, not {cik}. "
            f"Refusing to use another fund's file."
        )
    if row_period != period:
        raise FundBuildError(
            f"{path}: parsed rows are period {row_period!r}, not "
            f"{period!r}. Refusing to fall back to another quarter."
        )


def accepted_managers() -> list[Manager]:
    registry = load_registry()
    return [manager_from_key(key, registry) for key in ALL_REGISTRY_KEYS]
