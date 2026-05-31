import mimetypes

from django.conf import settings
from django.db.models import Prefetch
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Product, ProductImage, Cart, CartItem
from django.views.decorators.http import require_POST
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from django.shortcuts import get_object_or_404
from django.contrib import messages

class ItemDraft(BaseModel):
    title: str = Field(description="Short product title.")
    description: str = Field(description="Short product description.")
    category: str = Field(description="One of clothes, footwear, accessories.")
    condition: str = Field(description="One of new, like_new, good, fair, used.")


AI_ITEM_DRAFT_PROMPT = """
You are helping a thrift store seller draft a product listing from uploaded images.
Look at the images and return only JSON that matches the schema.

Rules:
- title should be short, natural, and specific
- description should be 1 to 3 sentences and describe the item clearly
- category must be one of: clothes, footwear, accessories
- condition must be one of: new, like_new, good, fair, used
- if something is unclear, pick the safest neutral option
""".strip()

@login_required(login_url='login')
@require_POST
def analyze_item_draft(request):
    images = request.FILES.getlist('images')

    if not images:
        return JsonResponse({"error": "Please upload at least one image."}, status=400)

    if not settings.GEMINI_API_KEY:
        return JsonResponse({"error": "GEMINI_API_KEY is not configured."}, status=500)

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    contents = []
    for image in images:
        image_bytes = image.read()
        image.seek(0)
        mime_type = image.content_type or mimetypes.guess_type(image.name)[0] or "image/jpeg"
        contents.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            )
        )

    contents.append(AI_ITEM_DRAFT_PROMPT)

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=contents,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": ItemDraft.model_json_schema(),
            },
        )
        draft = ItemDraft.model_validate_json(response.text)
    except Exception as exc:
        return JsonResponse({"error": f"Gemini draft generation failed: {exc}"}, status=500)

    return JsonResponse(draft.model_dump())

# Create your views here.
def home(request):
    products = (
        Product.objects
        .prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.order_by('uploaded_at'))
        )
        .order_by('-created_at')
    )
    products_by_category = {
        'clothes': [],
        'footwear': [],
        'accessories': [],
    }

    for product in products :
        products_by_category[product.category].append(product)

    return render(request, 'thrift/home.html', {'products_by_category': products_by_category})

def account(request):
    return render(request, 'thrift/account.html')

def previous_orders(request):
    return render(request, 'thrift/previous_orders.html')

def edit_user_information(request):
    return render(request, 'thrift/edit_user_information.html')

@login_required(login_url='login')
def cart(request):

    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_items = (
        CartItem.objects
        .filter(cart=cart)
        .select_related('product')
        .prefetch_related('product__images')
        .order_by('-added_at')
    )

    total_price = sum(item.product.price for item in cart_items)
    
    return render(request, 'thrift/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

@login_required(login_url='login')
def add_item(request):
    if request.method == 'POST' :
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        condition = request.POST.get('condition')
        brand = request.POST.get('brand')
        size = request.POST.get('size')
        price = request.POST.get('price')
        images = request.FILES.getlist('images')

        product = Product.objects.create(
            seller=request.user,
            title=title,
            description=description,
            category=category,
            condition=condition,
            status='available',
            brand=brand,
            size=size,
            price=price,
        )
        print("Saved product:", product.id, product.title)
        for image in images:
            ProductImage.objects.create(product=product, image=image)

        return redirect('previous_listed_items')

    return render(request, 'thrift/add_item.html')

@login_required(login_url='login')
def previous_listed_items(request):
    products = (
        Product.objects
        .filter(seller=request.user)
        .prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.order_by('uploaded_at'))
        )
        .order_by('-created_at')
    )
    return render(request, 'thrift/previous_listed_items.html', {'products': products})

def about(request): 
    return HttpResponse('This is about')

@login_required(login_url='login')
@require_POST
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)

    if product.seller == request.user:
        return JsonResponse({'success': False, 'message': 'You cannot add your own item to cart.'}, status=400)

    if product.status == 'sold' :
        return JsonResponse({'success': False, 'message': 'This item is already sold.'}, status=400)
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if created:
        message = f'{product.title} added to cart.'
    else:
        message = f'{product.title} is already in your cart.'

    return JsonResponse({'success': True, 'message': message, 'cart_item_count': cart.cart_items.count()})
    
@login_required(login_url='login')
@require_POST
def remove_from_cart(request, id):
    cart_item = get_object_or_404(CartItem, id=id, cart__user=request.user)
    # Without it, one user could try to remove another user’s cart item by guessing the id.
    cart_item.delete()
    return redirect('cart')
    

        
 
