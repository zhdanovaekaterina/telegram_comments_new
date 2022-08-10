# <-- Message text section -->

# Help message with the list of available commands
help_message = '/help - помощь\n' \
               '/add - добавить пост\n' \
               '/clients - добавить клиента\n' \
               '/archive - архив'

# First message after bot start
start_message = f'С чего начнем?\n{help_message}'

# Ask the user which client should we add the post?
add_message = 'К какому клиенту добавляем новый пост?'

# Support message in client's menu
client_list_message = 'Ниже вы найдете список клиентов. ' \
                      'Выберите любого, чтобы посмотреть отслеживаемые посты. ' \
                      'Также вы можете добавить нового клиента.'

# Support message in post list
post_list_message = 'Ниже вы найдете список постов. ' \
                    'Выберите пост, чтобы посмотреть по нему краткую статистику.'

# Support message in archive menu
client_archive_message = 'Ниже вы найдете список клиентов, у которых есть посты в архиве. ' \
                         'Чтобы посмотреть посты, выберите клиента.'

# Support message in archive menu when there are no archive clients
empty_archive = 'Архив пока что пуст.'

# Support message when there are no clients yet in clients' menu
empty_client_list = 'Пока нет ни одного клиента. Хотите добавить первого?'

# Support message when there are no clients yet in post-add menu
empty_client_list_when_add = 'Пока не добавлено ни одного клиента. Для начала работы добавьте первого.'

# Support message when client don't have tracking posts yet
empty_post_list = 'У этого клиента пока нет отслеживаемых постов. Хотите добавить первый?'

# Support message in archive menu after client selection
client_posts_archive_message = 'Ниже вы найдете список постов в архиве. ' \
                                'Чтобы посмотреть подробнее, выберите пост.'

# Ask user to type post name (needed just to give pretty output in list)
ask_post_name = 'Введите название поста ниже (рекомендуется не длиннее 20 символов). ' \
                'Пожалуйста, не используйте в названии символ "_"'

# Ask user for the post link
ask_post_link = 'Введите ссылку на пост:'

# Ask user for the post link second time
ask_post_link_second_time = 'Похоже, это не ссылка на пост в телеграм. Пожалуйста, введите корректную ссылку ниже:'

# Archive client verification message
archive_client_verification = 'Вы точно хотите заархивировать этого клиента? ' \
                              'Он не будет значиться в списке клиентов, а все его активные посты будут заархивированы.'

# Ask user for client name
ask_client_name = 'Введите название компании:'

# Exit message
nothing_message = 'Хорошо, если понадоблюсь, используйте одну из команд.'

# Ask for password
ask_password = 'Для удаления поста введите пароль:'


# <-- Notification text section -->


# Successfully added post to db
success_add_post = 'Пост успешно добавлен к отслеживанию.'

# Post already exists in base
post_already_exists = 'Такой пост уже есть в базе? Хотите добавить другой пост?'

# Successfully archived post
success_archive_post = 'Пост больше не отслеживается.'

# Successfully archived client
success_archive_client = 'Клиент успешно перемещен в архив.'

# Successfully added client
success_add_client = 'Клиент успешно добавлен. Хотите добавить пост для этого клиента?'

# Client already exists
client_already_exists = 'В базе уже есть такой клиент! Хотите добавить для него пост или добавить нового клиента?'

# Post deleted successfully
deleted_successfully = 'Пост успешно удален из базы.'

# Wrong password typed
wrong_password = 'Пароль введен неверно. Попробуйте еще раз.'


# <-- Buttons text section -->


help_button = 'Помощь'
add_button = 'Добавить пост'
client_button = 'Добавить клиента'
archive_button = 'Архив'

# Add new client button
add_client_button = 'Добавить клиента'

# Add another post button
add_another_post = 'Добавить другой пост'

# Watch comments button
watch_comments = 'Посмотреть комментарии'

# Go to post button
go_to_post = 'Перейти к посту'

# Archive client button
archive_client = 'Архивировать клиента'

# Archive post button
archive_post = 'Архивировать пост'

# Add new post button
add_post = 'Добавить пост'

# Exit button
nothing = 'Ничего не хочу'

# Track again button
track_again = 'Отслеживать снова'

# Delete button
delete_post = 'Удалить окончательно'
