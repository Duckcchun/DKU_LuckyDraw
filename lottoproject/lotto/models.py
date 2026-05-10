"""
6/45 Lotto 데이터 모델
- LottoRound: 로또 회차 정보
- LottoTicket: 구매한 로또 티켓
- DrawResult: 추첨 결과
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import random


class LottoRound(models.Model):
    """로또 회차 모델"""
    round_number = models.PositiveIntegerField(unique=True, verbose_name='회차')
    is_active = models.BooleanField(default=True, verbose_name='판매중')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    draw_date = models.DateTimeField(null=True, blank=True, verbose_name='추첨일')

    class Meta:
        ordering = ['-round_number']
        verbose_name = '로또 회차'
        verbose_name_plural = '로또 회차'

    def __str__(self):
        status = "판매중" if self.is_active else "추첨완료"
        return f"제 {self.round_number}회 ({status})"

    @classmethod
    def get_current_round(cls):
        """현재 판매중인 회차를 반환하거나 새 회차를 생성"""
        active_round = cls.objects.filter(is_active=True).first()
        if not active_round:
            last_round = cls.objects.first()
            next_number = (last_round.round_number + 1) if last_round else 1
            active_round = cls.objects.create(round_number=next_number)
        return active_round


class LottoTicket(models.Model):
    """로또 티켓 모델 - 사용자가 구매한 번호"""
    PURCHASE_TYPE_CHOICES = [
        ('manual', '수동'),
        ('auto', '자동'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets', verbose_name='구매자')
    lotto_round = models.ForeignKey(LottoRound, on_delete=models.CASCADE, related_name='tickets', verbose_name='회차')
    number_1 = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(45)])
    number_2 = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(45)])
    number_3 = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(45)])
    number_4 = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(45)])
    number_5 = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(45)])
    number_6 = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(45)])
    purchase_type = models.CharField(max_length=10, choices=PURCHASE_TYPE_CHOICES, verbose_name='구매유형')
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name='구매일시')
    prize_rank = models.PositiveIntegerField(null=True, blank=True, verbose_name='당첨등수')

    class Meta:
        ordering = ['-purchased_at']
        verbose_name = '로또 티켓'
        verbose_name_plural = '로또 티켓'

    def __str__(self):
        numbers = self.get_numbers()
        return f"{self.user.username} - {self.lotto_round} - {numbers}"

    def get_numbers(self):
        """티켓의 번호를 정렬된 리스트로 반환"""
        return sorted([self.number_1, self.number_2, self.number_3,
                       self.number_4, self.number_5, self.number_6])

    def get_numbers_display(self):
        """표시용 번호 문자열"""
        return ', '.join(map(str, self.get_numbers()))

    @classmethod
    def generate_auto_numbers(cls):
        """자동번호 6개 생성 (1~45 중 중복 없이)"""
        return sorted(random.sample(range(1, 46), 6))

    def check_prize(self, draw_result):
        """당첨 확인"""
        my_numbers = set(self.get_numbers())
        winning_numbers = set(draw_result.get_numbers())
        bonus_number = draw_result.bonus_number

        matched = my_numbers & winning_numbers
        match_count = len(matched)

        if match_count == 6:
            self.prize_rank = 1  # 1등: 6개 일치
        elif match_count == 5 and bonus_number in my_numbers:
            self.prize_rank = 2  # 2등: 5개 + 보너스
        elif match_count == 5:
            self.prize_rank = 3  # 3등: 5개 일치
        elif match_count == 4:
            self.prize_rank = 4  # 4등: 4개 일치
        elif match_count == 3:
            self.prize_rank = 5  # 5등: 3개 일치
        else:
            self.prize_rank = 0  # 낙첨

        self.save()
        return self.prize_rank


class DrawResult(models.Model):
    """추첨 결과 모델"""
    lotto_round = models.OneToOneField(LottoRound, on_delete=models.CASCADE, related_name='draw_result', verbose_name='회차')
    number_1 = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(45)])
    number_2 = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(45)])
    number_3 = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(45)])
    number_4 = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(45)])
    number_5 = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(45)])
    number_6 = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(45)])
    bonus_number = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(45)], verbose_name='보너스번호')
    drawn_at = models.DateTimeField(auto_now_add=True, verbose_name='추첨일시')

    class Meta:
        ordering = ['-drawn_at']
        verbose_name = '추첨 결과'
        verbose_name_plural = '추첨 결과'

    def __str__(self):
        numbers = self.get_numbers()
        return f"{self.lotto_round} - {numbers} + 보너스: {self.bonus_number}"

    def get_numbers(self):
        """당첨 번호를 정렬된 리스트로 반환"""
        return sorted([self.number_1, self.number_2, self.number_3,
                       self.number_4, self.number_5, self.number_6])

    def get_numbers_display(self):
        """표시용 당첨 번호 문자열"""
        return ', '.join(map(str, self.get_numbers()))

    @classmethod
    def perform_draw(cls, lotto_round):
        """추첨 실행 - 7개 번호 생성 (6개 당첨번호 + 1개 보너스번호)"""
        all_numbers = random.sample(range(1, 46), 7)
        winning_numbers = sorted(all_numbers[:6])
        bonus_number = all_numbers[6]

        draw_result = cls.objects.create(
            lotto_round=lotto_round,
            number_1=winning_numbers[0],
            number_2=winning_numbers[1],
            number_3=winning_numbers[2],
            number_4=winning_numbers[3],
            number_5=winning_numbers[4],
            number_6=winning_numbers[5],
            bonus_number=bonus_number,
        )

        # 해당 회차 판매 종료
        lotto_round.is_active = False
        lotto_round.save()

        # 모든 티켓의 당첨 확인
        tickets = LottoTicket.objects.filter(lotto_round=lotto_round)
        for ticket in tickets:
            ticket.check_prize(draw_result)

        return draw_result
