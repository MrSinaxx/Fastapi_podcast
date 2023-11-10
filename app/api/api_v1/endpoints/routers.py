from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from fastapi.requests import Request
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordBearer
from app.core.config import EPISODELIST_ENDPOINT, PODCASTLIST_ENDPOINT, settings
from app.db.mongo import liked_collection
from app.jwt.utils import get_user_id_from_token, is_access_token_valid
from app.schema.schemas import LikedPodcastRequest, LikedPodcastResponse
import httpx

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")
router = APIRouter(tags=["podcast"])


@router.get("/podcastlist", status_code=status.HTTP_200_OK)
async def podcastlist():
    """
    Get the list of podcasts.

    Returns:
        JSON: List of podcasts.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(PODCASTLIST_ENDPOINT)
    return response.json()


@router.get("/podcasts/{pk}/episodes/", status_code=status.HTTP_200_OK)
async def episodelist(
    pk: int = Path(..., description="Primary key for the podcast"),
    page: int = Query(1, description="Page number for pagination"),
):
    """
    Get the list of episodes for a specific podcast.

    Args:
        pk (int): Primary key for the podcast.
        page (int, optional): Page number for pagination. Defaults to 1.

    Returns:
        JSON: List of episodes for the specified podcast.
    """
    target_url = f"{settings.EPISODELIST_ENDPOINT}{pk}/episodes/?page={page}"
    async with httpx.AsyncClient() as client:
        response = await client.get(target_url)

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Page not found")

    return response.json()


@router.post("/like_podcast", status_code=status.HTTP_201_CREATED)
async def like_podcast(
    request: Request,
    liked_podcast: LikedPodcastRequest,
    token: str = Depends(oauth2_scheme),
):
    """
    Like or unlike a podcast.

    Args:
        request (Request): The incoming request.
        liked_podcast (LikedPodcastRequest): The podcast to like/unlike.
        token (str): OAuth2 token for authorization.

    Returns:
        JSON: A message indicating success.
    """
    if not is_access_token_valid(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token"
        )
    user_id = get_user_id_from_token(token)
    podcast_id = liked_podcast.podcast_id

    existing_like = await liked_collection.find_one(
        {"user_id": user_id, "podcast_id": podcast_id}
    )

    if existing_like:
        await liked_collection.delete_one(
            {"user_id": user_id, "podcast_id": podcast_id}
        )
        message = "Podcast unliked successfully"
    else:
        liked_data = {
            "user_id": user_id,
            "podcast_id": podcast_id,
        }

        result = await liked_collection.insert_one(liked_data)
        message = "Podcast liked successfully"

    return {
        "message": message,
    }


@router.get(
    "/liked_podcasts",
    status_code=status.HTTP_200_OK,
    response_model=List[LikedPodcastResponse],
)
async def get_liked_podcasts(request: Request, token: str = Depends(oauth2_scheme)):
    """
    Get the list of liked podcasts for the current user.

    Args:
        request (Request): The incoming request.
        token (str): OAuth2 token for authorization.

    Returns:
        JSON: List of liked podcasts.
    """
    if not is_access_token_valid(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token"
        )
    user_id = get_user_id_from_token(token)

    liked_podcasts = await liked_collection.find({"user_id": user_id}).to_list(
        length=None
    )

    return liked_podcasts


@router.get("/liked_count/{podcast_id}", status_code=status.HTTP_200_OK)
async def bookmark_count(podcast_id: str):
    """
    Get the total number of bookmarks for a podcast.

    Args:
        podcast_id (str): The ID of the podcast.

    Returns:
        JSON: Podcast ID and total bookmarks count.
    """
    total_bookmarks = await liked_collection.count_documents({"podcast_id": podcast_id})

    return {"podcast_id": podcast_id, "total_bookmarks": total_bookmarks}
