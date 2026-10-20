from .models import ContactBlock, MenuItem, SiteSettings


def site(request):
    if request.path.startswith("/admin"):
        return {}

    items = []
    for m in MenuItem.objects.filter(is_active=True):
        url = m.get_url()
        if m.page == "home":
            active = request.path == "/"
        elif m.page == "custom":
            active = request.path == url
        else:
            active = request.path.startswith(url)
        items.append({"title": m.title, "url": url, "active": active, "new_tab": m.new_tab})

    half = (len(items) + 1) // 2
    blocks = list(ContactBlock.objects.all())
    return {
        "menu_left": items[:half],
        "menu_right": items[half:],
        "foot_coop": [b for b in blocks if b.column == "coop" and b.show_in_footer],
        "foot_order": [b for b in blocks if b.column == "order" and b.show_in_footer],
        "site": SiteSettings.load(),
        "menu_items": items,
        "footer_coop": [b for b in blocks if b.column == "coop"],
        "footer_order": [b for b in blocks if b.column == "order"],
    }
