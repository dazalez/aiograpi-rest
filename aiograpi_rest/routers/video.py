from pathlib import Path
from typing import List, Optional

import requests
from aiograpi.types import (
    Media,
    Story,
    StoryHashtag,
    StoryLink,
    StoryLocation,
    StoryMention,
    StorySticker,
    Track,
)
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import FileResponse

from aiograpi_rest.dependencies import ClientStorage, get_clients, get_sessionid
from aiograpi_rest.helpers import (
    LOCATION_FORM_DESCRIPTION,
    USERTAGS_FORM_DESCRIPTION,
    parse_json_form_dict,
    parse_json_form_model,
    parse_json_form_models,
    parse_upload_location,
    parse_upload_usertags,
    video_upload_post,
    video_upload_to_story_with_music_post,
)

router = APIRouter(
    prefix="/video",
    tags=["Video"],
    responses={404: {"description": "Not found"}},
)
TRACK_FORM_DESCRIPTION = "JSON-encoded Track object returned by search or music browser endpoints."
EXTRA_DATA_FORM_DESCRIPTION = "JSON-encoded extra configure data. Leave empty to omit."
STORY_MENTIONS_FORM_DESCRIPTION = "Repeat this form field with a JSON-encoded StoryMention object."
STORY_LOCATIONS_FORM_DESCRIPTION = "Repeat this form field with a JSON-encoded StoryLocation object."
STORY_LINKS_FORM_DESCRIPTION = "Repeat this form field with a JSON-encoded StoryLink object."
STORY_HASHTAGS_FORM_DESCRIPTION = "Repeat this form field with a JSON-encoded StoryHashtag object."
STORY_STICKERS_FORM_DESCRIPTION = "Repeat this form field with a JSON-encoded StorySticker object."


@router.get("/download")
async def video_download(sessionid: str = Depends(get_sessionid),
                         media_pk: int = Query(...),
                         folder: Optional[Path] = Query(""),
                         returnFile: Optional[bool] = Query(True),
                         clients: ClientStorage = Depends(get_clients)):
    """Download video using media pk
    """
    cl = await clients.get(sessionid)
    result = await cl.video_download(media_pk, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@router.get("/download/by/url")
async def video_download_by_url(sessionid: str = Depends(get_sessionid),
                         url: str = Query(...),
                         filename: Optional[str] = Query(""),
                         folder: Optional[Path] = Query(""),
                         returnFile: Optional[bool] = Query(True),
                         clients: ClientStorage = Depends(get_clients)):
    """Download video using URL
    """
    cl = await clients.get(sessionid)
    result = await cl.video_download_by_url(url, filename, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@router.post("/upload", response_model=Media)
async def video_upload(sessionid: str = Depends(get_sessionid),
                       file: UploadFile = File(...),
                       caption: str = Form(...),
                       thumbnail: Optional[UploadFile] = File(None),
                       usertags: Optional[List[str]] = Form([], description=USERTAGS_FORM_DESCRIPTION),
                       location: Optional[str] = Form(None, description=LOCATION_FORM_DESCRIPTION),
                       clients: ClientStorage = Depends(get_clients)
                       ) -> Media:
    """Upload photo and configure to feed
    """
    cl = await clients.get(sessionid)

    content = await file.read()
    usernames_tags = parse_upload_usertags(usertags)
    parsed_location = parse_upload_location(location)
    if thumbnail is not None:
        thumb = await thumbnail.read()
        return await video_upload_post(
            cl, content, caption=caption,
            thumbnail=thumb,
            usertags=usernames_tags,
            location=parsed_location)
    return await video_upload_post(
        cl, content, caption=caption,
        usertags=usernames_tags,
        location=parsed_location)


@router.post("/upload/to/story/with/music", response_model=Story)
async def video_upload_to_story_with_music(sessionid: str = Depends(get_sessionid),
                                           file: UploadFile = File(...),
                                           caption: str = Form(...),
                                           track: str = Form(..., description=TRACK_FORM_DESCRIPTION),
                                           thumbnail: Optional[UploadFile] = File(None),
                                           mentions: Optional[List[str]] = Form(
                                               [], description=STORY_MENTIONS_FORM_DESCRIPTION
                                           ),
                                           locations: Optional[List[str]] = Form(
                                               [], description=STORY_LOCATIONS_FORM_DESCRIPTION
                                           ),
                                           links: Optional[List[str]] = Form(
                                               [], description=STORY_LINKS_FORM_DESCRIPTION
                                           ),
                                           hashtags: Optional[List[str]] = Form(
                                               [], description=STORY_HASHTAGS_FORM_DESCRIPTION
                                           ),
                                           stickers: Optional[List[str]] = Form(
                                               [], description=STORY_STICKERS_FORM_DESCRIPTION
                                           ),
                                           extra_data: Optional[str] = Form(
                                               None, description=EXTRA_DATA_FORM_DESCRIPTION
                                           ),
                                           audio_asset_start_time: Optional[int] = Form(None),
                                           overlap_duration: Optional[int] = Form(None),
                                           original_volume: float = Form(0.0),
                                           music_volume: float = Form(1.0),
                                           product: str = Form("story_camera_music_overlay_post_capture"),
                                           alacorn_session_id: str = Form("null"),
                                           clients: ClientStorage = Depends(get_clients)
                                           ) -> Story:
    """Upload a video story with music
    """
    cl = await clients.get(sessionid)
    content = await file.read()
    thumbnail_content = await thumbnail.read() if thumbnail is not None else None
    return await video_upload_to_story_with_music_post(
        cl, content,
        caption=caption,
        track=parse_json_form_model(track, Track, "track"),
        thumbnail=thumbnail_content,
        mentions=parse_json_form_models(mentions, StoryMention, "mentions"),
        locations=parse_json_form_models(locations, StoryLocation, "locations"),
        links=parse_json_form_models(links, StoryLink, "links"),
        hashtags=parse_json_form_models(hashtags, StoryHashtag, "hashtags"),
        stickers=parse_json_form_models(stickers, StorySticker, "stickers"),
        extra_data=parse_json_form_dict(extra_data, "extra_data", default={}),
        audio_asset_start_time=audio_asset_start_time,
        overlap_duration=overlap_duration,
        original_volume=original_volume,
        music_volume=music_volume,
        product=product,
        alacorn_session_id=alacorn_session_id)


@router.post("/upload/by/url", response_model=Media)
async def video_upload(sessionid: str = Depends(get_sessionid),
                       url: str = Form(...),
                       caption: str = Form(...),
                       thumbnail: Optional[UploadFile] = File(None),
                       usertags: Optional[List[str]] = Form([], description=USERTAGS_FORM_DESCRIPTION),
                       location: Optional[str] = Form(None, description=LOCATION_FORM_DESCRIPTION),
                       clients: ClientStorage = Depends(get_clients)
                       ) -> Media:
    """Upload photo by URL and configure to feed
    """
    cl = await clients.get(sessionid)

    content = requests.get(url).content
    usernames_tags = parse_upload_usertags(usertags)
    parsed_location = parse_upload_location(location)
    if thumbnail is not None:
        thumb = await thumbnail.read()
        return await video_upload_post(
            cl, content, caption=caption,
            thumbnail=thumb,
            usertags=usernames_tags,
            location=parsed_location)
    return await video_upload_post(
        cl, content, caption=caption,
        usertags=usernames_tags,
        location=parsed_location)
