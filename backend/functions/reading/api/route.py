from fastapi import APIRouter

from .exam_routes import (
    router as exam_router,
)

from .tutor_routes import (
    router as tutor_router,
)

router = APIRouter()

router.include_router(exam_router)
router.include_router(tutor_router)