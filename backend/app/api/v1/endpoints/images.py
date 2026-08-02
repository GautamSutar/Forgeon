"""Generated-image serving.

Images live under IMAGE_STORAGE_DIR/<user_id>/<file>. Serving them through
an endpoint rather than a static mount keeps the ownership check on the
path — one user cannot read another's generations by guessing a filename.
"""
from __future__ import annotations

import os
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/{user_id}/{filename}")
async def get_image(
    user_id: uuid.UUID,
    filename: str,
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    if user_id != current_user.id:
        raise NotFoundError("Image not found")

    # Reject any filename that isn't a bare name — "..", separators, or an
    # absolute path would otherwise escape the user's directory.
    if filename != os.path.basename(filename) or filename in ("", ".", ".."):
        raise NotFoundError("Image not found")

    directory = os.path.abspath(os.path.join(settings.IMAGE_STORAGE_DIR, str(user_id)))
    path = os.path.abspath(os.path.join(directory, filename))
    if not path.startswith(directory + os.sep) or not os.path.isfile(path):
        raise NotFoundError("Image not found")

    return FileResponse(path, media_type="image/png")
