from dataclasses import dataclass

@dataclass(frozen=True)
class ParsedError:
    """Represents a parsed error from the error journal."""
    language: str
    error_type: str
    message: str = ""
    file: str | None = None
    line: int | None = None

def parse_python(stderr: str) -> list[ParsedError]:
    """Parse Python tracebacks."""
    # do this later
    return []

def parse_java(stderr: str) -> list[ParsedError]:
    """Parse Javac output."""
    # do this later
    return []