from rest_framework import serializers
from .models import CustomUser, UserInfo
from datetime import date

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser 
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user
    




class UserInfoSerializer(serializers.ModelSerializer):

    date_of_birth = serializers.DateField(allow_null=True, required=False)
    exam_type = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    education_level = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    profession = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    location = serializers.CharField(allow_null=True, allow_blank=True, required=False)

    class Meta:
        model = UserInfo
        fields = ('info_id', 'date_of_birth', 'exam_type', 'education_level', 'profession', 'location')



    def validate_data(self, validated_data):
    #check if user info is aleady there in user_info table
        if UserInfo.objects.filter(user=self.context['user']).exists():
            raise serializers.ValidationError("User info already exists")
    
    def create(self, validated_data):
        self.validate_data(validated_data)
        #check if user info is aleady there in user_info table
        if UserInfo.objects.filter(user=self.context['user']).exists():
            raise serializers.ValidationError("User info already exists")
        
        user = self.context['user']
        user_info = UserInfo.objects.create(user=user, **validated_data)
        return user_info
    


    def update(self, instance, validated_data):
        self.validate_data(validated_data)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.exam_type = validated_data.get('exam_type', instance.exam_type)
        instance.education_level = validated_data.get('education_level', instance.education_level)
        instance.profession = validated_data.get('profession', instance.profession)
        instance.location = validated_data.get('location', instance.location)
        instance.save()
        return instance


    
    




