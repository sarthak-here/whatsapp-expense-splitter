import pytest
from backend.parser import (
    parse_whatsapp_chat,
    extract_members,
    get_date_range,
    messages_by_sender,
    count_messages_per_sender,
)

ANDROID_CHAT = """\
25/04/2024, 10:02 am - Rahul: Good morning!
25/04/2024, 10:05 am - Priya: Can't wait
27/04/2024, 08:00 am - Aakash: All settled now
"""

IOS_CHAT = """\
[25/04/2024, 10:02 AM] Rahul: Good morning!
[25/04/2024, 10:05 AM] Priya: Can't wait
"""

SYSTEM_CHAT = """\
25/04/2024, 09:00 am - Messages and calls are end-to-end encrypted.
25/04/2024, 10:02 am - Rahul: Hey everyone
25/04/2024, 10:05 am - Priya: Hi!
"""


class TestAndroidFormat:
    def test_message_count(self):
        msgs = parse_whatsapp_chat(ANDROID_CHAT)
        assert len(msgs) == 3

    def test_sender_names(self):
        msgs = parse_whatsapp_chat(ANDROID_CHAT)
        assert msgs[0].sender == "Rahul"
        assert msgs[1].sender == "Priya"
        assert msgs[2].sender == "Aakash"

    def test_message_content(self):
        msgs = parse_whatsapp_chat(ANDROID_CHAT)
        assert msgs[0].content == "Good morning!"

    def test_timestamp_parsed(self):
        msgs = parse_whatsapp_chat(ANDROID_CHAT)
        assert msgs[0].timestamp is not None


class TestIosFormat:
    def test_message_count(self):
        msgs = parse_whatsapp_chat(IOS_CHAT)
        assert len(msgs) == 2

    def test_sender_names(self):
        msgs = parse_whatsapp_chat(IOS_CHAT)
        assert msgs[0].sender == "Rahul"
        assert msgs[1].sender == "Priya"


class TestSystemMessageFiltering:
    def test_system_messages_excluded(self):
        msgs = parse_whatsapp_chat(SYSTEM_CHAT)
        senders = {m.sender for m in msgs}
        # encrypted notice should not appear as a sender
        assert len(msgs) == 2
        assert "Rahul" in senders
        assert "Priya" in senders


class TestExtractMembers:
    def test_all_members_found(self):
        msgs = parse_whatsapp_chat(ANDROID_CHAT)
        members = extract_members(msgs)
        assert members == {"Rahul", "Priya", "Aakash"}

    def test_empty_chat(self):
        assert extract_members([]) == set()


class TestDateRange:
    def test_range_returned(self):
        msgs = parse_whatsapp_chat(ANDROID_CHAT)
        start, end = get_date_range(msgs)
        assert start is not None and end is not None
        assert end >= start

    def test_no_dates(self):
        start, end = get_date_range([])
        assert start is None and end is None


class TestMessageGrouping:
    def test_by_sender_keys(self):
        msgs = parse_whatsapp_chat(ANDROID_CHAT)
        grouped = messages_by_sender(msgs)
        assert set(grouped.keys()) == {"Rahul", "Priya", "Aakash"}

    def test_count_sorted(self):
        chat = """\
25/04/2024, 10:00 am - Alice: hi
25/04/2024, 10:01 am - Alice: hey
25/04/2024, 10:02 am - Bob: yo
"""
        msgs = parse_whatsapp_chat(chat)
        counts = count_messages_per_sender(msgs)
        keys = list(counts.keys())
        assert keys[0] == "Alice"  # Alice has 2, Bob has 1
