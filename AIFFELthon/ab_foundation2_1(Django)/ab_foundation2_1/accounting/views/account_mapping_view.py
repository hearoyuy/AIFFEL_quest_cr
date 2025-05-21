from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from accounting.modules.rag_matching.account_matcher import match_accounts

@csrf_exempt
def match_account_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            article_name = data.get("article_name")
            context = {
                "price": data.get("price"),
                "vat": data.get("vat"),
                "payment_method": data.get("payment_method"),
                "invoice_type": data.get("invoice_type"),
                "country_code": data.get("country_code"),
                "additional_notes": data.get("additional_notes"),
            }
            result = match_accounts(article_name, context)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "POST method required"}, status=400)
