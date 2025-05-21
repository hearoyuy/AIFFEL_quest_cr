from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

def financial_position_view(request: HttpRequest) -> HttpResponse:
    # financial_position.html 템플릿을 렌더링
    return render(request, 'accounting/financial_statements/financial_position.html')
