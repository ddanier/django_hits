from .models import Hit, HitHistory

def create_hit_history(hit):
    try:
        last_history = hit.history.order_by('-when', '-pk')[0]
    except IndexError:
        last_history = HitHistory(hit=hit)  # empty history, not stored (only used for calculation below)
    history = HitHistory(
        hit=hit,

        views=hit.views,
        visits=hit.visits,

        views_change=hit.views - last_history.views,
        visits_change=hit.visits - last_history.visits,
    )
    history.save()
    return history
