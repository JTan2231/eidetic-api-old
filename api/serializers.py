from rest_framework import serializers
from .models import Entry, User, EntryLink, Embedding, Cluster, ClusterLink, Follow

class BinaryField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, value):
        return value

class EntrySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    content = serializers.CharField()
    title = serializers.CharField()

    timestamp = serializers.DateTimeField()

    def create(self, validated_data):
        return Entry.objects.create(
            user=validated_data.get('user'),
            content=validated_data.get('content'),
            timestamp=validated_data.get('timestamp'),
            title=validated_data.get('title'),
        )

    def update(self, instance, validated_data):
        instance.user = validated_data.get('user', instance.user_id)
        instance.raw_html = validated_data.get('content', instance.content)
        instance.timestamp = validated_data.get('timestamp', instance.timestamp)
        instance.title = validated_data.get('title', instance.title)

        instance.save()

        return instance

    class Meta:
        model = Entry
        fields = ('entry_id', 'user', 'content', 'timestamp', 'title',)

class EmbeddingSerializer(serializers.ModelSerializer):
    token_index = serializers.IntegerField()
    embedding = BinaryField()
    mask = BinaryField()

    def create(self, validated_data):
        return Entry.objects.create(
            token_index=validated_data.get('token_index'),
            embedding=validated_data.get('embedding'),
            mask=validated_data.get('mask'),
        )

    def update(self, instance, validated_data):
        instance.token_index = validated_data.get('token_index')
        instance.embedding = validated_data.get('embedding', instance.embedding)
        instance.mask = validated_data.get('mask', instance.mask)

        instance.save()

        return instance

    class Meta:
        model = Embedding
        fields = ('embedding_id', 'token_index', 'embedding', 'mask',)

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=256)

    def create(self, validated_data):
        return User.objects.create(
            username=validated_data.get('username'),
            password=validated_data.get('password')
        )

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)

        instance.save()

        return instance

    class Meta:
        model = User
        fields = ('user_id', 'username', 'password')

class EntryLinkSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    centroid = serializers.PrimaryKeyRelatedField(queryset=Entry.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Entry.objects.all())

    def create(self, validated_data):
        return EntryLink.objects.create(
            user=validated_data.get('user'),
            centroid=validated_data.get('centroid'),
            branch=validated_data.get('branch'),
        )

    class Meta:
        model = EntryLink
        fields = ('entry_link_id', 'user', 'centroid', 'branch')

class ClusterSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    title = serializers.CharField()

    def create(self, validated_data):
        return Cluster.objects.create(
            user=validated_data.get('user'),
            title=validated_data.get('title'),
        )

    class Meta:
        model = Cluster
        fields = ('cluster_id', 'user', 'title')

class ClusterLinkSerializer(serializers.ModelSerializer):
    cluster = serializers.PrimaryKeyRelatedField(queryset=Cluster.objects.all())
    entry = serializers.PrimaryKeyRelatedField(queryset=Entry.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def create(self, validated_data):
        return ClusterLink.objects.create(
            cluster=validated_data.get('cluster'),
            entry=validated_data.get('entry'),
            user=validated_data.get('user'),
        )

    class Meta:
        model = ClusterLink
        fields = ('cluster_link_id', 'cluster', 'entry', 'user')

class Follow(serializers.ModelSerializer):
    follower = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    followee = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def create(self, validated_data):
        return Follow.objects.create(
            follower=validated_data.get('follower'),
            followee=validated_data.get('followee'),
        )

    class Meta:
        model = Follow
        fields = ('follow_id', 'follower', 'followee')
