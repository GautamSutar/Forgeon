"""Builds minimal, real, parseable single-page PDFs for tests — no external
PDF-generation dependency required.
"""
from __future__ import annotations


def build_pdf(lines: list[str]) -> bytes:
    content_lines = ["BT", "/F1 12 Tf", "72 720 Td"]
    for i, line in enumerate(lines):
        if i > 0:
            content_lines.append("0 -14 Td")
        escaped = line.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")
        content_lines.append(f"({escaped}) Tj")
    content_lines.append("ET")
    content_stream = "\n".join(content_lines).encode("latin-1")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> "
        b"/MediaBox [0 0 612 792] /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length %d >>\nstream\n" % len(content_stream) + content_stream + b"\nendstream",
    ]

    buf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj_body in enumerate(objects, start=1):
        offsets.append(len(buf))
        buf += f"{i} 0 obj\n".encode("latin-1")
        buf += obj_body
        buf += b"\nendobj\n"

    xref_offset = len(buf)
    n = len(objects) + 1
    buf += f"xref\n0 {n}\n".encode("latin-1")
    buf += b"0000000000 65535 f \n"
    for off in offsets:
        buf += f"{off:010d} 00000 n \n".encode("latin-1")
    buf += b"trailer\n"
    buf += f"<< /Size {n} /Root 1 0 R >>\n".encode("latin-1")
    buf += b"startxref\n"
    buf += f"{xref_offset}\n".encode("latin-1")
    buf += b"%%EOF"
    return bytes(buf)
