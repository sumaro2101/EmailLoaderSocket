# Title
Этот проект был написанн для динамической выгрузки Email сообщений из различных почтовых ящиков.
Реализация на основе WebSocket

# To Do
## Для выполенения данной задачи были реализованны классы:
1. AbstractConnection - Абстрактный класс определяющий каркас.
2. BaseConnection - Общий класс выполняющий базовые потребности, неоходим для паттерна "стратегия".

3. GmailConnection - Специализированный класс для подкючения Gmail почты.
4. YandexConnection - Специализированный класс для подкючения Yandex почты.
5. MailConnection - Специализированный класс для подкючения Mail почты.

Данные классы так же могут проверять подключение на уровне валидации, тем самым
проверяется достоверность почты.
Для данной проверки нужно указать дополнительный аргумент form который является окружением формы.

```Python
GmailConnection.connection(
                    login=address,
                    password=password,
                    form=form,
                )
```

Для подкючения и получения списка всех писем из ящика:
```Python
server = GmailConnection
connection = server(email.address,
                    email.password,
                    limit=email.last_index,
                    )
```
В данном случае важно указать limit, так как это послее зафиксированное Email сообщение
которое обработала программа.

Реализованны каркасные методы (магические).
```Python
len(connection) # Длина списка писем
connection[index] # Получить любое письмо по индексу
connection.reverse() # Список в обратном порядке
for item in connection: # Итеррация по списку
with connection as list_: # Менеджер открывает список писем
```

Для дальнейшей обработки списка нужен парсер.
Реализован класс:
1. Parser.
2. TextParser.
3. FileParser.

Класс Parser автоматически вмещает в себе остальные классы для обработки.
Для работы Parser, ему необходим только экземпляр Соединения IMAP4_SSL, а так же uid (ID сообщения)
```Python
parser = Parser(connection.server, uid)
message = parser.parse()
```
Это все что необходимо для выполнения работы Parser.
Parser отдает dict со всеми данными что получилось изьять из сообщения.

# WebSocket
## Для реализации WebSocket нужно:
1. Инициализировать экземпляр WebSocket в JavaSctipt
```JavaScript
const socket = new WebSocket(
        'ws://'
        + window.location.host
        + '/email/download/'
        + pk
        + '/'
    );
```
2. Определить действия для каждого события
```JavaScript
socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
};
socket.onopen = function(e) {
    // some move
};
socket.onclose = function(e) {
    this.close()
    console.log('Socket closed unexpectedly');
};
```
3. Написать потребителя AsyncWebsocketConsumer
4. Указать Routing
5. Изменить точку входа на asgi с помощью ProtocolTypeRouter с указание websocket
```Python
application = ProtocolTypeRouter(dict(
    http=django_asgi_app,
    websocket=AuthMiddlewareStack(
        URLRouter(
            mailscaner.routing.websocket_urlpatterns
        )
    ),
))
```
