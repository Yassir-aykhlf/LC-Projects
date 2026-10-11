class NotFoundError(Exception):
    pass


class ValidationError(Exception):
    pass


class CommentService:
    def __init__(self, post_store):
        self.post_store = post_store
        # TODO: Initialize your data structures and concurrency controls here.

    def add_comment(self, post_id: int, user_id: str, content: str) -> dict:
        """
        Create a comment and return its dictionary representation:

        {
            "id": int,
            "post_id": int,
            "user_id": str,
            "content": str,
            "created_at": float,
            "replies": []
        }

        Raises NotFoundError if post_id does not exist.
        Raises ValidationError if user_id or content is empty.
        """
        pass

    def add_reply(self, post_id: int, comment_id: int, user_id: str, content: str) -> dict:
        """
        Create a reply to a comment and return its dictionary representation:

        {
            "id": int,
            "post_id": int,
            "comment_id": int,
            "user_id": str,
            "content": str,
            "created_at": float
        }

        Raises NotFoundError if post_id does not exist.
        Raises NotFoundError if comment_id does not exist for the given post.
        Raises ValidationError if user_id or content is empty.
        """
        pass

    def get_comments(self, post_id: int) -> list:
        """
        Return all comments for the given post.

        Each comment must include its "replies" list.
        Comments and replies must be returned in creation order.

        Raises NotFoundError if post_id does not exist.
        """
        pass
