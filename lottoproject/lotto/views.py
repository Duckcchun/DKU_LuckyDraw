from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .models import LottoRound, LottoTicket, DrawResult
from .forms import SignUpForm, ManualNumberForm


def is_admin(user):
    return user.is_staff or user.is_superuser


def user_logout(request):
    logout(request)
    return redirect('home')


def home(request):
    current_round = LottoRound.get_current_round()
    recent_results = DrawResult.objects.select_related('lotto_round').all()[:5]

    context = {
        'current_round': current_round,
        'recent_results': recent_results,
    }
    return render(request, 'lotto/home.html', context)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'{user.username}님, 회원가입이 완료되었습니다!')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def purchase_auto(request):
    current_round = LottoRound.get_current_round()

    if request.method == 'POST':
        # 구매 수량 (1~5장)
        quantity = int(request.POST.get('quantity', 1))
        quantity = max(1, min(5, quantity))

        tickets = []
        for _ in range(quantity):
            numbers = LottoTicket.generate_auto_numbers()
            ticket = LottoTicket.objects.create(
                user=request.user,
                lotto_round=current_round,
                number_1=numbers[0],
                number_2=numbers[1],
                number_3=numbers[2],
                number_4=numbers[3],
                number_5=numbers[4],
                number_6=numbers[5],
                purchase_type='auto',
            )
            tickets.append(ticket)

        messages.success(request, f'자동번호 {quantity}장을 구매했습니다!')
        return render(request, 'lotto/purchase_result.html', {
            'tickets': tickets,
            'current_round': current_round,
        })

    return render(request, 'lotto/purchase_auto.html', {
        'current_round': current_round,
    })


@login_required
def purchase_manual(request):
    current_round = LottoRound.get_current_round()

    if request.method == 'POST':
        form = ManualNumberForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            numbers = sorted([data[f'number_{i}'] for i in range(1, 7)])
            ticket = LottoTicket.objects.create(
                user=request.user,
                lotto_round=current_round,
                number_1=numbers[0],
                number_2=numbers[1],
                number_3=numbers[2],
                number_4=numbers[3],
                number_5=numbers[4],
                number_6=numbers[5],
                purchase_type='manual',
            )
            messages.success(request, '수동번호 1장을 구매했습니다!')
            return render(request, 'lotto/purchase_result.html', {
                'tickets': [ticket],
                'current_round': current_round,
            })
    else:
        form = ManualNumberForm()

    return render(request, 'lotto/purchase_manual.html', {
        'form': form,
        'current_round': current_round,
    })


@login_required
def my_tickets(request):
    tickets = LottoTicket.objects.filter(user=request.user).select_related('lotto_round')
    return render(request, 'lotto/my_tickets.html', {'tickets': tickets})


@login_required
def check_results(request):
    # 추첨 완료된 회차의 티켓만 조회
    tickets = LottoTicket.objects.filter(
        user=request.user,
        lotto_round__is_active=False
    ).select_related('lotto_round').order_by('-purchased_at')

    winning_tickets = tickets.filter(prize_rank__gt=0, prize_rank__lte=5)
    losing_tickets = tickets.filter(prize_rank=0)

    context = {
        'winning_tickets': winning_tickets,
        'losing_tickets': losing_tickets,
        'total_tickets': tickets.count(),
    }
    return render(request, 'lotto/check_results.html', context)


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    current_round = LottoRound.get_current_round()
    total_tickets = LottoTicket.objects.filter(lotto_round=current_round).count()
    total_rounds = LottoRound.objects.count()
    total_users = LottoTicket.objects.values('user').distinct().count()

    context = {
        'current_round': current_round,
        'total_tickets': total_tickets,
        'total_rounds': total_rounds,
        'total_users': total_users,
    }
    return render(request, 'lotto/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_sales(request):
    round_filter = request.GET.get('round', None)

    if round_filter:
        tickets = LottoTicket.objects.filter(
            lotto_round__round_number=round_filter
        ).select_related('user', 'lotto_round')
    else:
        tickets = LottoTicket.objects.all().select_related('user', 'lotto_round')

    rounds = LottoRound.objects.all()

    # 통계
    stats = {
        'total_count': tickets.count(),
        'auto_count': tickets.filter(purchase_type='auto').count(),
        'manual_count': tickets.filter(purchase_type='manual').count(),
    }

    context = {
        'tickets': tickets[:100],  # 최근 100건
        'rounds': rounds,
        'selected_round': round_filter,
        'stats': stats,
    }
    return render(request, 'lotto/admin_sales.html', context)


@login_required
@user_passes_test(is_admin)
def admin_draw(request):
    current_round = LottoRound.get_current_round()
    ticket_count = LottoTicket.objects.filter(lotto_round=current_round).count()

    if request.method == 'POST':
        if ticket_count == 0:
            messages.warning(request, '판매된 티켓이 없어 추첨할 수 없습니다.')
            return redirect('admin_draw')

        # 추첨 실행
        draw_result = DrawResult.perform_draw(current_round)

        messages.success(request, f'제 {current_round.round_number}회 추첨이 완료되었습니다!')
        return redirect('admin_draw_result', round_number=current_round.round_number)

    context = {
        'current_round': current_round,
        'ticket_count': ticket_count,
    }
    return render(request, 'lotto/admin_draw.html', context)


@login_required
@user_passes_test(is_admin)
def admin_draw_result(request, round_number):
    lotto_round = get_object_or_404(LottoRound, round_number=round_number)
    draw_result = get_object_or_404(DrawResult, lotto_round=lotto_round)

    # 등수별 당첨자 수
    prize_stats = {}
    for rank in range(1, 6):
        prize_stats[rank] = LottoTicket.objects.filter(
            lotto_round=lotto_round, prize_rank=rank
        ).count()

    winning_tickets = LottoTicket.objects.filter(
        lotto_round=lotto_round, prize_rank__gte=1, prize_rank__lte=5
    ).select_related('user')

    context = {
        'lotto_round': lotto_round,
        'draw_result': draw_result,
        'prize_stats': prize_stats,
        'winning_tickets': winning_tickets,
    }
    return render(request, 'lotto/admin_draw_result.html', context)


@login_required
@user_passes_test(is_admin)
def admin_winners(request):
    results = DrawResult.objects.select_related('lotto_round').all()

    winners_by_round = []
    for result in results:
        tickets = LottoTicket.objects.filter(
            lotto_round=result.lotto_round,
            prize_rank__gte=1,
            prize_rank__lte=5
        ).select_related('user')

        winners_by_round.append({
            'result': result,
            'winners': tickets,
            'winner_count': tickets.count(),
        })

    context = {
        'winners_by_round': winners_by_round,
    }
    return render(request, 'lotto/admin_winners.html', context)
