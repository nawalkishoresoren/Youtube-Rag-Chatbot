from pathlib import Path

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectTimeout, HTTPError, ProxyError, RequestException
from urllib3.util.retry import Retry


VIDEO_URL = "https://videos15.fpo.xxx/remote_control.php?file=BSiw4sCxskIhCbvT3Xcy6nVl6K6l9IlN4C3uEnoZC4zEXysZX7t3ODQjnEDICjrqWI8-CHD26qvrQDXtumq4SuIzAN6N4-DMObh-XI96RckoPwHaeirNEHjthpG-Fw0_uCLJmOuMeTfEzCjwUd7BAMwbsRYvj2z0cCi1TduhRuCoTZwe4RlJMpSVdsUs3G94NRCcB_r_H6vHnfb_UHgw3fYKVgUGNxecY-a9.mp4&acctoken=ZWEzZGRmYzczZWY1MjBjN2M2ODYxOWY4ZTFlYzk2YWUxNGU4MjNkZDgyY2IxNzFmOGU5N2I5YzI2NzRkYmU0M3wxNzgwODI2MzIzfDE1OTkxMjV8ZnBvLnh4eHwwfDkxLjIyMS4xOTAuNTN8Njk2ZWEyNTYwN2M2NjBmYzlkYmZmNTYyNTgxOWI4MjM"
OUTPUT_FILE = Path("video.mp4")
TEMP_FILE = OUTPUT_FILE.with_suffix(".mp4.part")
CHUNK_SIZE = 8192
TIMEOUT = (15, 60)


def build_session() -> requests.Session:
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.trust_env = False
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def download_file(session: requests.Session, video_url: str, output_file: Path) -> int:
    with session.get(video_url, stream=True, timeout=TIMEOUT) as response:
        response.raise_for_status()
        return write_response(response, output_file)


def write_response(response: Response, output_file: Path) -> int:
    total = 0

    with TEMP_FILE.open("wb") as file_handle:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if not chunk:
                continue
            file_handle.write(chunk)
            total += len(chunk)

    TEMP_FILE.replace(output_file)
    return total


def main() -> None:
    session = build_session()

    try:
        total = download_file(session, VIDEO_URL, OUTPUT_FILE)
    except ConnectTimeout:
        print("Download failed: connection to the video host timed out.")
    except ProxyError:
        print("Download failed: the configured proxy is unreachable.")
    except HTTPError as error:
        status_code = error.response.status_code if error.response else "unknown"
        print(f"Download failed: server returned HTTP {status_code}.")
    except RequestException as error:
        print(f"Download failed: {error}")
    else:
        print(f"Downloaded {total:,} bytes to {OUTPUT_FILE}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
