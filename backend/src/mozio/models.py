from django.db.models import (
    Model, CharField, EmailField, DecimalField,
    ForeignKey, CASCADE
)
from django.contrib.gis.db.models import PolygonField
from djmoney.models.fields import CurrencyField
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator


class Provider(Model):
    name = CharField(max_length=100)
    email = EmailField(blank=True, null=True)
    phone = PhoneNumberField(blank=True, null=True)
    cur = CurrencyField(default='usd')

    def __str__(self):
        return "{}({})".format(self.name, self.id)


class Service(Model):
    provider = ForeignKey(Provider, on_delete=CASCADE)
    name = CharField(max_length=100)
    price = DecimalField(
        decimal_places=4, max_digits=6, validators=[MinValueValidator(0)]
    )
    poly = PolygonField(blank=False, null=False)

    def __str__(self):
        return "{}({},{}): {}".format(
            self.provider.name, self.id, self.name, self.poly
        )
