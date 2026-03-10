import json
import urllib.parse
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from IMDBTraktSyncer import errorHandling as EH
from IMDBTraktSyncer import errorLogger as EL
from IMDBTraktSyncer import verifyCredentials as VC


class TraktFetchError(RuntimeError):
    pass


def _parse_json_response(response, endpoint):
    if not EH.is_trakt_success(response):
        status_code = response.status_code if response is not None else "no response"
        raise TraktFetchError(
            f"Failed to load Trakt data from {endpoint}. Status: {status_code}"
        )
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        EL.logger.error("Failed to decode Trakt API response.", exc_info=True)
        raise TraktFetchError(f"Invalid JSON returned from Trakt endpoint {endpoint}")


def _get_page_count(response):
    if not response:
        return 0
    try:
        return max(1, int(response.headers.get("X-Pagination-Page-Count", "1")))
    except (TypeError, ValueError):
        return 1


def _fetch_paginated(endpoint, params=None, sort=None, limit=100):
    combined_params = dict(params or {})
    combined_params["limit"] = limit
    if sort is not None:
        combined_params["sort"] = sort

    response = EH.make_trakt_request(endpoint, params={**combined_params, "page": 1})
    items = _parse_json_response(response, endpoint)
    total_pages = _get_page_count(response)

    for page in range(2, total_pages + 1):
        page_response = EH.make_trakt_request(
            endpoint, params={**combined_params, "page": page}
        )
        items.extend(_parse_json_response(page_response, f"{endpoint}?page={page}"))

    return items


def remove_slashes(string):
    string = string.replace("/", "") if string is not None else None
    return string


def get_trakt_encoded_username():
    credentials = VC.load_credentials()
    saved_slug = credentials.get("trakt_username_slug")
    if saved_slug and saved_slug != "empty":
        return urllib.parse.quote(saved_slug)

    response = EH.make_trakt_request("https://api.trakt.tv/users/me")
    json_data = _parse_json_response(response, "https://api.trakt.tv/users/me")
    username_slug = json_data["ids"]["slug"]
    credentials["trakt_username_slug"] = username_slug
    VC.save_credentials(credentials)
    encoded_username = urllib.parse.quote(username_slug)
    return encoded_username


def get_trakt_watchlist(encoded_username):
    # Get Trakt Watchlist Items
    json_data = _fetch_paginated(
        f"https://api.trakt.tv/users/{encoded_username}/watchlist", sort="added,asc"
    )

    trakt_watchlist = []

    for item in json_data:
        if item["type"] == "movie":
            movie = item.get("movie")
            imdb_movie_id = movie.get("ids", {}).get("imdb")
            imdb_movie_id = remove_slashes(imdb_movie_id)
            trakt_movie_id = movie.get("ids", {}).get("trakt")
            trakt_watchlist.append(
                {
                    "Title": movie.get("title"),
                    "Year": movie.get("year"),
                    "IMDB_ID": imdb_movie_id,
                    "TraktID": trakt_movie_id,
                    "Date_Added": item.get("listed_at"),
                    "Type": "movie",
                }
            )
        elif item["type"] == "show":
            show = item.get("show")
            imdb_show_id = show.get("ids", {}).get("imdb")
            imdb_show_id = remove_slashes(imdb_show_id)
            trakt_show_id = show.get("ids", {}).get("trakt")
            trakt_watchlist.append(
                {
                    "Title": show.get("title"),
                    "Year": show.get("year"),
                    "IMDB_ID": imdb_show_id,
                    "TraktID": trakt_show_id,
                    "Date_Added": item.get("listed_at"),
                    "Type": "show",
                }
            )
        elif item["type"] == "episode":
            show = item.get("show")
            show_title = show.get("title")
            episode = item.get("episode")
            imdb_episode_id = episode.get("ids", {}).get("imdb")
            imdb_episode_id = remove_slashes(imdb_episode_id)
            trakt_episode_id = episode.get("ids", {}).get("trakt")
            episode_title = f"{show_title}: {episode.get('title')}"
            trakt_watchlist.append(
                {
                    "Title": episode_title,
                    "Year": episode.get("year"),
                    "IMDB_ID": imdb_episode_id,
                    "TraktID": trakt_episode_id,
                    "Date_Added": item.get("listed_at"),
                    "Type": "episode",
                }
            )

    return trakt_watchlist


def get_trakt_ratings(encoded_username):
    # Get Trakt Ratings
    json_data = _fetch_paginated(
        f"https://api.trakt.tv/users/{encoded_username}/ratings", sort="newest"
    )

    movie_ratings = []
    show_ratings = []
    episode_ratings = []

    for item in json_data:
        if item["type"] == "movie":
            movie = item.get("movie")
            movie_id = movie.get("ids", {}).get("imdb")
            movie_id = remove_slashes(movie_id)
            movie_ratings.append(
                {
                    "Title": movie.get("title"),
                    "Year": movie.get("year"),
                    "Rating": item.get("rating"),
                    "IMDB_ID": movie_id,
                    "Date_Added": item.get("rated_at"),
                    "WatchedAt": item.get("rated_at"),
                    "Type": "movie",
                }
            )
        elif item["type"] == "show":
            show = item.get("show")
            show_id = show.get("ids", {}).get("imdb")
            show_id = remove_slashes(show_id)
            show_ratings.append(
                {
                    "Title": show.get("title"),
                    "Year": show.get("year"),
                    "Rating": item.get("rating"),
                    "IMDB_ID": show_id,
                    "Date_Added": item.get("rated_at"),
                    "WatchedAt": item.get("rated_at"),
                    "Type": "show",
                }
            )
        elif item["type"] == "episode":
            show = item.get("show")
            show_title = show.get("title")
            episode = item.get("episode")
            episode_id = episode.get("ids", {}).get("imdb")
            episode_id = remove_slashes(episode_id)
            episode_title = f"{show_title}: {episode.get('title')}"
            episode_ratings.append(
                {
                    "Title": episode_title,
                    "Year": episode.get("year"),
                    "Rating": item.get("rating"),
                    "IMDB_ID": episode_id,
                    "Date_Added": item.get("rated_at"),
                    "WatchedAt": item.get("rated_at"),
                    "Type": "episode",
                }
            )

    trakt_ratings = movie_ratings + show_ratings + episode_ratings

    return trakt_ratings


def get_trakt_comments(encoded_username):
    # Get Trakt Comments
    json_data = _fetch_paginated(
        f"https://api.trakt.tv/users/{encoded_username}/comments", sort="newest"
    )
    trakt_comments = []

    for comment in json_data:
        comment_type = comment["type"]
        spoiler = comment.get("spoiler", False)
        show_movie_or_episode_title = None
        show_movie_or_episode_year = None
        show_movie_or_episode_imdb_id = None

        if comment_type == "movie":
            movie = comment.get("movie")
            show_movie_or_episode_title = movie.get("title")
            show_movie_or_episode_year = movie.get("year")
            show_movie_or_episode_imdb_id = movie.get("ids", {}).get("imdb")
            show_movie_or_episode_imdb_id = remove_slashes(
                show_movie_or_episode_imdb_id
            )
        elif comment_type == "episode":
            show = comment.get("show")
            episode = comment.get("episode")
            show_movie_or_episode_title = f"{show.get('title')}: {episode.get('title')}"
            show_movie_or_episode_year = show.get("year")
            show_movie_or_episode_imdb_id = episode.get("ids", {}).get("imdb")
            show_movie_or_episode_imdb_id = remove_slashes(
                show_movie_or_episode_imdb_id
            )
        elif comment_type == "show":
            show = comment.get("show")
            show_movie_or_episode_title = show.get("title")
            show_movie_or_episode_year = show.get("year")
            show_movie_or_episode_imdb_id = show.get("ids", {}).get("imdb")
            show_movie_or_episode_imdb_id = remove_slashes(
                show_movie_or_episode_imdb_id
            )
        elif comment_type == "season":
            show = comment.get("show")
            season = comment.get("season")
            show_movie_or_episode_title = (
                f"{show.get('title')}: Season {season.get('number')}"
            )
            show_movie_or_episode_year = None
            show_movie_or_episode_imdb_id = None
        else:
            # Generic fallback for unknown types
            # Find the first dict that has title/year/ids
            for key, value in comment.items():
                if isinstance(value, dict) and "title" in value:
                    show_movie_or_episode_title = value.get("title")
                    show_movie_or_episode_year = value.get("year")
                    show_movie_or_episode_imdb_id = remove_slashes(
                        value.get("ids", {}).get("imdb")
                    )
                    break

        comment_info = comment["comment"]
        trakt_comment_id = comment_info.get("id")
        trakt_comment = comment_info.get("comment")

        trakt_comments.append(
            {
                "Title": show_movie_or_episode_title,
                "Year": show_movie_or_episode_year,
                "IMDB_ID": show_movie_or_episode_imdb_id,
                "TraktCommentID": trakt_comment_id,
                "Comment": trakt_comment,
                "Spoiler": spoiler,
                "Type": comment_type,
            }
        )

    # Filter out duplicate comments for the same item based on ID
    filtered_comments = []
    seen = set()
    for item in trakt_comments:
        if item["IMDB_ID"] not in seen:
            seen.add(item["IMDB_ID"])
            filtered_comments.append(item)
    trakt_comments = filtered_comments

    return trakt_comments


def get_trakt_watch_history(encoded_username):
    # Get Trakt Watch History
    json_data = _fetch_paginated(
        f"https://api.trakt.tv/users/{encoded_username}/history",
        params={"extended": "full"},
    )

    watched_movies = []
    watched_shows = []
    watched_episodes = []
    seen_ids = set()

    for item in json_data:
        if item["type"] == "movie":
            movie = item.get("movie")
            imdb_movie_id = movie.get("ids", {}).get("imdb")
            imdb_movie_id = remove_slashes(imdb_movie_id)
            trakt_movie_id = movie.get("ids", {}).get("trakt")
            if trakt_movie_id and trakt_movie_id not in seen_ids:
                watched_movies.append(
                    {
                        "Title": movie.get("title"),
                        "Year": movie.get("year"),
                        "IMDB_ID": imdb_movie_id,
                        "TraktID": trakt_movie_id,
                        "Date_Added": item.get("watched_at"),
                        "WatchedAt": item.get("watched_at"),
                        "Type": "movie",
                    }
                )
                seen_ids.add(trakt_movie_id)
        elif item["type"] == "episode":
            show = item.get("show")
            imdb_show_id = show.get("ids", {}).get("imdb")
            imdb_show_id = remove_slashes(imdb_show_id)
            trakt_show_id = show.get("ids", {}).get("trakt")
            show_status = show.get("status")
            aired_episodes = show.get("aired_episodes")

            if trakt_show_id and trakt_show_id not in seen_ids:
                watched_shows.append(
                    {
                        "Title": show.get("title"),
                        "Year": show.get("year"),
                        "IMDB_ID": imdb_show_id,
                        "TraktID": trakt_show_id,
                        "Date_Added": item.get("watched_at"),
                        "WatchedAt": item.get("watched_at"),
                        "ShowStatus": show_status,
                        "AiredEpisodes": aired_episodes,
                        "Type": "show",
                    }
                )
                seen_ids.add(trakt_show_id)

            show_title = show.get("title")
            episode = item.get("episode")
            season_number = episode.get("season")
            episode_number = episode.get("number")
            imdb_episode_id = episode.get("ids", {}).get("imdb")
            imdb_episode_id = remove_slashes(imdb_episode_id)
            trakt_episode_id = episode.get("ids", {}).get("trakt")
            episode_title = f"{show_title}: {episode.get('title')}"
            episode_year = (
                datetime.datetime.strptime(
                    episode.get("first_aired"), "%Y-%m-%dT%H:%M:%S.%fZ"
                ).year
                if episode.get("first_aired")
                else None
            )
            watched_at = item.get("watched_at")
            if trakt_episode_id and trakt_episode_id not in seen_ids:
                watched_episodes.append(
                    {
                        "Title": episode_title,
                        "Year": episode_year,
                        "IMDB_ID": imdb_episode_id,
                        "TraktID": trakt_episode_id,
                        "TraktShowID": trakt_show_id,
                        "SeasonNumber": season_number,
                        "EpisodeNumber": episode_number,
                        "Date_Added": watched_at,
                        "WatchedAt": watched_at,
                        "Type": "episode",
                    }
                )
                seen_ids.add(trakt_episode_id)

    # Filter watched_shows for completed shows where 80% or more of the show has been watched AND where the show's status is "ended" or "cancelled"
    filtered_watched_shows = []
    for show in watched_shows:
        trakt_show_id = show["TraktID"]
        show_status = show["ShowStatus"]
        aired_episodes = show["AiredEpisodes"]
        episode_numbers = [
            episode["EpisodeNumber"]
            for episode in watched_episodes
            if episode["Type"] == "episode" and episode["TraktShowID"] == trakt_show_id
        ]
        unique_watched_episode_count = len(episode_numbers)

        if (show_status.lower() in ["ended", "cancelled", "canceled"]) and (
            unique_watched_episode_count >= 0.8 * int(aired_episodes)
        ):
            filtered_watched_shows.append(show)

    # Update watched_shows with the filtered results
    watched_shows = filtered_watched_shows

    trakt_watch_history = watched_movies + watched_shows + watched_episodes

    return trakt_watch_history
