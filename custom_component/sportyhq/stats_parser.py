"""HTML parsing for the SportyHQ /my_stats page (no Home Assistant imports)."""
import re

from bs4 import BeautifulSoup

_LABEL_KEYS = {
    "sportyhq rating": "sportyhq_rating",
    "rating confidence": "rating_confidence",
    "matches ytd": "matches_ytd",
    "matches all time": "matches_all_time",
}


def _parse_profile_layout(soup) -> dict:
    """Current layout (2026-11): shq-profile-* profile page."""
    data = {}

    # Several .shq-profile-primary-number elements exist (some hidden/empty
    # placeholders, others for different ratings), so anchor on the article
    # titled "SportyHQ Rating".
    scope = soup
    for strong in soup.find_all("strong"):
        if strong.get_text(strip=True).lower() == "sportyhq rating":
            scope = strong.find_parent("article") or scope
            break

    number = next(
        (n for n in scope.select(".shq-profile-primary-number") if n.get_text(strip=True)),
        None,
    )
    if number:
        data["sportyhq_rating"] = number.get_text(strip=True)

    note = scope.select_one(".shq-profile-rating-note")
    if note:
        text = note.get_text(" ", strip=True)
        change = re.search(r"Last change:\s*[-+−]?\s*\d+(?:\.\d+)?\s*points?", text, re.I)
        if change:
            data["rating_last_change"] = change.group().strip()
        conf = re.search(r"Rating confidence\s*:?\s*(\d+(?:\.\d+)?)\s*%", text, re.I)
        if conf:
            data["rating_confidence"] = conf.group(1) + "%"

    for hl in soup.select(".shq-profile-highlight"):
        label = hl.select_one(".shq-profile-highlight-label")
        value = hl.select_one(".shq-profile-highlight-value")
        if label and value and re.match(r"matches in \d{4}$", label.get_text(strip=True), re.I):
            data["matches_ytd"] = value.get_text(strip=True)
            break

    for dt in soup.find_all("dt"):
        if dt.get_text(strip=True).lower().rstrip(":") == "matches all time":
            dd = dt.find_next_sibling("dd")
            if dd:
                data["matches_all_time"] = dd.get_text(strip=True)
            break

    return data


def _parse_metric_layout(soup) -> dict:
    """Previous layout: div.shq-metric cards."""
    data = {}
    for card in soup.select("div.shq-metric"):
        label = card.select_one(".shq-metric-label")
        value = card.select_one(".shq-metric-value")
        if label and value:
            key = _LABEL_KEYS.get(label.get_text(strip=True).lower())
            if key:
                data[key] = value.get_text(strip=True)
                if key == "sportyhq_rating":
                    detail = card.select_one(".shq-metric-detail")
                    if detail:
                        data["rating_last_change"] = detail.get_text(strip=True)
    return data


def _parse_legacy_layout(soup) -> dict:
    """Oldest layout: positional cards with <h6> values."""
    try:
        group = soup.find("div", class_="card-group mb-4")
        if group:
            cards = group.find_all("div", class_="card")
            return {
                "sportyhq_rating": cards[0].find("h6").text,
                "rating_confidence": cards[1].find("h6").text,
                "matches_ytd": cards[2].find("h6").text,
                "matches_all_time": cards[3].find("h6").text,
            }
    except (AttributeError, IndexError):
        pass
    return {}


def parse_stats(html: str) -> dict:
    """Return whatever stats can be extracted, trying newest layout first."""
    soup = BeautifulSoup(html, "html.parser")
    for parser in (_parse_profile_layout, _parse_metric_layout, _parse_legacy_layout):
        data = parser(soup)
        if data.get("sportyhq_rating"):
            return data
    return {}
