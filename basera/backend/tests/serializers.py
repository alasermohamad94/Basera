from rest_framework import serializers
from .models import Quiz, Question, Choice, QuizAttempt, Answer


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'is_correct']
        read_only_fields = ['is_correct']  # لا نكشف الإجابة الصحيحة إلا بعد الإجابة


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    question_audio_url = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'question_type', 'question_text', 'question_audio',
                  'question_audio_url', 'order', 'points', 'choices']

    def get_question_audio_url(self, obj):
        if obj.question_audio:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.question_audio.url)
        return None


class QuizSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'lesson', 'lesson_title', 'title', 'description',
                  'passing_score', 'questions_count', 'created_at', 'updated_at']

    def get_questions_count(self, obj):
        return obj.questions.count()


class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'lesson', 'lesson_title', 'title', 'description',
                  'passing_score', 'questions', 'created_at', 'updated_at']


class AnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    answer_audio_url = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ['id', 'attempt', 'question', 'question_text', 'answer_text',
                  'answer_audio', 'answer_audio_url', 'selected_choice',
                  'is_correct', 'points_earned', 'reviewed']

    def get_answer_audio_url(self, obj):
        if obj.answer_audio:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.answer_audio.url)
        return None


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ['id', 'user', 'quiz', 'quiz_title', 'score', 'passed',
                  'started_at', 'completed_at', 'answers']
        read_only_fields = ['user', 'score', 'passed']

