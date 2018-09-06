from rest_framework import serializers


class NeuralInputSerializer(serializers.Serializer):
    name = serializers.CharField()
    path_list = serializers.ListField(
        child=serializers.CharField())
    extra = serializers.DictField(
        child=serializers.CharField())

    def validate_path_list(self, value):
        if not value:
            raise serializers.ValidationError('Path list is empty')
        return value