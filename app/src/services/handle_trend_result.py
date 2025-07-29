from app.src.entity.tag import Tag
from app.src.adapter.aws.dynamo import DynamoAdapter
from app.src.adapter.aws.sqs import SqsAdapter
import re
import time

class HandleTrendResult:

    def __init__(self,
                 dynamo_adapter: DynamoAdapter,
                 sqs_adapter: SqsAdapter,
                 dynamo_table_name: str,
                 sqs_queue_name: str):
        self.dynamo_adapter = dynamo_adapter
        self.sqs_adapter = sqs_adapter
        self.sqs_queue_name = sqs_queue_name
        self.dynamo_table_name = dynamo_table_name

    def handle(self, posts: list[str]):
        existing_tags = self._get_existing_tags()
        new_tags = self._get_new_tags(posts = posts,
                                      existing_tags=existing_tags)
        self._update_existing_tags(new_tags=new_tags,
                                   existing_tags=existing_tags)
        self._send_to_sqs(new_tags)

    def _get_new_tags(self, posts: list[str], existing_tags: list[Tag]) -> list[str]:
        latest_tags = []
        for post in posts:
            if 'Tags' in post:
                tags = self._extract_tags_from_post(post)
                latest_tags.extend(tags)
            else:
                raise ValueError("No 'Tags' found in the post content.")
        existing_tags_name = [tag.name for tag in existing_tags]
        new_tags = []
        for tag in latest_tags:
            if tag not in existing_tags_name:
                new_tags.append(tag)
        return new_tags

    def _update_existing_tags(self, new_tags: list[str], existing_tags: list[Tag]) -> None:
        valid_tags = self._remove_expired_tags(existing_tags)
        new_tags_with_timestamps = [(Tag(tag)) for tag in new_tags]
        valid_tags.extend(new_tags_with_timestamps)
        self._save_updated_tags_dynamo(valid_tags)

    def _get_existing_tags(self) -> list[Tag]:
        item = self.dynamo_adapter.get_item(
            table_name=self.dynamo_table_name,
            key= {
                'type': 'cache',
                'id': 'tags'
            }
        )
        tags = []
        for tag_dict in item.get('tags'):
            tag = Tag(
                name=tag_dict['name'],
                created_at=tag_dict['created_at']
            )
            tags.append(tag)
        return tags

    def _save_updated_tags_dynamo(self, tags: list[Tag]) -> None:
        item = {
            'type': 'cache',
            'id': 'tags',
            'tags': [{'name': tag.name, 'created_at': tag.created_at} for tag in tags]
        }
        self.dynamo_adapter.put_item(
            table_name=self.dynamo_table_name,
            item=item
        )

    def _send_to_sqs(self, tags: list[str]) -> None:
        if not tags:
            return
        message = {
            'type': 'new_tags',
            'tags': tags
        }
        self.sqs_adapter.send_message(
            message=message
        )

    def _extract_tags_from_post(self, text: str) -> list[str]:
        tags = re.findall(r'#\w+', text)
        if not tags:
            raise ValueError("No tags found in the post content.")
        return tags

    def _remove_expired_tags(self, existing_tags: list[Tag]) -> list[Tag]:
        valid_tags = []
        for tag in existing_tags:
            if tag.created_at < time.time() - 24 * 60 * 60:
                valid_tags.append(tag)
        return valid_tags
