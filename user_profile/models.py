from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from main.models import User, Buyer, Seller
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class BuyerProfile(models.Model):

    NATIONALITY_CHOICES = [
        ('Not Set', 'Not Set'),
        ('Afghan', 'Afghan'),
        ('Albanian', 'Albanian'),
        ('Algerian', 'Algerian'),
        ('American Samoan', 'American Samoan'),
        ('Andorran', 'Andorran'),
        ('Angolan', 'Angolan'),
        ('Anguillian', 'Anguillian'),
        ('Antiguan or Barbudan', 'Antiguan or Barbudan'),
        ('Argentine', 'Argentine'),
        ('Armenian', 'Armenian'),
        ('Aruban', 'Aruban'),
        ('Australian', 'Australian'),
        ('Austrian', 'Austrian'),
        ('Azerbaijani', 'Azerbaijani'),
        ('Bahamian', 'Bahamian'),
        ('Bahraini', 'Bahraini'),
        ('Bangladeshi', 'Bangladeshi'),
        ('Barbadian', 'Barbadian'),
        ('Belarusian', 'Belarusian'),
        ('Belgian', 'Belgian'),
        ('Belizean', 'Belizean'),
        ('Beninese', 'Beninese'),
        ('Bermudian', 'Bermudian'),
        ('Bhutanese', 'Bhutanese'),
        ('Bolivian', 'Bolivian'),
        ('Bosnian or Herzegovinian', 'Bosnian or Herzegovinian'),
        ('Botswanan', 'Botswanan'),
        ('Brazilian', 'Brazilian'),
        ('Bruneian', 'Bruneian'),
        ('Bulgarian', 'Bulgarian'),
        ('Burkinabe', 'Burkinabe'),
        ('Burundian', 'Burundian'),
        ('Cape Verdean', 'Cape Verdean'),
        ('Cambodian', 'Cambodian'),
        ('Cameroonian', 'Cameroonian'),
        ('Canadian', 'Canadian'),
        ('Caymanian', 'Caymanian'),
        ('Central African', 'Central African'),
        ('Chadian', 'Chadian'),
        ('Chilean', 'Chilean'),
        ('Chinese', 'Chinese'),
        ('Colombian', 'Colombian'),
        ('Comoran', 'Comoran'),
        ('Congolese', 'Congolese'),
        ('Congolese, Democratic Republic of', 'Congolese, Democratic Republic of'),
        ('Costa Rican', 'Costa Rican'),
        ('Croatian', 'Croatian'),
        ('Cuban', 'Cuban'),
        ('Cypriot', 'Cypriot'),
        ('Czech', 'Czech'),
        ('Danish', 'Danish'),
        ('Djiboutian', 'Djiboutian'),
        ('Dominican', 'Dominican'),
        ('Dominican (Republic)', 'Dominican (Republic)'),
        ('Ecuadorian', 'Ecuadorian'),
        ('Egyptian', 'Egyptian'),
        ('Salvadoran', 'Salvadoran'),
        ('Equatorial Guinean', 'Equatorial Guinean'),
        ('Eritrean', 'Eritrean'),
        ('Estonian', 'Estonian'),
        ('Ethiopian', 'Ethiopian'),
        ('Fijian', 'Fijian'),
        ('Finnish', 'Finnish'),
        ('French', 'French'),
        ('Gabonese', 'Gabonese'),
        ('Gambian', 'Gambian'),
        ('Georgian', 'Georgian'),
        ('German', 'German'),
        ('Ghanaian', 'Ghanaian'),
        ('Greek', 'Greek'),
        ('Grenadian', 'Grenadian'),
        ('Guatemalan', 'Guatemalan'),
        ('Guinean', 'Guinean'),
        ('Bissau-Guinean', 'Bissau-Guinean'),
        ('Guyanese', 'Guyanese'),
        ('Haitian', 'Haitian'),
        ('Honduran', 'Honduran'),
        ('Hungarian', 'Hungarian'),
        ('Icelander', 'Icelander'),
        ('Indian', 'Indian'),
        ('Indonesian', 'Indonesian'),
        ('Iranian', 'Iranian'),
        ('Iraqi', 'Iraqi'),
        ('Irish', 'Irish'),
        ('Israeli', 'Israeli'),
        ('Italian', 'Italian'),
        ('Jamaican', 'Jamaican'),
        ('Japanese', 'Japanese'),
        ('Jordanian', 'Jordanian'),
        ('Kazakhstani', 'Kazakhstani'),
        ('Kenyan', 'Kenyan'),
        ('Kiribati', 'Kiribati'),
        ('Kuwaiti', 'Kuwaiti'),
        ('Kyrgyzstani', 'Kyrgyzstani'),
        ('Lao', 'Lao'),
        ('Latvian', 'Latvian'),
        ('Lebanese', 'Lebanese'),
        ('Basotho', 'Basotho'),
        ('Liberian', 'Liberian'),
        ('Libyan', 'Libyan'),
        ('Liechtenstein', 'Liechtenstein'),
        ('Lithuanian', 'Lithuanian'),
        ('Luxembourgish', 'Luxembourgish'),
        ('Malagasy', 'Malagasy'),
        ('Malawian', 'Malawian'),
        ('Malaysian', 'Malaysian'),
        ('Maldivian', 'Maldivian'),
        ('Malian', 'Malian'),
        ('Maltese', 'Maltese'),
        ('Marshallese', 'Marshallese'),
        ('Mauritanian', 'Mauritanian'),
        ('Mauritian', 'Mauritian'),
        ('Mexican', 'Mexican'),
        ('Micronesian', 'Micronesian'),
        ('Moldovan', 'Moldovan'),
        ('Monégasque', 'Monégasque'),
        ('Mongolian', 'Mongolian'),
        ('Montenegrin', 'Montenegrin'),
        ('Moroccan', 'Moroccan'),
        ('Mozambican', 'Mozambican'),
        ('Burmese', 'Burmese'),
        ('Namibian', 'Namibian'),
        ('Nauruan', 'Nauruan'),
        ('Nepalese', 'Nepalese'),
        ('Dutch', 'Dutch'),
        ('New Zealander', 'New Zealander'),
        ('Nicaraguan', 'Nicaraguan'),
        ('Nigerien', 'Nigerien'),
        ('Nigerian', 'Nigerian'),
        ('North Korean', 'North Korean'),
        ('Norwegian', 'Norwegian'),
        ('Omani', 'Omani'),
        ('Pakistani', 'Pakistani'),
        ('Palauan', 'Palauan'),
        ('Panamanian', 'Panamanian'),
        ('Papua New Guinean', 'Papua New Guinean'),
        ('Paraguayan', 'Paraguayan'),
        ('Peruvian', 'Peruvian'),
        ('Filipino', 'Filipino'),
        ('Polish', 'Polish'),
        ('Portuguese', 'Portuguese'),
        ('Qatari', 'Qatari'),
        ('Romanian', 'Romanian'),
        ('Russian', 'Russian'),
        ('Rwandan', 'Rwandan'),
        ('Saint Kitts and Nevis', 'Saint Kitts and Nevis'),
        ('Saint Lucian', 'Saint Lucian'),
        ('Saint Vincentian', 'Saint Vincentian'),
        ('Samoan', 'Samoan'),
        ('Sanmarinese', 'Sanmarinese'),
        ('Sao Tomean', 'Sao Tomean'),
        ('Saudi', 'Saudi'),
        ('Senegalese', 'Senegalese'),
        ('Serbian', 'Serbian'),
        ('Seychellois', 'Seychellois'),
        ('Sierra Leonean', 'Sierra Leonean'),
        ('Singaporean', 'Singaporean'),
        ('Slovak', 'Slovak'),
        ('Slovenian', 'Slovenian'),
        ('Solomon Islander', 'Solomon Islander'),
        ('Somali', 'Somali'),
        ('South African', 'South African'),
        ('South Korean', 'South Korean'),
        ('South Sudanese', 'South Sudanese'),
        ('Spanish', 'Spanish'),
        ('Sri Lankan', 'Sri Lankan'),
        ('Sudanese', 'Sudanese'),
        ('Surinamese', 'Surinamese'),
        ('Swazi', 'Swazi'),
        ('Swedish', 'Swedish'),
        ('Swiss', 'Swiss'),
        ('Syrian', 'Syrian'),
        ('Taiwanese', 'Taiwanese'),
        ('Tajikistani', 'Tajikistani'),
        ('Tanzanian', 'Tanzanian'),
        ('Thai', 'Thai'),
        ('Timorese', 'Timorese'),
        ('Togolese', 'Togolese'),
        ('Tongan', 'Tongan'),
        ('Trinidadian or Tobagonian', 'Trinidadian or Tobagonian'),
        ('Tunisian', 'Tunisian'),
        ('Turkish', 'Turkish'),
        ('Turkmen', 'Turkmen'),
        ('Tuvaluan', 'Tuvaluan'),
        ('Ugandan', 'Ugandan'),
        ('Ukrainian', 'Ukrainian'),
        ('Emirati', 'Emirati'),
        ('British', 'British'),
        ('American', 'American'),
        ('Uruguayan', 'Uruguayan'),
        ('Uzbekistani', 'Uzbekistani'),
        ('Ni-Vanuatu', 'Ni-Vanuatu'),
        ('Venezuelan', 'Venezuelan'),
        ('Vietnamese', 'Vietnamese'),
        ('Yemeni', 'Yemeni'),
        ('Zambian', 'Zambian'),
        ('Zimbabwean', 'Zimbabwean'),
    ]

    user = models.OneToOneField(Buyer, on_delete=models.CASCADE)
    profile_picture = models.URLField(max_length=1000, blank=True, null=True)
    store_name = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100, choices=NATIONALITY_CHOICES)




    def __str__(self):
        return self.user.username

class SellerProfile(models.Model):
    user = models.OneToOneField(Seller, on_delete=models.CASCADE)
    profile_picture = models.URLField(max_length=1000, blank=True, null=True)
    store_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    SUBDISTRICT_CHOICES = [
        ('Denpasar Selatan', 'Denpasar Selatan'),
        ('Denpasar Timur', 'Denpasar Timur'),
        ('Denpasar Barat', 'Denpasar Barat'),
        ('Denpasar Utara', 'Denpasar Utara'),
    ]

    VILLAGE_CHOICES = [
        # Denpasar Selatan
        ('Panjer', 'Panjer'),
        ('Pedungan', 'Pedungan'),
        ('Renon', 'Renon'),
        ('Sanur', 'Sanur'),
        ('Tukad Manggis', 'Tukad Manggis'),
        ('Tukad Punggawa', 'Tukad Punggawa'),

        # Denpasar Timur
        ('Dangin Puri', 'Dangin Puri'),
        ('Kesiman', 'Kesiman'),
        ('Penatih', 'Penatih'),
        ('Sumerta', 'Sumerta'),

        # Denpasar Barat
        ('Dauh Puri', 'Dauh Puri'),
        ('Padang Sambian', 'Padang Sambian'),
        ('Pemecutan', 'Pemecutan'),

        # Denpasar Utara
        ('Peguyangan', 'Peguyangan'),
        ('Tonja', 'Tonja'),
        ('Ubung', 'Ubung'),
    ]


    subdistrict = models.CharField(max_length=100, choices=SUBDISTRICT_CHOICES)
    village = models.CharField(max_length=100, choices=VILLAGE_CHOICES)
    address = models.CharField(max_length=255)
    maps = models.URLField(max_length=1000)


    def __str__(self):
        return self.user.username

# Sinyal untuk membuat profil setelah buyer dibuat
@receiver(post_save, sender=Buyer)
def create_buyer_profile(sender, instance, created, **kwargs):
    profile_buyer, created = BuyerProfile.objects.get_or_create(user=instance)

    # Mengatur nilai default, jika profile blm dibuat
    if created:
        profile_buyer.profile_picture = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
        profile_buyer.store_name = instance.username
        profile_buyer.nationality = "Not Set"
        profile_buyer.save()

@receiver(post_save, sender=Seller)
def create_seller_profile(sender, instance, created, **kwargs):
    profile_seller, created = SellerProfile.objects.get_or_create(user=instance)

    # Mengatur nilai default nya, jika profile blm dibuat
    if created:
        profile_seller.profile_picture = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
        profile_seller.store_name = instance.username
        profile_seller.city = "Denpasar"
        profile_seller.subdistrict = "Denpasar Selatan"
        profile_seller.village = "Panjer"
        profile_seller.address = "Not Set"
        profile_seller.maps = "https://www.google.com/maps"
        profile_seller.save()