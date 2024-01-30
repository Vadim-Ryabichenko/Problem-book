from rest_framework import serializers
from .models import TaskCard
from django.contrib.auth.models import User



class TaskCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCard
        fields = ('id', 'text', 'status', 'creator', 'executor', 'create_at')

    def create(self, validated_data):
        return TaskCard.objects.create(text=validated_data['text'], creator=self.context['request'].user)

    def update(self, instance, validated_data):
        if 'text' in validated_data:
            if self.context['request'].user.is_superuser or self.context['request'].user == instance.creator:
                instance.text = validated_data['text']
            else: raise serializers.ValidationError("Ne baluisya")
        if 'status' in validated_data:
            if self.context['request'].user == instance.executor:
                allowed_transitions = {
            'New': ['In progress'],
            'In progress': ['In QA', 'New'],
            'In QA': ['Ready', 'In progress'],
            'Ready': ['In QA']
        }
            elif self.context['request'].user.is_superuser:
                allowed_transitions = {
            'Ready': ['Done'],
            'Done': ['Ready']
        }
            else: raise serializers.ValidationError("Ne baluisya")
            current_status = instance.status
            new_status = validated_data['status']
            if current_status in allowed_transitions:
                if new_status in allowed_transitions[current_status]:
                    instance.status = new_status
                else:
                    raise serializers.ValidationError("There is no such option to switch between statuses")
        if 'executor' in validated_data:
            if self.context['request'].user == instance.creator:
                if validated_data['executor'] == self.context['request'].user:
                    instance.executor = validated_data['executor']
            elif self.context['request'].user.is_superuser:
                instance.executor = User.objects.get(id=validated_data['executor'].id)
            else:
                if not self.context['request'].user.is_superuser:
                    raise serializers.ValidationError("You cannot assign another user as an executor")
                else:
                    instance.executor = validated_data['executor']
        instance.save()
        return instance
    

class TaskCardSerializerForFilter(serializers.ModelSerializer):
    class Meta:
        model = TaskCard
        fields = ('id', 'creator', 'executor', 'update_at')