from channels.generic.websocket import AsyncWebsocketConsumer
import json

class LiveStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.group_name = f"live_{self.session_id}"

        # إضافة المستخدم للمجموعة
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # إزالة المستخدم من المجموعة
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        # إرسال البيانات لكل المشتركين في المجموعة
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'stream_message',
                'message': text_data_json,
            }
        )

    async def stream_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))