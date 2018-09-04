from rest_framework import serializers


class NeuralInputSerializer(serializers.Serializer):
    name = serializers.CharField()
    path_list = serializers.ListField(
        child=serializers.CharField())
    extra = serializers.DictField(
        child=serializers.CharField())