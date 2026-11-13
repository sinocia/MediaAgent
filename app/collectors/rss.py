"""Parse explicitly configured public RSS/Atom feeds without login or scraping."""

from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.error import URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Topic


ATOM = "{http://www.w3.org/2005/Atom}"


@dataclass(frozen=True)
class CollectedTopic:
    title: str
    source: str
    source_url: str
    external_id: str
    published_at: datetime | None
    captured_at: datetime


class FeedError(ValueError):
    """Raised when a feed cannot be safely fetched or parsed."""


def _child_text(element: ElementTree.Element, *names: str) -> str | None:
    for name in names:
        node = element.find(name)
        if node is not None and node.text and node.text.strip():
            return node.text.strip()
    return None


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError, OverflowError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_feed(xml: bytes | str, *, source: str, feed_url: str,
               captured_at: datetime | None = None) -> list[CollectedTopic]:
    """Parse RSS 2.0 or Atom entries; missing popularity values remain absent."""
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError as exc:
        raise FeedError("Invalid RSS/Atom XML") from exc
    capture_time = captured_at or datetime.now(timezone.utc)
    if capture_time.tzinfo is None:
        capture_time = capture_time.replace(tzinfo=timezone.utc)
    capture_time = capture_time.astimezone(timezone.utc)

    if root.tag == f"{ATOM}feed":
        entries = root.findall(f"{ATOM}entry")
        records = []
        for entry in entries:
            title = _child_text(entry, f"{ATOM}title")
            identifier = _child_text(entry, f"{ATOM}id")
            link_node = entry.find(f"{ATOM}link")
            link = link_node.get("href") if link_node is not None else None
            url = link or identifier
            if title and url:
                records.append(CollectedTopic(title, source, url, identifier or url,
                    _parse_date(_child_text(entry, f"{ATOM}published", f"{ATOM}updated")), capture_time))
        return records

    items = root.findall("./channel/item")
    records = []
    for item in items:
        title = _child_text(item, "title")
        link = _child_text(item, "link")
        guid = _child_text(item, "guid")
        url = link or guid
        if title and url:
            records.append(CollectedTopic(title, source, url, guid or url,
                _parse_date(_child_text(item, "pubDate", "published", "updated")), capture_time))
    return records


def fetch_feed(feed_url: str, *, source: str, timeout_seconds: float = 10,
               max_bytes: int = 2_000_000) -> list[CollectedTopic]:
    """Fetch a configured public feed with bounded time/size and a descriptive user agent."""
    if not feed_url.startswith("https://"):
        raise FeedError("Only HTTPS feed URLs are allowed")
    request = Request(feed_url, headers={"User-Agent": "AI-Media-Agent/0.1 (public RSS reader)"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = response.read(max_bytes + 1)
    except (URLError, TimeoutError, OSError) as exc:
        raise FeedError("Unable to fetch configured feed") from exc
    if len(payload) > max_bytes:
        raise FeedError("Feed exceeds maximum allowed size")
    return parse_feed(payload, source=source, feed_url=feed_url)


def save_topics(session: Session, records: list[CollectedTopic]) -> int:
    """Insert unseen feed items; the database unique key is the final idempotency guard."""
    inserted = 0
    seen: set[tuple[str, str]] = set()
    for record in records:
        key = (record.source, record.external_id)
        if key in seen:
            continue
        seen.add(key)
        existing = session.scalar(select(Topic.id).where(
            Topic.source == record.source, Topic.external_id == record.external_id))
        if existing is not None:
            continue
        session.add(Topic(title=record.title, source=record.source, source_url=record.source_url,
                          external_id=record.external_id, published_at=record.published_at,
                          captured_at=record.captured_at))
        inserted += 1
    session.flush()
    return inserted
