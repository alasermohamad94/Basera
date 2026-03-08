from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Quiz, QuizAttempt, Question, Answer, Choice
from .serializers import QuizSerializer, QuizDetailSerializer, QuizAttemptSerializer, AnswerSerializer


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['lesson']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return QuizDetailSerializer
        return QuizSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def start_attempt(self, request, pk=None):
        """بدء محاولة جديدة للاختبار"""
        quiz = self.get_object()
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz
        )
        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit_answer(self, request, pk=None):
        """تقديم إجابة على سؤال"""
        quiz = self.get_object()
        attempt_id = request.data.get('attempt_id')
        question_id = request.data.get('question_id')
        
        try:
            attempt = QuizAttempt.objects.get(id=attempt_id, user=request.user, quiz=quiz)
            question = Question.objects.get(id=question_id, quiz=quiz)
        except (QuizAttempt.DoesNotExist, Question.DoesNotExist):
            return Response({'error': 'المحاولة أو السؤال غير موجود'}, 
                          status=status.HTTP_404_NOT_FOUND)

        # البحث عن إجابة موجودة أو إنشاء جديدة
        answer, created = Answer.objects.get_or_create(
            attempt=attempt,
            question=question
        )

        # معالجة الإجابة حسب نوع السؤال
        if question.question_type == 'multiple_choice':
            choice_id = request.data.get('choice_id')
            if choice_id:
                try:
                    choice = Choice.objects.get(id=choice_id, question=question)
                    answer.selected_choice = choice
                    answer.is_correct = choice.is_correct
                    answer.points_earned = question.points if choice.is_correct else 0
                except Choice.DoesNotExist:
                    return Response({'error': 'الخيار غير موجود'}, 
                                  status=status.HTTP_400_BAD_REQUEST)

        elif question.question_type == 'true_false':
            answer_text = request.data.get('answer_text', '').lower()
            correct_answer = question.choices.filter(is_correct=True).first()
            if correct_answer:
                answer.is_correct = (answer_text == correct_answer.choice_text.lower())
                answer.points_earned = question.points if answer.is_correct else 0
            answer.answer_text = answer_text

        elif question.question_type in ['text_answer', 'audio_answer']:
            answer.answer_text = request.data.get('answer_text', '')
            # للإجابات الصوتية، يجب رفع الملف هنا
            # answer.answer_audio = request.FILES.get('answer_audio')
            # هذه الإجابات تحتاج مراجعة يدوية
            answer.reviewed = False

        answer.save()
        serializer = AnswerSerializer(answer)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit_attempt(self, request, pk=None):
        """إنهاء محاولة الاختبار وحساب النتيجة"""
        quiz = self.get_object()
        attempt_id = request.data.get('attempt_id')
        
        try:
            attempt = QuizAttempt.objects.get(id=attempt_id, user=request.user, quiz=quiz)
        except QuizAttempt.DoesNotExist:
            return Response({'error': 'المحاولة غير موجودة'}, 
                          status=status.HTTP_404_NOT_FOUND)

        # حساب النتيجة
        total_points = sum(answer.points_earned for answer in attempt.answers.all())
        total_possible = sum(q.points for q in quiz.questions.all())
        score_percentage = (total_points / total_possible * 100) if total_possible > 0 else 0

        attempt.score = score_percentage
        attempt.passed = score_percentage >= quiz.passing_score
        attempt.completed_at = timezone.now()
        attempt.save()

        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data)


class QuizAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)

