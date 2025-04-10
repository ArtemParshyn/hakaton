from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiUser
        fields = ['id', 'username', 'email', 'can_publish', 'is_admin', 'telegram_chat_id']
        read_only_fields = ['can_publish', 'is_admin']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class UserNewSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNewSubscription
        fields = '__all__'


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'


class NewsItemSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    sources = SourceSerializer(many=True, read_only=True)

    class Meta:
        model = NewsItem
        fields = '__all__'
        read_only_fields = ['created_at', 'author']


class NewsSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField(read_only=True)
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = NewsItem
        fields = [
            'id',
            'title',
            'content',
            'created_at',
            'status',
            'status_display',
            'is_organization_news',
            'cover',
            'author',
            'tags',
            'sources'
        ]
        read_only_fields = ['id']

    def get_status_display(self, obj):
        return obj.get_status_display()

    def validate_author(self, value):
        if self.context['request'].method in ['POST', 'PUT', 'PATCH']:
            return self.context['request'].user
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])

        news_item = NewsItem.objects.create(**validated_data)

        self._process_tags(news_item, tags)

        return news_item

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)

        instance = super().update(instance, validated_data)

        if tags is not None:
            instance.tags.clear()
            self._process_tags(instance, tags)

        return instance

    def _process_tags(self, news_item, tags):
        """Обработка тегов с bulk-операциями"""
        existing_tags = Tag.objects.filter(name__in=[tag.name for tag in tags])
        new_tags = [tag for tag in tags if tag not in existing_tags]

        if new_tags:
            Tag.objects.bulk_create(new_tags)

        news_item.tags.add(*existing_tags, *new_tags)


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    class Meta:
        model = ApiUser
        fields = ('username', 'password')

    def validate_username(self, value):
        if get_user_model().objects.filter(username=value).exists():
            raise serializers.ValidationError("Имя пользователя занято")
        return value

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
