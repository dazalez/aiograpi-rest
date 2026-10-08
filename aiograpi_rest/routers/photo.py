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
from pydantic import AnyHttpUrl

from aiograpi_rest.dependencies import ClientStorage, get_clients, get_sessionid
from aiograpi_rest.helpers import (
    LOCATION_FORM_DESCRIPTION,
    USERTAGS_FORM_DESCRIPTION,
    parse_json_form_dict,
    parse_json_form_model,
    parse_json_form_models,
    parse_upload_location,
    parse_upload_usertags,
    photo_upload_post,
    photo_upload_to_story_with_music_post,
    photo_upload_with_music_post,
)

router = APIRouter(
    prefix="/photo",
    tags=["Photo"],
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
async def photo_download(sessionid: str = Depends(get_sessionid),
                         media_pk: int = Query(...),
                         folder: Optional[Path] = Query(""),
                         returnFile: Optional[bool] = Query(True),
                         clients: ClientStorage = Depends(get_clients)):
    """Download photo using media pk
    """
    cl = await clients.get(sessionid)
    result = await cl.photo_download(media_pk, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@router.get("/download/by/url")
async def photo_download_by_url(sessionid: str = Depends(get_sessionid),
                         url: str = Query(...),
                         filename: Optional[str] = Query(""),
                         folder: Optional[Path] = Query(""),
                         returnFile: Optional[bool] = Query(True),
                         clients: ClientStorage = Depends(get_clients)):
    """Download photo using URL
    """
    cl = await clients.get(sessionid)
    result = await cl.photo_download_by_url(url, filename, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@router.post("/upload", response_model=Media)
async def photo_upload(sessionid: str = Depends(get_sessionid),
                       file: UploadFile = File(...),
                       caption: str = Form(...),
                       upload_id: Optional[str] = Form(""),
                       usertags: Optional[List[str]] = Form([], description=USERTAGS_FORM_DESCRIPTION),
                       location: Optional[str] = Form(None, description=LOCATION_FORM_DESCRIPTION),
                       clients: ClientStorage = Depends(get_clients)
                       ) -> Media:
    """Upload photo and configure to feed
    """
    cl = await clients.get(sessionid)

    content = await file.read()
    return await photo_upload_post(
        cl, content, caption=caption,
        upload_id=upload_id,
        usertags=parse_upload_usertags(usertags),
        location=parse_upload_location(location))


@router.post("/upload/with/music", response_model=Media)
async def photo_upload_with_music(sessionid: str = Depends(get_sessionid),
                       file: UploadFile = File(...),
                       caption: str = Form(...),
                       track: str = Form(..., description=TRACK_FORM_DESCRIPTION),
                       upload_id: Optional[str] = Form(""),
                       usertags: Optional[List[str]] = Form([], description=USERTAGS_FORM_DESCRIPTION),
                       location: Optional[str] = Form(None, description=LOCATION_FORM_DESCRIPTION),
                       extra_data: Optional[str] = Form(None, description=EXTRA_DATA_FORM_DESCRIPTION),
                       audio_asset_start_time: Optional[int] = Form(None),
                       overlap_duration: int = Form(30000),
                       browse_session_id: Optional[str] = Form(None),
                       alacorn_session_id: Optional[str] = Form(None),
                       clients: ClientStorage = Depends(get_clients)
                       ) -> Media:
    """Upload a feed photo with music
    """
    cl = await clients.get(sessionid)

    content = await file.read()
    parsed_track = parse_json_form_model(track, Track, "track")
    parsed_extra_data = parse_json_form_dict(extra_data, "extra_data", default={})
    return await photo_upload_with_music_post(
        cl, content, caption=caption,
        upload_id=upload_id,
        usertags=parse_upload_usertags(usertags),
        location=parse_upload_location(location),
        track=parsed_track,
        extra_data=parsed_extra_data,
        audio_asset_start_time=audio_asset_start_time,
        overlap_duration=overlap_duration,
        browse_session_id=browse_session_id,
        alacorn_session_id=alacorn_session_id)


@router.post("/upload/by/url", response_model=Media)
async def photo_upload(sessionid: str = Depends(get_sessionid),
                       url: AnyHttpUrl = Form(...),
                       caption: str = Form(...),
                       upload_id: Optional[str] = Form(""),
                       usertags: Optional[List[str]] = Form([], description=USERTAGS_FORM_DESCRIPTION),
                       location: Optional[str] = Form(None, description=LOCATION_FORM_DESCRIPTION),
                       clients: ClientStorage = Depends(get_clients)
                       ) -> Media:
    """Upload photo and configure to feed
    """
    cl = await clients.get(sessionid)

    content = requests.get(url).content
    return await photo_upload_post(
        cl, content, caption=caption,
        upload_id=upload_id,
        usertags=parse_upload_usertags(usertags),
        location=parse_upload_location(location))


@router.post("/upload/to/story/with/music", response_model=Story)
async def photo_upload_to_story_with_music(sessionid: str = Depends(get_sessionid),
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
                                           duration: float = Form(15.0),
                                           audio_asset_start_time: Optional[int] = Form(None),
                                           overlap_duration: Optional[int] = Form(None),
                                           original_volume: float = Form(0.0),
                                           music_volume: float = Form(1.0),
                                           product: str = Form("story_camera_music_overlay_post_capture"),
                                           alacorn_session_id: str = Form("null"),
                                           clients: ClientStorage = Depends(get_clients)
                                           ) -> Story:
    """Upload a photo story with music
    """
    cl = await clients.get(sessionid)
    content = await file.read()
    thumbnail_content = await thumbnail.read() if thumbnail is not None else None
    return await photo_upload_to_story_with_music_post(
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
        duration=duration,
        audio_asset_start_time=audio_asset_start_time,
        overlap_duration=overlap_duration,
        original_volume=original_volume,
        music_volume=music_volume,
        product=product,
        alacorn_session_id=alacorn_session_id)
