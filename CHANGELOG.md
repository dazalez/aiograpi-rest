# Changelog

## v7.0.1 - 2026-10-10

### Changed

- Upgraded the wrapped client to `aiograpi==2.0.17` (from `2.0.15`).
- Updated the package version to `7.0.1`.

### Verified

- The public `aiograpi.Client` surface is unchanged between `2.0.15` and
  `2.0.17`; the generated coverage report only differs in the pinned version
  line, so no router changes were required.

## v7.0.0 - 2026-10-08

### Changed

- Upgraded the wrapped client to `aiograpi==2.0.15` (from `1.0.9`).
- Updated the package version to `7.0.0`.
- `POST /note` and `POST /note/music` now map the numeric `audience` field to
  aiograpi's `NoteAudience` enum and reject unsupported values with HTTP 422.
- `POST /auth/login` now accepts an optional `login_flow` field (`caa` default,
  `legacy` for `Client.login_legacy`) and no longer relies on the obsolete
  `builtins.input` fallback for two-factor codes.
- `POST /direct/media` now calls `direct_media_share` with keyword arguments so
  the new `thread_ids` parameter cannot be mistaken for `send_attribute`.
- `GET /direct/inbox` and `GET /direct/threads` pass `None` instead of empty
  strings for `selected_filter` and `box`, matching aiograpi's optional filters.
- `GET /account/collection/media` forwards `amount` and `last_media_pk` to
  `collection_medias_by_name`, which now paginates.
- `GET /account/feed/timeline` accepts an optional `max_id` cursor and forwards
  it to `get_timeline_feed`, so the home feed can paginate with the
  `next_max_id` returned by the previous page.
- Removed the automatic `get_timeline_feed()` call from session restoration.
  Every REST request restored the client and then fetched the full timeline
  feed just to validate the session, which added a slow Instagram round-trip to
  each request. Expired sessions now surface as `LoginRequired` and map to HTTP
  401 instead.

### Added

- Account conversion routes: `POST /account/convert/business`,
  `POST /account/convert/creator`, `POST /account/convert/professional`,
  `PATCH /account/ai-info`, and `POST /account/phone/confirm/code`.
- User discovery routes: `GET /user/followers/private`,
  `GET /user/following/private`, `GET /user/followers/iter`,
  `GET /user/following/iter`, `GET /user/suggested/profiles`,
  `POST /user/report`, `POST /user/address-book/link`, and
  `DELETE /user/address-book`.
- Hashtag routes: `GET /hashtag/following`, `GET /hashtag/media/paginated`,
  `GET /hashtag/media/paginated/gql`, and `GET /hashtag/media/iter`.
- Media routes: `POST /media/link/reel`, `POST /media/share/to/story`,
  `GET /media/upload/status`, `GET /media/video/resources`,
  `GET /media/comments/public`, and `GET /user/media/iter`.
- Search and music routes: `GET /search/media` and `GET /music/bookmarked`.
- Story routes: `GET /story/likers`, `POST /story/poll/vote`,
  `POST /story/upload/with/music`, `POST /photo/upload/to/story/with/music`,
  and `POST /video/upload/to/story/with/music`.
- Clip routes: `GET /clip/interest/topics`, `GET /clip/mashup/info`,
  `PATCH /clip/seen`, `GET /clip/share/facebook/destination`,
  `GET /clip/share/facebook/unified/config`, and
  `GET /clip/share/facebook/unified/destination`.
- Direct routes: `GET /direct/messages/chunk` and `GET /direct/thread/chunk`.
- Story tray route: `GET /story/tray` exposes the reels tray (users with active
  stories in the last 24 hours) through `get_reels_tray_feed`.

### Verified

- Offline test gate: `285 passed, 6 deselected`, `100.00%` coverage.
- `ruff check .` and `scripts/generate_aiograpi_coverage.py --check` pass.

## v6.0.0 - 2026-05-21

Release: <https://github.com/subzeroid/aiograpi-rest/releases/tag/v6.0.0>

### Changed

- Upgraded the wrapped client to `aiograpi==1.0.9`.
- Updated the package version to `6.0.0`.
- Reworked account password and email flows for current aiograpi semantics:
  `POST /account/password/reset`, `POST /account/email/confirmation`, and
  `POST /account/email/confirm`.
- Updated Reel upload with music to use aiograpi's current
  `clip_upload_with_music` method and expose the new optional upload fields.

### Added

- Direct routes for request previews, channels, interop upgrade status, GenAI
  bot suggestions, and E2EE eligibility.
- Music routes for current catalog search, keyword search, trending music, top
  trends, Reels music browsing, audio bookmarking, and original-audio title
  availability.
- Media note routes: `POST /media/note` and `DELETE /media/note`.

### Removed

- Removed the public `GET /hashtag/related` route because aiograpi 1.0.x no
  longer exposes `hashtag_related_hashtags`.

### Verified

- Offline test gate: `270 passed, 6 deselected`, `100.00%` coverage.
- Live smoke gate: `/user/about`, paginated reads, story upload/read/download
  cleanup, and media upload/edit/delete state checks passed on Python 3.13.
- Release workflow verified PyPI, Docker Hub, GHCR, GitHub Release artifacts,
  and a smoke test of the published Docker image.
