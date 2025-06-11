from flask_restx import Api, Resource, fields

from server import token_required, app

# Инициализация API
api = Api(
    app,
    version='1.0',
    title='Trello-like API',
    description='A simple Trello-like API with JWT authentication',
    doc='/swagger/'
)

# Пространство имен для аутентификации
auth_ns = api.namespace('auth', description='Authentication operations')
users_ns = api.namespace('users', description='User operations')
tasks_ns = api.namespace('tasks', description='Task operations')

# Модели для Swagger
user_model = api.model('User', {
    'id': fields.Integer(readOnly=True, description='User identifier'),
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(description='Email address'),
    'photo_url': fields.String(description='URL to user photo')
})

task_model = api.model('Task', {
    'id': fields.Integer(readOnly=True, description='Task identifier'),
    'title': fields.String(required=True, description='Task title'),
    'description': fields.String(description='Task description'),
    'priority': fields.Integer(description='Priority (1-5)', enum=[1, 2, 3, 4, 5]),
    'status': fields.String(description='Task status', enum=['todo', 'in_progress', 'review', 'done']),
    'created_at': fields.DateTime(description='Creation date'),
    'due_date': fields.DateTime(description='Due date'),
    'creator': fields.Nested(user_model, description='Task creator'),
    'assignee': fields.Nested(user_model, description='Task assignee', allow_null=True)
})

login_model = api.model('Login', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

token_model = api.model('Token', {
    'access_token': fields.String(description='Access token'),
    'refresh_token': fields.String(description='Refresh token'),
    'user_id': fields.Integer(description='User ID')
})

# Пример защищенного эндпоинта в Swagger
@tasks_ns.route('/')
class TaskList(Resource):
    @tasks_ns.doc('list_tasks')
    @tasks_ns.marshal_list_with(task_model)
    @tasks_ns.doc(security='Bearer')
    @token_required
    def get(self, current_user):
        """List all tasks"""
        # Ваш код получения задач