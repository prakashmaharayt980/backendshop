
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from .models import Product

user = get_user_model()

class Wishlist(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    product= models.ForeignKey(Product,on_delete=models.CASCADE ,related_name='wish_list_product')
    user =models.ForeignKey(user,on_delete=models.CASCADE,related_name='wish_list_user')
    created_at=models.DateTimeField(auto_now_add=True)

    class meta :
        unique_together=('product','user')
        ordering=['-created_at']
    
    def __str__(self):
        return f"Wishlist({self.user.username} - {self.product.name})"
    


class AddCart(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    product= models.ForeignKey(Product,on_delete=models.CASCADE ,related_name='cart_product')
    user =models.ForeignKey(user,on_delete=models.CASCADE,related_name='cart_user')
    created_at=models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"AddCart({self.user.username} - {self.product.name})"