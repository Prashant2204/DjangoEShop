import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()

from django.core.files import File
from home.models import Product

products_data = [
    {
        'name': 'Bamboo Tooth Brush',
        'description': 'Eco-friendly bamboo toothbrush with soft bristles',
        'price': 4.99,
        'image': 'Bamboo_Tooth_Brush.png',
        'stock': 50
    },
    {
        'name': 'Bamboo Cotton Buds',
        'description': 'Sustainable bamboo cotton buds, 200 pieces',
        'price': 3.99,
        'image': 'Bamboo_Cotton_Buds.png',
        'stock': 30
    },
    {
        'name': 'Steel Lunchbox',
        'description': 'Stainless steel lunchbox with compartments',
        'price': 12.99,
        'image': 'Steel_Lunchbox.jpg',
        'stock': 20
    },
    {
        'name': 'Green Packaging Banana Leaves',
        'description': 'Natural banana leaves for eco-friendly packaging',
        'price': 8.99,
        'image': 'Green_Packaging_Banana_Leaves.png',
        'stock': 40
    },
    {
        'name': 'Bamboo Straws',
        'description': 'Set of 4 reusable bamboo straws with cleaning brush',
        'price': 6.99,
        'image': 'Bamboo_Straws.jpg',
        'stock': 25
    }
]

def create_products():
    for product_data in products_data:
        image_path = os.path.join('media', 'products', product_data['image'])
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                product = Product.objects.create(
                    name=product_data['name'],
                    description=product_data['description'],
                    price=product_data['price'],
                    stock=product_data['stock']
                )
                product.image.save(product_data['image'], File(f), save=True)
                print(f"Created product: {product.name}")

if __name__ == '__main__':
    create_products() 