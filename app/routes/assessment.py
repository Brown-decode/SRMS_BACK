from fastapi import APIRouter, Depends, HTTPException

assessment_router = APIRouter(prefix="/assessment")

@assessment_router.post("/create")
def 