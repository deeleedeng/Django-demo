import datetime
import random
from datetime import date
from typing import List, Generic, TypeVar, Optional

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from pydantic import Field
from pydantic.fields import ModelField

from django.contrib.auth.models import User, Group
from ninja import NinjaAPI, Schema, Path, Query, Form, File, ModelSchema, Router
from ninja.files import UploadedFile
from ninja.responses import codes_4xx
from ninja.security import django_auth, HttpBearer, HttpBasicAuth, APIKeyQuery, APIKeyHeader, APIKeyCookie


"""
Ninja 可定义请求解析器，比如：YAML XML CSV 更快的 JSON 解析
"""

# import yaml
# from ninja.parser import Parser
#
#
# class MyYamlParser(Parser):
#     # 解析 Yaml 格式请求
#
#     def parse_body(self, request):
#         return yaml.safe_load(request.body)
#
#
# api = NinjaAPI(parser=MyYamlParser())
#
#
# class ORJSONParser(Parser):
#     # 使用 ORJSON 包解析 Json 请求，更快，更准确
#
#     def parse_body(self, request):
#         return orjson.loads(request.body)
#
#
# api = NinjaAPI(parser=ORJSONParser())
#
#
# class Payload(Schema):
#     ints: List[int]
#     string: str
#     f: float
#
#
# def operation(request, payload: Payload):
#     return payload.dict()

"""
reqeust------
ints:
 - 0
 - 1
string: hello
f: 3.14

response------
{
  "ints": [
    0,
    1
  ],
  "string": "hello",
  "f": 3.14
}
"""


"""
Ninja 可定义相应渲染，比如：相应 XML JSON 格式
"""

from ninja.renderers import BaseRenderer


# 返回文本
# class MyRrenderer(BaseRenderer):
#     media_type = "text/plain"
#
#     def render(self, request, data, *, response_status):
#         return ...
#
#
# api = NinjaAPI(renderer=MyRrenderer())
#
#
# # 返回 JSON（使用 orjson）
# import orjson
#
#
# class ORJSONRenderer(BaseRenderer):
#     media_type = "application/json"
#
#     def render(self, request, data, *, response_status):
#         return orjson.dumps(data)
#
#
# api = NinjaAPI(renderer=ORJSONRenderer())
#
#
# # 返回 XML
# from io import StringIO
# from django.utils.encoding import force_str
# from django.utils.xmlutils import SimplerXMLGenerator
#
#
# class XMLRenderer(BaseRenderer):
#     media_type = "text/xml"
#
#     def render(self, request, data, *, response_status):
#         stream = StringIO()
#         xml = SimplerXMLGenerator(stream, "utf-8")
#         xml.startDocument()
#         xml.startElement("data", {})
#         self._to_xml(xml, data)
#         xml.endElement("data")
#         xml.endDocument()
#         return stream.getvalue()
#
#     def _to_xml(self, xml, data):
#         if isinstance(data, (list, tuple)):
#             for item in data:
#                 xml.startElement("item", {})
#                 self._to_xml(xml, item)
#                 xml.endElement("item")
#         elif isinstance(data, dict):
#             for key, value in data.items():
#                 xml.startElement(key, {})
#                 self._to_xml(xml, value)
#                 xml.endElement(key)
#         elif data is None:
#             pass
#         else:
#             xml.characters(force_str(data))
#
#
# api = NinjaAPI(renderer=XMLRenderer())


api = NinjaAPI(auth=django_auth, csrf=True)


@api.get("/hello", auth=None)
def hello(request):
    return "Hello world"


"""
ninja HTTP 请求方式
inja 支持如 GET POST PUT DELETE 等 HTTP 请求方式，同一路由可同时支持多种方式
"""


@api.get('/path')
def get_operation(request):
    ...


@api.post('/path')
def post_operation(request):
    ...


@api.put('/path')
def put_operation(request):
    ...


@api.delete('/path')
def delete_operation(request):
    ...


@api.patch('/path')
def patch_operation(request):
    ...


@api.api_operation(['GET', 'POST'], '/path')
def mix(request):
    ...


""""
ninja 实现路由带路径参数
1. 使用 Scheme，Path 用来告诉 ninja，date 需要用于路径参数
"""


# 单个参数
@api.get('/items/{item_id}')
def read_item(request, item_id: int):
    return {"item_id": item_id}


# 多个参数
@api.get('/events/{year}/{month}/{day}')
def events(request, year: int, month: int, day: int):
    return {"date": [year, month, day]}


class PathDate(Schema):
    year: int
    month: int
    day: int

    def value(self):
        return datetime.date(self.year, self.month, self.day)


@api.get('/event/{year}/{month}/{day}')
def event(request, date: PathDate = Path(...)):
    return {"date": date.value()}


"""
ninja 使用查询参数，如果参数没有声明类型，ninja 会默认为 str 类型
1. 如果参数设置的默认值，则表明参数是可选，否则为必选
2. Query 类会把请求参数处理成一个 dict
3. Field 将请求/相应字段设置一个别名
"""

weapons = ["Ninjato", "Shuriken", "Katana", "Kama", "Kunai", "Naginata", "Yari"]


@api.get('/weapons')
def list_weapons(request, limit: int = 10, offset: int = 0):
    return weapons[offset: offset + limit]


@api.get('weapons/search')
def weapons_search(request, q: str, offset: int = 0):
    results = [w for w in weapons if q in w.lower()]
    print(q, results)
    return results[offset: offset + 10]


@api.get('/example')
def example(request, s: str = None, b: bool = None, d: date = None, i: int = None):
    return [s, b, d, i]


class Filters(Schema):
    limit: int = 100
    offset: int = None
    query: str = None
    category__in: List[str] = Field(None, alias='categories')


@api.get('/filter')
def filters(request, filters: Filters = Query(...)):
    return {"filter": filters.dict()}


"""
ninja 定义 POST 接口
1. 需使用 ninja 的 Schema 类，Schema 会将请求参数转化成 dict
2. ninja 支持 post 请求中同时带请求体+路径参数
3. ninja 支持 post 请求中同时带请求体+路径参数+查询参数

函数参数将被识别如下：
1. 如果参数也在path中声明，它将被用作路径参数。
2. 如果参数是单数类型（如int、float、str、bool等），它将被解释为查询参数。
3. 如果参数被声明为Schema（或 Pydantic BaseModel）的类型，它将被解释为 request body。
"""


class Item(Schema):
    name: str
    description: str = None
    price: float
    quantity: int


@api.post('/item')
def create(request, item: Item):
    return item


@api.post('/create1/{item_id}')
def create1(request, item_id: int, item: Item):
    return {"item_id": item_id, "item": item.dict()}


@api.post('/create2/{item_id}')
def create2(request, item_id: int, item: Item, q: str):
    return {"item_id": item_id, "item": item.dict(), "q": q}


"""
ninja API 处理表单 form 数据
1. Form() 类识别 form-data 格式数据，application x-www-form-urlencoded 或 multipart/form-data
2. 如果参数传值为 None，ninja 会默认处理成空 str，可以使用 pytantic 转换为原始值
3. Optional 表示可以为空值，Optional[str] 等价于 str = None
"""


class LoginItem(Schema):
    username: str = None
    password: Optional[str]


@api.post('/login')
def login(request, username: str = Form(...), password: str = Form(...)):
    return {"username": username, "password": password}


@api.post('/login2')
def login2(request, login_item: LoginItem = Form(...)):
    return login_item.dict()


@api.post('/login3/{item_id}')
def login3(request, item_id: int, q: str, login_item: LoginItem = Form(...)):
    return {"item_id": item_id, "q": q, "login": login_item}


PydanticField = TypeVar("PydanticField")


class EmptyStrToDefault(Generic[PydanticField]):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: PydanticField, field: ModelField) -> PydanticField:
        if value == "":
            return field.default
        return value


class UpdateItem(Schema):
    name: str
    description: str = None
    price: EmptyStrToDefault[float] = 0.0
    quantity: EmptyStrToDefault[int] = 0
    in_stock: EmptyStrToDefault[bool] = True


@api.post('/update')
def update(request, item: UpdateItem):
    return item.dict()


"""
ninja 实现文件/图片上传
1. 使用 UploadFile，以及 File 类
"""


@api.post('/upload')
def upload(request, file: UploadedFile = File(...)):
    data = file.read()
    return {"name": file.name, "len": len(data)}


@api.post('/uploadmulti')
def upload_multi(request, file: List[UploadedFile] = File(...)):
    return [f.name for f in file]


"""
ninja 定义返回体参数
1. UserIn 和 UserOut 都可以嵌套，只需要声明对应参数的类型即可
"""


class UserIn(Schema):
    username: str
    password: str
    email: str


class UserOut(Schema):
    id: int
    username: str
    email: str


@api.post('/users', response=UserOut)
def create_user(request, data: UserIn):
    user = User(username=data.username)
    user.set_password(data.password)
    user.email = data.email
    user.save()
    return user


"""
ninja 实现根据响应码返回 response
1. 自定义 response，根据 key 来决定返回那部分内容
2。 使用 ninja 的 response 方法集合
"""


class Token(Schema):
    token: str
    expires: date


class Message(Schema):
    message: str


@api.post('/login4', response={200: Token, 401: Message, 402: Message, 500: None})
def login4(request, payload: int):
    if payload == 0:
        return 401, {'message': 'Unauthorized'}
    if payload == 1:
        return 402, {'message': 'Insufficient balance amount. Please proceed to a payment page.'}
    if payload == 2:
        return 500, None
    return 200, {'token': payload}


@api.post('/login5', response={200: Token, codes_4xx: Message})
def login5(request, payload: int):
    if payload == 0:
        return 401, {'message': 'Unauthorized'}
    if payload == 1:
        return 402, {'message': 'Insufficient balance amount. Please proceed to a payment page.'}
    return 200, {'token': payload, "expires": datetime.datetime.now()}


"""
ninja 实现增删改查功能
django models：Departmen, Employee
"""

from .models import Employee, Department


class EmployeeIn(Schema):
    first_name: str
    last_name: str
    department_id: int = None
    brithdate: date = None


class EmployeeOut(Schema):
    id: int
    first_name: str
    last_name: str
    department_id: int = None
    brithdate: date = None


# 创建接口， title 数据
@api.post('/deparment')
def create_title(request, title: str):
    department = Department.objects.create(title=title)
    return {"id": department.id}


# 创建接口， employee 数据，创建前需知道 title.id，否则会创建失败
@api.post('/employee')
def create_employee(request, payload: EmployeeIn):
    employee = Employee.objects.create(**payload.dict())
    return {"id": employee.id}


# 查询结果，empolyee 数据，返回单个
@api.post('/employee/{employee_id}', response=EmployeeOut)
def get_employee(request, employee_id: int):
    employee = get_object_or_404(Employee, id=employee_id)
    return employee


# 返回全部
@api.post('/employees', response=List[EmployeeOut])
def get_employees(request):
    employees = Employee.objects.all()
    return employees


# 更新接口，employee 数据
@api.put('/employeeupdate/{employee_id}')
def update_employee(request, employee_id: int, payload: EmployeeIn):
    employee = get_object_or_404(Employee, id=employee_id)
    for attr, value in payload.dict().items():
        print(attr, value)
        setattr(employee, attr, value)  # python 自带方法，根据 k-v set 到 employee 对象
    employee.save()
    return {"success": True}


# 删除接口，empoyee 数据，物理删除
@api.delete('/employeedelete/{employee_id}')
def delete_employee(request, employee_id: int):
    employee = get_object_or_404(Employee, id=employee_id)
    employee.delete()
    return {"success": True}


"""
ninja 可提供继承 django 模型的 Schema 定义方式
1. 使用 ModelSchema，来定义 User Schema
"""


# 一般的写法
class UserSchema(Schema):
    id: int
    username: str
    first_name: str
    last_name: str


# 使用 django 的 User model
class UserSchemaDjango(ModelSchema):
    class Config:
        model = User
        model_fields = ['id', 'username', 'first_name', 'last_name']


# 使用 User 模型中所有的字段，但不建议使用所有字段，因为会存在暴露过多数据的风险，比如密码
class UserSchemaDjangoAll(ModelSchema):
    class Config:
        model = User
        model_fields = "__all__"


# 排除 User 中的部分字段
class UserSchemaDjangoExclude(ModelSchema):
    class Config:
        model = User
        model_exclude = ['password', 'last_login', 'user_permissions']


# 覆盖 User 中的部分字段
class GroupSchema(ModelSchema):
    class Config:
        model = Group
        model_fields = ['id', 'name']


class UserSchemaDjangoUpdate(ModelSchema):
    groups: List[GroupSchema] = []

    class Config:
        model = User
        model_fields = ['id', 'username', 'first_name', 'last_name']


"""
ninja 的接口认证
0. 默认情况下，ninja 对所有操作都关闭 django 的 CSRF，要打开它，需要在实例化 NinjaAPI 时指明 cstr=True；
   但是，将 NinjaAPI 与基于 cookie 的身份认证一起使用是不安全的（比如 CookieKey 或者 django_auth），所以需要打开 CSRT 检查
1. 使用 django 的会话认证（默认是 cookie）
2. 如果需要对所有 NinjaAPI 进行认证，可以通过 api = NinjaAPI(auth=GlobalAuth()) 实现，同时需要对部分 API 不设置认证，则可以对该
   API 操作 def api(auth=None) 实现
"""


@api.get('/pets', auth=django_auth)
def pets(request):
    return f"Authenticated user {request.auth}"


# 基于 http 参数认证
class AuthBearer(HttpBearer):
    def authenticate(self, request, token: str):
        if token == 'supersecret':
            return token


# 单个 NinjaAPI，基于 HTTP 请求参数的认证
@api.get('/bearer', auth=AuthBearer())
def bearer(request):
    return {"token": request.auth}


# 基于 htt 基本身份认证
class BasicAuth(HttpBasicAuth):

    def authenticate(self, request, username, password):
        if username == 'admin' and password == 'secret':
            return username


@api.get('/basic', auth=BasicAuth())
def basic(request):
    return {"httpuser": request.auth}


# 自定义可用的身份认证方法
def ip_whitelist(request):
    if request.META["REMOTE_ADDR"] == "127.0.0.1":
        return "8.8.8.8"


@api.get('/ipwhitelist', auth=ip_whitelist)
def ipwhitelist(request):
    return f"Authenticated client, IP = {request.auth}"


# 使用 API 密钥，比如：
# 在请求参数中携带：GET /something?api_key=abcdef12345
# 在请求头中携带：GET /something HTTP/1.1， X-API-Key: abcdef12345
# 作为 cookie 携带：GET /something HTTP/1.1， Cookie: X-API-KEY=abcdef12345


# 在 query 中携带：
Model_Client = {"ninja": "ninja"}


class ApiKeyQuery(APIKeyQuery):
    param_name = 'api_key'

    def authenticate(self, request, key):
        try:
            print(Model_Client[key])
            return Model_Client[key]
        except KeyError:
            pass


api_key_query = ApiKeyQuery()


@api.get('/apikeyquery', auth=api_key_query)
def apikeyquery(request):
    print(request.auth)
    assert isinstance(request.auth, int)
    return f"Hello {request.auth}"


# 在 header 中携带
class ApiKeyHeader(APIKeyHeader):
    param_name = 'X-API-Key'

    def authenticate(self, request, key):
        if key == 'supersecret':
            return key


api_key_header = ApiKeyHeader()


@api.get('/apikeyheader', auth=api_key_header)
def apikeyheader(request):
    return f"Token = {request.auth}"


# 在 cookie 中携带
class ApiKeyCookie(APIKeyCookie):

    def authenticate(self, request, key):
        if key == 'supersecret':
            return key


api_key_cookie = ApiKeyCookie()


@api.get('/apikeycookie', auth=api_key_cookie)
def apikeycookie(request):
    return f"Cookie = {request.auth}"


# 同时设置多个身份认证器，只要其中一个认证通过即可，按顺序校验

class AuthCheck:

    def authenticate(self, request, key):
        if key == 'supersecret':
            return key


class QueryKey(AuthCheck, APIKeyQuery):
    pass


class HeaderKey(AuthCheck, APIKeyHeader):
    pass


@api.get('/multipleauth', auth=[QueryKey(), HeaderKey()])
def multiple_auth(request):
    return f"Token = {request.auth}"


# 路由认证/标签：可以通过请求的路由设置 auth 认证
# events_router = Router()
# api.add_router('/router', events_router, auth=BasicAuth, tags=['ninjademo'])

# 或者使用路由器构造函数/标签
# router = Router(auth=BasicAuth, tags=['ninjademo'])


# 自定义认证过程中异常
class InvalidToken(Exception):
    pass


@api.exception_handler(InvalidToken)
def on_invalid_token(request, exc):
    return api.create_response(request, {"detail": "Invalid token supplied", "message": str(exc)}, status=401)


class AuthBearer1(HttpBearer):

    def authenticate(self, request, token):
        if token == 'supersecret':
            return token
        raise InvalidToken


@api.get('/bearer1', auth=AuthBearer1())
def bearer1(request):
    return {"token": request.auth}


"""
URL 的反向解析
1. NinjaAPI 的 url 都包含在一个默认的命名空间 "api-1.0.0" 中，并且每个 URL 名称都与它所修饰的函数相匹配
2. 可以通过装饰器的 url_name 属性更改 URL 名称
3. 可以通过覆盖默认 Schema 类的 urls_namespace 属性来显式指定命名空间
"""


# URL 的生成
@api.get('/urlgen')
def urlgen(request):
    ...


# gen_url = reverse_lazy("api-1.0.0:urlgen")


# 更改 URL 名称
@api.get('/urlupdate', url_name='url_update')
def urlupdate(reqeust):
    ...


# update_url = reverse_lazy("api-1.0.0:urlupdate")


# 自定义命名空间

# api1 = NinjaAPI(auth=BasicAuth, version='2')
# api_privete = NinjaAPI(auth=BasicAuth, urls_namespace='private_api')
#
# api_users_url = reverse_lazy('api-2:users')
# private_api_admins_url = reverse_lazy('private_api:admins')


"""
NinjaAPI 提供的操作参数集合
1. 通过 tags 标签把 api 进行分组（也可以通过 router 的 tags 定义分组）
2. 通过 summary 添加 api 的概要（默认为方法名）
3. 通过 description 定义 api 的详情概要（也可以通过标准 docsting 进行描述）
4. 通过 opration_id 属性标识操作的来源（也可以通过覆盖 NinjaAPI 实例的 get_openapi_operation_id 方法）
5. 通过 deprecated 属性标识该 API 已被弃用
6. 通过 by_alias 属性标识 response 是否使用别名作为字段名，默认 false
7. 通过 exclude_unset 属性标识 response 中是否排除没有设置默认值的字段， 默认 false
8. 通过 exclude_defaults 属性标识 response 中是否排查等于其默认值（无论是否设置）的字段，默认 false
9. 通过 exclude_none 属性标识 response 中是否排查为 None 的字段
10. 通过 include_in_schema 属性标识是否在文档中展示该 API
11. 通过 url_name 属性设置 api 文档的 url 名称
"""


# 1
@api.post('/group', tags=['group'])
def groups(request):
    return {"success": True}


# 2
@api.post('/summary', summary='My sumaary', tags=['group','group2'])
def my_summare(request):
    return {"success": True}


# 3
@api.post('/desc1', description="This is a desc1", tags=['group', 'group2'])
def desc1(request):
    return {"success": True}


@api.post('/desc2', tags=['group'])
def desc2(request):
    """
    This is a desc2
    """
    return {"success": True}


# 4
@api.get('/newtask', operation_id='create_task', tags=['group', 'group1'])
def new_task(request):
    return {"success": True}


"""
class MySuperApi(NinjaAPI):

    def get_openapi_operation_id(self, operation) -> str:
        # 定义 operation
        return "True"


my_super_api = MySuperApi()


@my_super_api.get(...)
def my_super_api(request):
    return {"success": True}
"""


@api.post('oldmethod', deprecated=True, tags=['group', 'group1'])
def some_old_method(request):
    return {"success": True}


"""
Ninja 处理程序异常
1. 可自定义异常，使用 api.exception_handler 装饰器
2. ninja.error 自带多种异常，也可以重新定义进行覆盖
"""


# 自定义异常
class ServiceUnavailableError(Exception):
    pass


@api.exception_handler(ServiceUnavailableError)
def service_unavailable(request, exc):
    return api.create_response(
        request,
        {"message": "Please retry late","error": str(exc)},
        status=503
    )


@api.get('/exc')
def some_excepiton(request):
    if random.choice([True, False]):
        raise ServiceUnavailableError
    return {"message": "Hello"}


# 覆盖异常
from ninja.errors import ValidationError, HttpError
from django.http import HttpResponse


@api.exception_handler(ValidationError)
def validation_errors(reqeust, exc):
    return HttpResponse("Invalid input", status_code=422)


# 抛出带有异常的 HTTP 相应
@api.get('/exc1')
def some_excepiton1(request):
    if random.choice([True, False]):
        raise HttpError(503, "Service Unavailable.")
    return {"message": "Hello"}


"""
Ninja 对异步 API 的定义
1. django 在 3.1 版本后开始支持异步
2. 异步代码需要使用 asycio 库，以及 async、await 关键字
3. 运行异步 API 需要 ASGI 服务器支持，可以通过 Uvicom/Daphne 三方包实现，也可以 使用 manage.py runserver，但可能不支持某些库
4. Elasticsearch 异步的日志搜索引擎 ES，在 ninja 中的使用
5. 异步使用 ORM

"""

import time
import asyncio
from elasticsearch import Elasticsearch


async def task1(num):
    await asyncio.sleep(1)
    print("-----开始执行异步代码")
    await asyncio.sleep(num)
    print("------结束执行异步")


# 同步 API
@api.get('/sync-say-after', tags=['sync&async'], auth=None)
def sync_say_after(request, delay: int, word: str):
    time.sleep(delay)
    return {"saying": word}


# 异步 API
@api.get('/async-say-after', tags=['sync&async'], auth=None)
async def asnyc_say_after(request, delay: int, word: str):
    # loop = asyncio.get_event_loop()
    # loop.create_task(task1(num=delay)) # 写法一
    asyncio.create_task(task1(num=delay))
    print("------其他立即打印-------")
    return {"saying": word}


# es = Elasticsearch()
#
#
# # ES 的接口实现
# @api.get('/search-es', tags=['sync&async'], auth=None)
# async def search_es(request, q: str):
#     resp = await es.search(
#         index="documents",
#         body={"query": {"query_string": {"query": q}}},
#         size=20
#     )
#     return resp["hits"]


from asgiref.sync import sync_to_async
from polls.models import Question


@sync_to_async
def get_questions():
    return Question.objects.all()


# 没搞懂运行报错
@api.get("/questions", tags=['sync&async'], auth=None)
async def search(request):
    questions = get_questions()
    print(questions.throw())
    return {"question": "1"}















