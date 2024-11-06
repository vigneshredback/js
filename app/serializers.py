from rest_framework import serializers
from app.models import Like,Biodata

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'biodata']

class BiodataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biodata
        fields = ['id', 'gender', 'degree', 'profession', 'age', 'height', 'image1', 'user']

    # If the `user` model contains the name field
    user = serializers.CharField(source='user.name', read_only=True)
    image1 = serializers.ImageField(required=False)