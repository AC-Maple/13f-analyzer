"""
resolution_log.py -- Step 8: human decision capture. The missing piece
between "the pipeline flagged something" and "a human looked at it and
we remember what they decided."

Without this, every re-run re-surfaces the same exceptions from
scratch, and there's no record that a person ever reviewed a
FUND_UNVERIFIED row or a REVIEW_MARKET_DATA transition and decided it
was fine (or wasn't). This module is that record.

Append-only log, one JSON object per line (.jsonl) -- cheap to append
(no read-modify-rewrite of the whole file on every resolution), and
naturally auditable: every past decision stays in the file, nothing is
ever overwritten in place.

Exception ID scheme, consistent across every producer script:
    {fund}:{period}:{check}:{identifier}

Examples actually used by wired-in producers:
    armistice:2025-12-31_to_2026-03-31:check4:857477201   (corporate_actions.py)

Not yet wired in (see SKILL.md): integrity.py's other REVIEW_* checks,
liquidity.py's COMPOUNDING_ILLIQUIDITY flag, analyze.py's related-
security-family flags. Each of those will need its own exception_id
shape (row-based for some checks, cusip-based for others) -- this
module doesn't impose one, it just requires that whatever ID a
producer constructs is stable across runs so is_resolved() actually
matches on the next one.

This module does NOT decide what counts as "resolved enough to stop
re-flagging" -- that's each producer script's call, since a check-4
REVIEW and an informational family-flag note have different standards
for what a human needs to have done before it's closed. This module
only provides: record a decision, and look one up.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

LOG_FILE = "data/resolution_log.jsonl"

VALID_DECISIONS = {"APPROVE", "CORRECT", "ESCALATE"}


def make_exception_id(fund, period, check, identifier):
    """Canonical ID builder -- use this everywhere rather than hand-
    formatting the string, so the scheme stays consistent as more
    producers get wired in."""
    return f"{fund}:{period}:{check}:{identifier}"


def derive_quarter_label(rows, cli_quarter=None):
    """Quarter label for exception IDs, shared by every producer script
    so the same filing always derives the same label regardless of
    which script is deriving it. Real fetch_edgar.py-sourced rows carry
    _source_period_of_report automatically -- use it, so the common
    case needs no extra argument. Falls back to a CLI-supplied label,
    then to a warned placeholder. Never silently guesses: a collision-
    prone placeholder is flagged loudly, not hidden, because exception
    IDs from different quarters colliding would silently suppress a
    genuinely new issue as "already resolved"."""
    if cli_quarter:
        return cli_quarter
    if rows and rows[0].get("_source_period_of_report"):
        return rows[0]["_source_period_of_report"]
    print("  WARNING: no quarter label available (not sourced via fetch_edgar.py, "
          "none supplied) -- using 'unknown_quarter' for resolution-log exception "
          "IDs. These may collide across different quarters' runs; supply a real "
          "quarter label if you're tracking human resolutions across quarters.")
    return "unknown_quarter"


def record_resolution(exception_id, decision, reviewer, note=None, correction=None,
                       log_file=LOG_FILE):
    """Appends one resolution record. Never overwrites a prior entry for
    the same exception_id -- if the same exception is resolved twice
    (e.g. re-reviewed after new information), both entries stay in the
    log; is_resolved() / get_resolution() use the most recent one, but
    the full history is still there for anyone who wants it."""
    decision = decision.upper()
    if decision not in VALID_DECISIONS:
        raise ValueError(f"decision must be one of {VALID_DECISIONS}, got {decision!r}")

    record = {
        "exception_id": exception_id,
        "decision": decision,
        "reviewer": reviewer,
        "note": note,
        "correction": correction,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a") as f:
        f.write(json.dumps(record) + "\n")

    return record


def load_all_resolutions(log_file=LOG_FILE):
    """Returns {exception_id: most_recent_record}. Returns {} if the
    log doesn't exist yet -- an empty log is a normal starting state,
    not an error condition."""
    if not Path(log_file).exists():
        return {}

    latest = {}
    with open(log_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            # Later lines in an append-only file are more recent --
            # last one wins for a given exception_id.
            latest[record["exception_id"]] = record
    return latest


def is_resolved(exception_id, log_file=LOG_FILE):
    return exception_id in load_all_resolutions(log_file)


def get_resolution(exception_id, log_file=LOG_FILE):
    return load_all_resolutions(log_file).get(exception_id)


def annotate_with_resolutions(items, exception_id_fn, log_file=LOG_FILE):
    """Convenience for producer scripts: given a list of flagged items
    and a function that derives each item's exception_id, returns the
    items with a "resolution" field added (None if never resolved,
    else the resolution record). Only annotates -- never filters or
    suppresses. Each producer decides what to do with an already-
    resolved item; that decision differs by check type, so it doesn't
    belong in this shared module."""
    resolutions = load_all_resolutions(log_file)
    annotated = []
    for item in items:
        eid = exception_id_fn(item)
        item = dict(item)
        item["exception_id"] = eid
        item["resolution"] = resolutions.get(eid)
        annotated.append(item)
    return annotated


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python resolution_log.py list")
        print("  python resolution_log.py resolve <exception_id> <APPROVE|ESCALATE> <reviewer> [note]")
        print("  python resolution_log.py resolve <exception_id> CORRECT <reviewer> <correction_value> [note]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        resolutions = load_all_resolutions()
        if not resolutions:
            print("No resolutions recorded yet.")
        for eid, r in resolutions.items():
            print(f"  {eid}")
            print(f"    {r['decision']} by {r['reviewer']} at {r['timestamp']}")
            if r.get("note"):
                print(f"    note: {r['note']}")
            if r.get("correction"):
                print(f"    correction: {r['correction']}")

    elif command == "resolve":
        if len(sys.argv) < 5:
            print("Usage: python resolution_log.py resolve <exception_id> <APPROVE|ESCALATE> <reviewer> [note]")
            print("       python resolution_log.py resolve <exception_id> CORRECT <reviewer> <correction_value> [note]")
            sys.exit(1)
        exception_id = sys.argv[2]
        decision = sys.argv[3]
        reviewer = sys.argv[4]
        # CORRECT requires a distinct correction_value positional arg,
        # separate from note -- found broken (never actually wired,
        # not a regression: unchanged since the initial commit) while
        # running the real CLI end to end on Melqart's real Chart
        # Industries/EA corrections: record_resolution() and every
        # downstream consumer (import_bloomberg_data.py's CORRECT-
        # application logic) already read a distinct `correction`
        # field, but this CLI only ever parsed 4 positional args and
        # silently dropped the correction value into `note`, leaving
        # `correction` permanently None for every CLI-driven CORRECT
        # resolution regardless of what was actually typed. APPROVE and
        # ESCALATE don't need a correction value, so they keep the
        # simpler [note]-only form.
        if decision.upper() == "CORRECT":
            if len(sys.argv) < 6:
                print("CORRECT requires a correction value: "
                      "python resolution_log.py resolve <exception_id> CORRECT <reviewer> <correction_value> [note]")
                sys.exit(1)
            correction = sys.argv[5]
            note = sys.argv[6] if len(sys.argv) > 6 else None
        else:
            correction = None
            note = sys.argv[5] if len(sys.argv) > 5 else None
        record = record_resolution(exception_id, decision, reviewer, note=note, correction=correction)
        print(f"Recorded: {record}")

    else:
        print(f"Unknown command: {command!r}. Use 'list' or 'resolve'.")
        sys.exit(1)
