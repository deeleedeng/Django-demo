from ninja import NinjaAPI

from ninjablog.api import router as blog_router
from ninjanews.api import router as new_router


apis = NinjaAPI(version='2.0.0')

apis.add_router('/blogs/', blog_router, tags=['blog'])
apis.add_router('/news/', new_router, tags=['new'])
