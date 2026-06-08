import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from urllib.parse import parse_qs, urlparse

def get_video_id(url: str) -> str:
    parsed_url = urlparse(url)

    if parsed_url.hostname in {"youtu.be"}:
        return parsed_url.path.lstrip("/")

    if parsed_url.hostname in {"www.youtube.com", "youtube.com", "m.youtube.com"}:
        if parsed_url.path == "/watch":
            video_id = parse_qs(parsed_url.query).get("v", [None])[0]
            if video_id:
                return video_id

        match = re.match(r"^/(embed|shorts)/([^/?]+)", parsed_url.path)
        if match:
            return match.group(2)

    return None


def generate_transcript(video_id: str) -> str:
    try:
        transcript = YouTubeTranscriptApi().fetch(
            video_id=video_id,
            languages=["en"],
            preserve_formatting=False,
        )
        return " ".join(snippet.text for snippet in transcript)
    except TranscriptsDisabled:
        return ""
    except Exception as e:
        print(e)
        return ""
