from django.contrib import admin
from .models import LottoRound, LottoTicket, DrawResult


@admin.register(LottoRound)
class LottoRoundAdmin(admin.ModelAdmin):
    list_display = ['round_number', 'is_active', 'created_at', 'draw_date']
    list_filter = ['is_active']


@admin.register(LottoTicket)
class LottoTicketAdmin(admin.ModelAdmin):
    list_display = ['user', 'lotto_round', 'purchase_type', 'get_numbers_display', 'prize_rank', 'purchased_at']
    list_filter = ['purchase_type', 'lotto_round', 'prize_rank']
    search_fields = ['user__username']


@admin.register(DrawResult)
class DrawResultAdmin(admin.ModelAdmin):
    list_display = ['lotto_round', 'get_numbers_display', 'bonus_number', 'drawn_at']
