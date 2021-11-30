import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class ConsumidorChat(WebsocketConsumer):

    def connect(self):
        self.id = self.scope['url_route']['kwargs']['curso_id']
        #self.sala_group_name = f'chat_{self.id}'
        self.sala_group_name = 'chat_%s' % self.id

        # associando ao grupo da sala
        async_to_sync(self.channel_layer.group_add)(
            self.sala_group_name,
            self.channel_name
        )
        # aceita a conexão
        self.accept()

    def disconnect(self, code):
        # saindo do group
        async_to_sync(self.channel_layer.group_discard)(
            self.sala_group_name,
            self.channel_name
        )

    # recebendo um mensagem pelo WebSocket
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # enviar para o Websocket
        async_to_sync(self.channel_layer.group_send)(
            self.sala_group_name,
            {
                'type': 'chat_message',
                'message': message,
            }
        )

    # recebendo a mensagem do grupo
    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message
        }))
