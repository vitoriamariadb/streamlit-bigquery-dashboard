import logging
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class Comment:
    """Comentario em um elemento do dashboard."""

    author: str
    content: str
    target_type: str
    target_id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    resolved: bool = False
    parent_id: Optional[str] = None
    comment_id: str = ""

    def __post_init__(self):
        if not self.comment_id:
            timestamp = self.created_at.strftime("%Y%m%d%H%M%S%f")
            self.comment_id = f"cmt_{timestamp}"


class CommentManager:
    """Gerenciador de comentarios para colaboracao."""

    def __init__(self):
        self._comments: dict[str, Comment] = {}
        self.logger: logging.Logger = logging.getLogger(__name__)

    def add_comment(self, comment: Comment) -> str:
        self._comments[comment.comment_id] = comment
        self.logger.info(
            "Comentario adicionado por %s em %s/%s",
            comment.author, comment.target_type, comment.target_id,
        )
        return comment.comment_id

    def get_comments(
        self,
        target_type: str,
        target_id: str,
        include_resolved: bool = False,
    ) -> list[Comment]:
        comments = [
            c for c in self._comments.values()
            if c.target_type == target_type and c.target_id == target_id
        ]
        if not include_resolved:
            comments = [c for c in comments if not c.resolved]
        return sorted(comments, key=lambda c: c.created_at)

    def resolve_comment(self, comment_id: str) -> bool:
        comment = self._comments.get(comment_id)
        if comment:
            comment.resolved = True
            comment.updated_at = datetime.now()
            self.logger.info("Comentario resolvido: %s", comment_id)
            return True
        return False

    def delete_comment(self, comment_id: str) -> bool:
        if comment_id in self._comments:
            del self._comments[comment_id]
            self.logger.info("Comentario removido: %s", comment_id)
            return True
        return False

    def get_thread(self, parent_id: str) -> list[Comment]:
        parent = self._comments.get(parent_id)
        if not parent:
            return []
        replies = [
            c for c in self._comments.values()
            if c.parent_id == parent_id
        ]
        return [parent] + sorted(replies, key=lambda c: c.created_at)

    def get_unresolved_count(self) -> int:
        return sum(1 for c in self._comments.values() if not c.resolved)

    @property
    def total_comments(self) -> int:
        return len(self._comments)

