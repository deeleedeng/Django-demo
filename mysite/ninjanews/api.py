from ninja import Router

router = Router()


@router.get('/news')
def list_news(request):
    return {"new_id": 1, "new_title": "title1"}


@router.get('/news/{new_id}')
def new(request, new_id):
    return {"new_id": new_id, "new_title": "title1"}