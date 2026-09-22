#!/usr/bin/env python3
"""
vlr_vct_scraper.py
-------------------
Scrapes all VCT match data for a given season (default: 2026) from vlr.gg,
including Kickoff, Stage 1, Stage 2, Masters, and Champions events.

Output: CSV and/or JSON, ready to load into a relational database.

USAGE
-----
    python vlr_vct_scraper.py                          # scrape everything for 2026
    python vlr_vct_scraper.py --year 2026 --delay 2     # be extra polite to the server
    python vlr_vct_scraper.py --detailed                # also scrape per-map scores,
                                                          # patch, and pick/ban (slower,
                                                          # 1 extra request per match)
    python vlr_vct_scraper.py --events 2683,2684        # only scrape specific event IDs
    python vlr_vct_scraper.py --list-events             # just print discovered events, don't scrape

OUTPUT FILES (written to ./output/)
    events.csv / events.json        -> one row per event (id, name, stage, region, dates, prize)
    matches.csv / matches.json      -> one row per match  (teams, scores, date, round, event, url)
    maps.csv / maps.json            -> one row per map played (only with --detailed)
    player_stats.csv / .json        -> one row per player, per map (ACS, K/D/A, ADR, KAST,
                                        HS%, FK/FD, agent(s), rating) (only with --detailed)

NOTES
-----
- This relies on vlr.gg's current page structure (class names below). VLR
  redesigns occasionally -- if a run comes back with 0 matches, the site's
  HTML has likely changed and the CSS selectors in `parse_match_list_page()`
  or `parse_match_detail_page()` need a quick update.
- Please be a good citizen: keep --delay at 1-2 seconds. This script makes
  one request per event for the match list, plus (optionally) one request
  per match for details. For a full VCT season that's ~15 event requests,
  or several hundred if --detailed is used.
- Requires: requests, beautifulsoup4  (pip install requests beautifulsoup4)
"""

import argparse
import csv
import json
import re
import sys
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

BASE = "https://www.vlr.gg"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; personal-vct-data-project/1.0; "
                  "+https://vlr.gg) requests-python"
}

# vlr.gg's internal "stage" filter IDs used on /vct — covers a full season
STAGE_IDS = {
    "kickoff": 45,
    "stage1": 1,
    "masters": 46,
    "stage2": 16,
    "champions": 47,
}


# --------------------------------------------------------------------------
# Data models
# --------------------------------------------------------------------------

@dataclass
class Event:
    event_id: str
    name: str
    slug: str
    stage: str          # Kickoff / Stage 1 / Masters / Stage 2 / Champions (best guess from name)
    region: str          # Americas / EMEA / Pacific / China / International
    status: str          # upcoming / ongoing / completed
    dates: str
    prize_pool: str
    url: str


@dataclass
class Match:
    match_id: str
    event_id: str
    event_name: str
    stage: str
    region: str
    date_label: str       # e.g. "Sun, February 15, 2026" (as shown on page, event-local grouping)
    time_label: str       # e.g. "2:00 AM"
    round_name: str       # e.g. "Lower Final"
    sub_event: str        # e.g. "Main Event" / "Playoffs" / "Group Stage"
    team1: str
    team2: str
    score1: Optional[str]
    score2: Optional[str]
    status: str            # Completed / LIVE / Upcoming
    url: str


@dataclass
class MapResult:
    match_id: str
    map_number: int
    map_name: str
    team1_score: Optional[str]
    team2_score: Optional[str]
    winner: Optional[str]


@dataclass
class PlayerMapStat:
    match_id: str
    map_number: int
    map_name: str
    team: str
    team_tag: str            # e.g. "VL", "GEN" -- as shown next to the player's name
    player: str
    player_id: str            # vlr.gg numeric player id, useful as a join key
    country: str
    agents: str                # "/"-joined if the player swapped agents mid-map
    rating: Optional[str]
    acs: Optional[str]
    kills: Optional[str]
    deaths: Optional[str]
    assists: Optional[str]
    plus_minus: Optional[str]   # K-D
    kast: Optional[str]
    adr: Optional[str]
    hs_pct: Optional[str]
    fk: Optional[str]           # first kills ("first bloods" on vlr.gg)
    fd: Optional[str]           # first deaths
    fk_fd_diff: Optional[str]


# --------------------------------------------------------------------------
# Networking helper
# --------------------------------------------------------------------------

def fetch(url: str, delay: float) -> Optional[BeautifulSoup]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        time.sleep(delay)
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as e:
        print(f"  [warn] failed to fetch {url}: {e}", file=sys.stderr)
        return None


# --------------------------------------------------------------------------
# Step 1: discover events for the season
# --------------------------------------------------------------------------

def discover_events(year: int, delay: float) -> list[Event]:
    """
    Pulls the event list from https://www.vlr.gg/vct/?stage=all&region=all
    (for the current season) which lists every Kickoff/Stage/Masters/Champions
    event with its id, name, dates, prize pool and status.
    """
    url = f"{BASE}/vct/?stage=all&region=all"
    print(f"Discovering events: {url}")
    soup = fetch(url, delay)
    if soup is None:
        return []

    events: list[Event] = []

    # Event cards are anchor tags linking to /event/{id}/{slug}
    for a in soup.select("a[href^='/event/']"):
        href = a.get("href", "")
        m = re.match(r"^/event/(\d+)/([\w-]+)/?$", href)
        if not m:
            continue
        event_id, slug = m.group(1), m.group(2)

        text = a.get_text(" ", strip=True)
        # e.g. "VCT 2026: Pacific Kickoff completed Status $0 Prize Pool Jan 22—Feb 15 Dates Region"
        name_match = re.match(r"^(.*?)(upcoming|ongoing|completed)", text)
        name = name_match.group(1).strip() if name_match else text
        status_match = re.search(r"\b(upcoming|ongoing|completed)\b", text)
        status = status_match.group(1) if status_match else ""

        if str(year) not in name:
            continue

        prize_match = re.search(r"(\$[\d,]+|\$0|TBD)\s*Prize Pool", text)
        prize = prize_match.group(1) if prize_match else ""

        dates_match = re.search(r"Prize Pool\s*(.*?)\s*Dates", text)
        dates = dates_match.group(1).strip() if dates_match else ""

        region = "International"
        for r in ("Americas", "EMEA", "China", "Pacific"):
            if r.lower() in name.lower():
                region = r
                break

        stage = "Other"
        for key, label in (
            ("kickoff", "Kickoff"),
            ("stage 1", "Stage 1"),
            ("stage1", "Stage 1"),
            ("stage 2", "Stage 2"),
            ("stage2", "Stage 2"),
            ("masters", "Masters"),
            ("champions", "Champions"),
        ):
            if key in name.lower():
                stage = label
                break

        # avoid duplicates (same event linked twice on the page)
        if any(e.event_id == event_id for e in events):
            continue

        events.append(Event(
            event_id=event_id,
            name=name,
            slug=slug,
            stage=stage,
            region=region,
            status=status,
            dates=dates,
            prize_pool=prize,
            url=f"{BASE}{href}",
        ))

    print(f"  found {len(events)} events for {year}")
    return events


# --------------------------------------------------------------------------
# Step 2: scrape the match list for one event
# --------------------------------------------------------------------------

def parse_match_list_page(soup: BeautifulSoup, event: Event) -> list[Match]:
    matches: list[Match] = []

    # Matches are grouped under date headers (wf-label mod-large) inside
    # wf-card containers; each match is an <a class="match-item">.
    current_date = ""
    for el in soup.select(".wf-label.mod-large, a.match-item"):
        classes = el.get("class", [])
        if "wf-label" in classes:
            current_date = el.get_text(strip=True)
            continue

        href = el.get("href", "")
        m = re.match(r"^/(\d+)/([\w-]+)/?$", href)
        if not m:
            continue
        match_id, slug = m.group(1), m.group(2)

        time_el = el.select_one(".match-item-time")
        time_label = time_el.get_text(strip=True) if time_el else ""

        team_els = el.select(".match-item-vs-team")
        team_names, team_scores = [], []
        for t in team_els:
            name_el = t.select_one(".match-item-vs-team-name")
            score_el = t.select_one(".match-item-vs-team-score")
            team_names.append(name_el.get_text(strip=True) if name_el else "")
            score_text = score_el.get_text(strip=True) if score_el else ""
            team_scores.append(score_text if score_text not in ("", "–", "-") else None)

        while len(team_names) < 2:
            team_names.append("")
        while len(team_scores) < 2:
            team_scores.append(None)

        status_el = el.select_one(".ml-status, .match-item-eta .ml-eta, .match-item-eta")
        status = status_el.get_text(strip=True) if status_el else ""
        # status text often contains countdown/time-ago glued on; normalize
        status_clean = "Completed" if "Completed" in status else (
            "LIVE" if "LIVE" in status.upper() else "Upcoming"
        )

        round_el = el.select_one(".match-item-event-series")
        round_name = round_el.get_text(strip=True) if round_el else ""

        subevent_el = el.select_one(".match-item-event")
        sub_event = subevent_el.get_text(" ", strip=True) if subevent_el else ""
        # the event name is often duplicated inside; strip the round text if present
        if round_name and round_name in sub_event:
            sub_event = sub_event.replace(round_name, "").strip()

        matches.append(Match(
            match_id=match_id,
            event_id=event.event_id,
            event_name=event.name,
            stage=event.stage,
            region=event.region,
            date_label=current_date,
            time_label=time_label,
            round_name=round_name,
            sub_event=sub_event,
            team1=team_names[0],
            team2=team_names[1],
            score1=team_scores[0],
            score2=team_scores[1],
            status=status_clean,
            url=f"{BASE}{href}",
        ))

    return matches


def scrape_event_matches(event: Event, delay: float) -> list[Match]:
    url = f"{BASE}/event/matches/{event.event_id}/{event.slug}/?group=all"
    print(f"  scraping matches: {event.name}  ({url})")
    soup = fetch(url, delay)
    if soup is None:
        return []
    matches = parse_match_list_page(soup, event)
    print(f"    -> {len(matches)} matches found")
    return matches


# --------------------------------------------------------------------------
# Step 3 (optional): scrape per-map scores AND per-player box scores from
# an individual match page
# --------------------------------------------------------------------------

def _clean_map_name(raw: str) -> str:
    # raw text looks like "1 Ascent PICK" or "2 Bind" -- strip leading map
    # number and trailing PICK/DECIDER/BAN tag
    raw = re.sub(r"^\d+\s*", "", raw)
    raw = re.sub(r"\b(PICK|BAN|DECIDER)\b", "", raw, flags=re.I)
    return raw.strip()


def _cell_value(cell) -> Optional[str]:
    """Grab the 'all rounds' value from an .ovw-cell: <span class='side mod-both'>"""
    if cell is None:
        return None
    span = cell.select_one(".side.mod-both")
    text = span.get_text(strip=True) if span else cell.get_text(strip=True)
    return text if text not in ("", "-", "–") else None


def parse_map_player_stats(map_div, match_id: str, map_num: int, map_name: str,
                            team1: str, team2: str) -> list[PlayerMapStat]:
    stats: list[PlayerMapStat] = []

    ovw_tables = map_div.select(".ovw-table")
    for table_idx, table in enumerate(ovw_tables):
        team = team1 if table_idx == 0 else team2

        for row in table.select(".ovw-row"):
            if "mod-head" in row.get("class", []):
                continue

            player_block = row.select_one(".ovw-player")
            if player_block is None:
                continue

            link = player_block.select_one("a")
            href = link.get("href", "") if link else ""
            m = re.search(r"/player/(\d+)/", href)
            player_id = m.group(1) if m else ""

            name_el = player_block.select_one(".ovw-player-name")
            player_name = name_el.get_text(strip=True) if name_el else ""

            tag_el = player_block.select_one(".ovw-player-tag")
            team_tag = tag_el.get_text(strip=True) if tag_el else ""

            flag_el = player_block.select_one(".flag")
            country = flag_el.get("title", "") if flag_el else ""

            agents = []
            for span in row.select(".ovw-agents span.mod-agent"):
                img = span.find("img")
                if img and img.get("title"):
                    agents.append(img["title"].strip())
            agents_str = "/".join(agents)

            rating = _cell_value(row.select_one("[data-col='rating2']"))
            acs = _cell_value(row.select_one("[data-col='acs']"))
            kills = _cell_value(row.select_one("[data-col='kills']"))
            deaths = _cell_value(row.select_one("[data-col='deaths']"))
            assists = _cell_value(row.select_one("[data-col='assists']"))
            plus_minus = _cell_value(row.select_one("[data-col='kd-diff']"))
            kast = _cell_value(row.select_one("[data-col='kast']"))
            adr = _cell_value(row.select_one("[data-col='adr']"))
            hs_pct = _cell_value(row.select_one("[data-col='hsp']"))
            fk = _cell_value(row.select_one("[data-col='fb']"))
            fd = _cell_value(row.select_one("[data-col='fd']"))
            fk_fd_diff = _cell_value(row.select_one("[data-col='fk-diff']"))

            stats.append(PlayerMapStat(
                match_id=match_id,
                map_number=map_num,
                map_name=map_name,
                team=team,
                team_tag=team_tag,
                player=player_name,
                player_id=player_id,
                country=country,
                agents=agents_str,
                rating=rating,
                acs=acs,
                kills=kills,
                deaths=deaths,
                assists=assists,
                plus_minus=plus_minus,
                kast=kast,
                adr=adr,
                hs_pct=hs_pct,
                fk=fk,
                fd=fd,
                fk_fd_diff=fk_fd_diff,
            ))

    return stats


def parse_match_detail_page(soup: BeautifulSoup, match_id: str,
                             team1: str = "", team2: str = ""):
    """Returns (list[MapResult], list[PlayerMapStat]) for one match page."""
    maps: list[MapResult] = []
    player_stats: list[PlayerMapStat] = []
    map_num = 0

    for map_div in soup.select(".vm-stats-game"):
        game_id = map_div.get("data-game-id", "")
        if game_id == "all":
            continue
        map_num += 1

        name_el = map_div.select_one(".map div > span, .map")
        map_name = _clean_map_name(name_el.get_text(" ", strip=True)) if name_el else ""

        score_els = map_div.select(".score")
        scores = [s.get_text(strip=True) for s in score_els if s.get_text(strip=True)]
        t1_score = scores[0] if len(scores) > 0 else None
        t2_score = scores[1] if len(scores) > 1 else None

        winner = None
        try:
            if t1_score is not None and t2_score is not None:
                winner = "team1" if int(t1_score) > int(t2_score) else "team2"
        except ValueError:
            pass

        maps.append(MapResult(
            match_id=match_id,
            map_number=map_num,
            map_name=map_name,
            team1_score=t1_score,
            team2_score=t2_score,
            winner=winner,
        ))

        player_stats.extend(parse_map_player_stats(map_div, match_id, map_num, map_name, team1, team2))

    return maps, player_stats


def scrape_match_detail(match: Match, delay: float):
    soup = fetch(match.url, delay)
    if soup is None:
        return [], []
    return parse_match_detail_page(soup, match.match_id, match.team1, match.team2)


# --------------------------------------------------------------------------
# Output helpers
# --------------------------------------------------------------------------

def read_existing_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def upsert_rows(existing: list[dict], new: list[dict], key_fields: tuple[str, ...]) -> list[dict]:
    """Merge new rows into existing rows, replacing any existing row whose
    key matches a new row (so updated scores/status win), keeping untouched
    existing rows, and appending genuinely new ones. Order: existing rows
    first (with replacements applied in place), then brand-new rows."""
    def key(row: dict):
        return tuple(row.get(f, "") for f in key_fields)

    new_by_key = {key(r): r for r in new}
    merged: list[dict] = []
    seen_keys = set()

    for row in existing:
        k = key(row)
        if k in new_by_key:
            merged.append(new_by_key[k])
        else:
            merged.append(row)
        seen_keys.add(k)

    for r in new:
        k = key(r)
        if k not in seen_keys:
            merged.append(r)
            seen_keys.add(k)

    return merged


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        print(f"  [skip] no rows for {path.name}")
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  wrote {path}  ({len(rows)} rows)")


def write_json(path: Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print(f"  wrote {path}  ({len(rows)} rows)")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Scrape VCT season match data from vlr.gg")
    parser.add_argument("--year", type=int, default=2026, help="Season year (default: 2026)")
    parser.add_argument("--delay", type=float, default=1.5, help="Seconds to wait between requests (default: 1.5)")
    parser.add_argument("--detailed", action="store_true",
                         help="Also scrape per-map scores for every match (1 extra request per match)")
    parser.add_argument("--events", type=str, default=None,
                         help="Comma-separated event IDs to scrape instead of auto-discovering (e.g. 2683,2684)")
    parser.add_argument("--list-events", action="store_true",
                         help="Only discover and print/save events, skip match scraping")
    parser.add_argument("--out", type=str, default="output", help="Output directory (default: ./output)")
    parser.add_argument("--format", choices=["csv", "json", "both"], default="both")
    parser.add_argument("--update", action="store_true",
                         help="Incremental mode: skip re-scraping match detail (maps/player_stats) "
                              "for matches you already have from a previous run in --out. Only new "
                              "matches, and matches that just finished, get scraped. Requires "
                              "--detailed. events.csv/matches.csv are still refreshed each run "
                              "(cheap: one request per event) so statuses/scores stay current.")
    parser.add_argument("--debug-match", type=str, default=None,
                         help="Fetch a single match URL, dump raw HTML to debug_match.html, "
                              "and print how many map/player rows were parsed from it. "
                              "Use this first if --detailed comes back with 0 player rows.")
    args = parser.parse_args()

    if args.debug_match:
        resp = requests.get(args.debug_match, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        Path("debug_match.html").write_text(resp.text, encoding="utf-8")
        soup = BeautifulSoup(resp.text, "html.parser")
        # try to pull team names off the page itself for a standalone debug run
        team_els = soup.select(".match-header-link-name .wf-title-med")
        t1 = team_els[0].get_text(strip=True) if len(team_els) > 0 else "team1"
        t2 = team_els[1].get_text(strip=True) if len(team_els) > 1 else "team2"
        maps, player_stats = parse_match_detail_page(soup, "debug", t1, t2)
        print(f"Saved raw HTML to debug_match.html")
        print(f"Parsed {len(maps)} maps, {len(player_stats)} player-map rows")
        for m in maps:
            print(f"  {m.map_name}: {m.team1_score}-{m.team2_score}")
        for p in player_stats[:5]:
            print(f"  {p.player} ({p.team}, {p.agents}) ACS={p.acs} K/D/A={p.kills}/{p.deaths}/{p.assists}")
        if not player_stats:
            n_game_divs = len(soup.select(".vm-stats-game"))
            n_tables = len(soup.select("table.wf-table-inset"))
            print(f"\n0 player rows parsed. Diagnostics: found {n_game_divs} '.vm-stats-game' "
                  f"map container(s) and {n_tables} 'table.wf-table-inset' table(s) total on the page.")
            if n_game_divs == 0:
                print("  -> The map-container selector itself found nothing. vlr.gg likely renamed "
                      "'.vm-stats-game'. Open debug_match.html, search for the block that holds the "
                      "map tabs/scores, and send me its class name.")
            elif n_tables == 0:
                print("  -> Map containers found, but no 'wf-table-inset' tables inside them. vlr.gg "
                      "likely renamed the stats table class. Search debug_match.html for the player "
                      "stat table and send me its class name.")
            else:
                print("  -> Tables were found but row parsing failed (e.g. player link/column layout "
                      "changed). Open debug_match.html, find one <tr> for a player row, and send me "
                      "its raw HTML.")
        return

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    events = discover_events(args.year, args.delay)

    if args.events:
        wanted = set(x.strip() for x in args.events.split(","))
        events = [e for e in events if e.event_id in wanted]
        print(f"Filtered to {len(events)} requested event(s)")

    if not events:
        print("No events found/matched -- nothing to do. "
              "If this is unexpected, vlr.gg's page structure may have changed.")
        sys.exit(1)

    event_rows = [asdict(e) for e in events]
    if args.format in ("csv", "both"):
        write_csv(out_dir / "events.csv", event_rows)
    if args.format in ("json", "both"):
        write_json(out_dir / "events.json", event_rows)

    if args.list_events:
        for e in events:
            print(f"  [{e.event_id}] {e.name}  ({e.stage}, {e.region}, {e.status})")
        return

    all_matches: list[Match] = []
    for event in events:
        all_matches.extend(scrape_event_matches(event, args.delay))

    match_rows = [asdict(m) for m in all_matches]
    if args.update:
        existing_match_rows = read_existing_csv(out_dir / "matches.csv")
        match_rows = upsert_rows(existing_match_rows, match_rows, key_fields=("match_id",))
    if args.format in ("csv", "both"):
        write_csv(out_dir / "matches.csv", match_rows)
    if args.format in ("json", "both"):
        write_json(out_dir / "matches.json", match_rows)

    if args.detailed:
        already_detailed_ids: set[str] = set()
        existing_map_rows: list[dict] = []
        existing_player_rows: list[dict] = []
        if args.update:
            existing_map_rows = read_existing_csv(out_dir / "maps.csv")
            existing_player_rows = read_existing_csv(out_dir / "player_stats.csv")
            already_detailed_ids = {r["match_id"] for r in existing_map_rows}
            print(f"\n--update: {len(already_detailed_ids)} match(es) already have detail scraped "
                  f"in {out_dir}/ -- these will be skipped.")

        to_scrape = [
            m for m in all_matches
            if m.status == "Completed" and m.match_id not in already_detailed_ids
        ]

        print(f"Scraping map + player detail for {len(to_scrape)} match(es) "
              f"(this will take ~{len(to_scrape) * args.delay / 60:.1f} min at --delay {args.delay})...")
        new_maps: list[MapResult] = []
        new_player_stats: list[PlayerMapStat] = []
        for i, match in enumerate(to_scrape, 1):
            print(f"  [{i}/{len(to_scrape)}] {match.team1} vs {match.team2}")
            maps, player_stats = scrape_match_detail(match, args.delay)
            new_maps.extend(maps)
            new_player_stats.extend(player_stats)

        map_rows = [asdict(m) for m in new_maps]
        player_rows = [asdict(p) for p in new_player_stats]

        if args.update:
            map_rows = upsert_rows(existing_map_rows, map_rows, key_fields=("match_id", "map_number"))
            player_rows = upsert_rows(existing_player_rows, player_rows,
                                       key_fields=("match_id", "map_number", "player_id"))

        if args.format in ("csv", "both"):
            write_csv(out_dir / "maps.csv", map_rows)
        if args.format in ("json", "both"):
            write_json(out_dir / "maps.json", map_rows)

        if args.format in ("csv", "both"):
            write_csv(out_dir / "player_stats.csv", player_rows)
        if args.format in ("json", "both"):
            write_json(out_dir / "player_stats.json", player_rows)

        print(f"  newly scraped matches: {len(to_scrape)}")
        print(f"  total player-map rows in output: {len(player_rows)}")

    print("\nDone.")
    print(f"  events:  {len(events)}")
    print(f"  matches: {len(all_matches)}")


if __name__ == "__main__":
    main()
