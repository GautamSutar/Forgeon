"""Thin wrapper around resume_parser_service for tool-calling contexts."""
from __future__ import annotations

from app.schemas.resume import ParsedResumeData
from app.services.resume_parser_service import parse_resume_pdf


class ResumeTool:
    @staticmethod
    def parse(file_bytes: bytes) -> ParsedResumeData:
        return parse_resume_pdf(file_bytes)
