from dataclasses import dataclass


@dataclass
class Task:
    """A task held only for the lifetime of the API process."""

    id: int
    title: str
    done: bool = False
