from django.db import models
from django.urls import reverse
from django.template.defaultfilters import slugify


class Category(models.Model):
    title = models.CharField(max_length=200)
    sub_category = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        related_name='sub_categories', null=True, blank=True
    )
    is_sub = models.BooleanField(default=False)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('shop:filter_by_category', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='products')
    title = models.CharField(max_length=250)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('-date_created',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('shop:product_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_final_price(self):
        """If a discount is available, return the discounted price."""
        return self.discount_price if self.discount_price else self.price
