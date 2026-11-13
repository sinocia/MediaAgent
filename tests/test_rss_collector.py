from datetime import datetime, timezone

import pytest

from app.collectors.rss import FeedError, fetch_feed, parse_feed
from app.database import Base, make_engine
from app.models import Topic
from sqlalchemy.orm import Session


def test_parse_rss_keeps_source_and_missing_popularity_missing():
    xml = """<rss version="2.0"><channel><item><title>Topic A</title>
    <link>https://example.com/a</link><guid>a-1</guid>
    <pubDate>Mon, 12 Oct 2026 02:00:00 +0000</pubDate></item></channel></rss>"""
    captured = datetime(2026, 10, 12, tzinfo=timezone.utc)
    records = parse_feed(xml, source="example-rss", feed_url="https://example.com/feed", captured_at=captured)
    assert len(records) == 1
    assert records[0].title == "Topic A"
    assert records[0].source_url == "https://example.com/a"
    assert records[0].external_id == "a-1"
    assert records[0].captured_at == captured
    assert not hasattr(records[0], "trend_score")


def test_parse_atom_feed():
    xml = """<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Atom</title>
    <id>tag:example.com,2026:1</id><link href="https://example.com/atom"/>
    <updated>2026-10-12T02:00:00Z</updated></entry></feed>"""
    record = parse_feed(xml, source="atom", feed_url="https://example.com/atom-feed")[0]
    assert record.title == "Atom"
    assert record.published_at == datetime(2026, 10, 12, 2, tzinfo=timezone.utc)


def test_invalid_xml_and_non_https_fetch_are_rejected():
    with pytest.raises(FeedError, match="Invalid"):
        parse_feed("<not-closed>", source="x", feed_url="https://example.com/feed")
    with pytest.raises(FeedError, match="HTTPS"):
        fetch_feed("http://example.com/feed", source="x")


def test_save_topics_is_idempotent_including_duplicates_in_one_batch():
    from app.collectors.rss import save_topics

    engine = make_engine("sqlite://")
    Base.metadata.create_all(engine)
    timestamp = datetime(2026, 10, 12, tzinfo=timezone.utc)
    item = parse_feed("""<rss><channel><item><title>One</title><link>https://e.test/1</link>
    <guid>one</guid></item></channel></rss>""", source="feed", feed_url="https://e.test/rss",
                      captured_at=timestamp)[0]
    with Session(engine) as session:
        assert save_topics(session, [item, item]) == 1
        session.commit()
        assert save_topics(session, [item]) == 0
        assert session.query(Topic).count() == 1
    engine.dispose()
