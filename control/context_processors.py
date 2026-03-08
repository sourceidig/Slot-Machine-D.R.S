from .menu import MENU

def sidebar_menu(request):

    if not request.user.is_authenticated:
        return {}

    role = request.user.role
    menu_filtered = []

    for section in MENU:

        items = []

        for item in section["items"]:
            if role in item["roles"]:
                items.append(item)

        if items:
            menu_filtered.append({
                "section": section["section"],
                "items": items
            })

    return {
        "sidebar_menu": menu_filtered
    }