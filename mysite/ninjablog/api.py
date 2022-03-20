from ninja import Router

router = Router()


@router.get('/blogs')
def list_blogs(request):
    return {"blog_id": 1, "blog_title": "title1"}


@router.get('/blogs/{blog_id}')
def blog(request, blog_id):
    return {"blog_id": blog_id, "blog_title": "title1"}