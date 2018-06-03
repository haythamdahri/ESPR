from rest_framework import serializers

from ELearning.models import Exam, Question


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id','name']

class QuestionSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['question','option1','option2','option3','option4','answer','exam']