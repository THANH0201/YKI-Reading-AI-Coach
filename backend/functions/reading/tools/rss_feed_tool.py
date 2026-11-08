from html.parser import HTMLParser
import ipaddress
import re
import socket
from urllib.parse import urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    Request,
    build_opener
)
import xml.etree.ElementTree as ET


MAX_FEED_BYTES = 2_000_000
MAX_FEED_ENTRIES = 20
HTTP_TIMEOUT_SECONDS = 12


class TextExtractor(HTMLParser):

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.ignored_depth = 0

    def handle_starttag(self, tag, attrs):

        tag = tag.lower()

        if tag in {
            "script",
            "style",
            "nav",
            "footer",
            "header"
        }:
            self.ignored_depth += 1

        elif tag in {
            "p",
            "br",
            "div",
            "li"
        } and not self.ignored_depth:
            self.parts.append(" ")

        elif tag == "img" and not self.ignored_depth:
            alt_text = dict(attrs).get("alt")

            if alt_text:
                self.parts.append(alt_text)

    def handle_endtag(self, tag):

        tag = tag.lower()

        if tag in {
            "script",
            "style",
            "nav",
            "footer",
            "header"
        }:
            self.ignored_depth = max(
                0,
                self.ignored_depth - 1
            )

        elif tag in {
            "p",
            "br",
            "div",
            "li"
        } and not self.ignored_depth:
            self.parts.append(" ")

    def handle_data(self, data):

        if not self.ignored_depth:
            self.parts.append(data)


class NoRedirectHandler(HTTPRedirectHandler):

    def redirect_request(
        self,
        *args,
        **kwargs,
    ):
        _ = args, kwargs
        return None


def validate_public_feed_url(
    feed_url: str
) -> None:

    parsed = urlsplit(feed_url)

    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.fragment
    ):
        raise ValueError(
            "Use a public HTTP or HTTPS RSS/Atom feed URL."
        )

    try:
        addresses = socket.getaddrinfo(
            parsed.hostname,
            parsed.port
            or (
                443
                if parsed.scheme == "https"
                else 80
            ),
            type=socket.SOCK_STREAM
        )

    except OSError as error:
        raise ValueError(
            "The feed host could not be resolved."
        ) from error

    if not addresses:
        raise ValueError(
            "Could not resolve feed host."
        )

    if any(
        not ipaddress.ip_address(
            address[4][0]
        ).is_global
        for address in addresses
    ):
        raise ValueError(
            "The feed URL must resolve only to public IP addresses."
        )


def fetch_feed(
    feed_url: str
) -> bytes:

    validate_public_feed_url(feed_url)

    request = Request(
        feed_url,
        headers={
            "User-Agent":
            "YKI-Reading-AI-Coach/1.0"
        }
    )

    opener = build_opener(
        NoRedirectHandler()
    )

    with opener.open(
        request,
        timeout=HTTP_TIMEOUT_SECONDS
    ) as response:

        content = response.read(
            MAX_FEED_BYTES + 1
        )

    if len(content) > MAX_FEED_BYTES:
        raise ValueError(
            "The feed exceeds the 2 MB download limit."
        )

    return content


def local_name(
    tag: str
) -> str:

    return (
        tag.rsplit("}", 1)[-1]
        .split(":")[-1]
        .casefold()
    )


def child_text(
    element: ET.Element,
    *names: str,
) -> str:

    children = list(element)

    for name in names:

        for child in children:

            if (
                local_name(child.tag)
                == name.casefold()
            ):
                text = "".join(
                    child.itertext()
                ).strip()

                if text:
                    return text

    return ""


def entry_link(
    entry: ET.Element
) -> str:

    for child in entry:

        if local_name(child.tag) != "link":
            continue

        href = child.attrib.get("href")

        if href:
            return href.strip()

        if child.text and child.text.strip():
            return child.text.strip()

    return child_text(
        entry,
        "link",
        "guid",
        "id"
    )


def clean_article_text(
    raw_content: str
) -> str:

    parser = TextExtractor()

    parser.feed(raw_content)

    parser.close()

    return re.sub(
        r"\s+",
        " ",
        " ".join(parser.parts)
    ).strip()


def word_count(
    content: str
) -> int:

    return len(
        re.findall(
            r"\b[\w'-]+\b",
            content,
            flags=re.UNICODE
        )
    )


def parse_feed(
    feed_content: bytes
) -> list[dict[str, str]]:
    root = ET.fromstring(feed_content)

    entries = [
        element
        for element in root.iter()
        if local_name(element.tag)
        in {"item", "entry"}
    ][:MAX_FEED_ENTRIES]

    parsed_entries = []

    for entry in entries:

        title = child_text(
            entry,
            "title"
        )

        article_url = entry_link(
            entry
        )

        raw_content = child_text(
            entry,
            "encoded",
            "content",
            "description",
            "summary"
        )

        content = clean_article_text(
            raw_content
        )

        if (
            title
            and article_url
            and content
        ):
            parsed_entries.append(
                {
                    "title": title,
                    "url": article_url,
                    "content": content,
                }
            )

    return parsed_entries