import os
import hashlib
from typing import Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter

_CHUNK_SIZE = int(os.getenv("TEXT_CHUNK_SIZE", "1000"))
_CHUNK_OVERLAP = int(os.getenv("TEXT_CHUNK_OVERLAP", "200"))

_language_separators = {
    "python": ["\nclass ", "\ndef ", "\n    ", "\n\t", "\n", " ", ""],
    "javascript": ["\nclass ", "\nfunction ", "\nconst ", "\nlet ", "\nvar ", "\n    ", "\n\t", "\n", " ", ""],
    "typescript": ["\nclass ", "\nfunction ", "\nconst ", "\nlet ", "\nvar ", "\n    ", "\n\t", "\n", " ", ""],
    "java": ["\nclass ", "\npublic ", "\nprivate ", "\nprotected ", "\n    ", "\n\t", "\n", " ", ""],
    "go": ["\nfunc ", "\ntype ", "\n    ", "\n\t", "\n", " ", ""],
    "rust": ["\nfn ", "\nstruct ", "\nenum ", "\nimpl ", "\n    ", "\n\t", "\n", " ", ""],
    "cpp": ["\nclass ", "\nvoid ", "\nint ", "\n    ", "\n\t", "\n", " ", ""],
    "default": ["\n\n", "\n", " ", ""],
}

_code_extensions = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".cpp": "cpp",
    ".c": "cpp",
    ".h": "cpp",
    ".hpp": "cpp",
}


def _detect_language(file_name: str) -> str:
    ext = os.path.splitext(file_name)[1].lower()
    return _code_extensions.get(ext, "default")


def _make_splitter(file_name: str, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None) -> RecursiveCharacterTextSplitter:
    language = _detect_language(file_name)
    separators = _language_separators.get(language, _language_separators["default"])
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or _CHUNK_SIZE,
        chunk_overlap=chunk_overlap or _CHUNK_OVERLAP,
        separators=separators,
        length_function=len,
    )


def _generate_chunk_id(file_name: str, chunk_index: int) -> str:
    raw = f"{file_name}:{chunk_index}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def split_file_content(
    file_name: str,
    content: str,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> list[dict]:
    if not content or not content.strip():
        return []

    splitter = _make_splitter(file_name, chunk_size, chunk_overlap)
    chunks = splitter.split_text(content)

    return [
        {
            "chunk_id": _generate_chunk_id(file_name, i),
            "content": chunk,
            "metadata": {
                "source_file": file_name,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "language": _detect_language(file_name),
            },
        }
        for i, chunk in enumerate(chunks)
    ]


def split_files(
    files: list[dict],
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> list[dict]:
    all_chunks = []
    for file in files:
        chunks = split_file_content(
            file_name=file.get("name", ""),
            content=file.get("content", ""),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        all_chunks.extend(chunks)
    return all_chunks
