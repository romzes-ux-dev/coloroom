import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"\+\d[\d\s()\-]{8,}\d")


@register.filter
def rich(value):
    """Абзацы по пустой строке, **жирный** текст. Всё остальное экранируется."""
    text = escape(value or "")
    out = []
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para:
            continue
        para = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", para).replace("\n", "<br>")
        out.append(f"<p>{para}</p>")
    return mark_safe("".join(out))


@register.filter
def contact(value):
    """Делает из e-mail и телефонов кликабельные ссылки, строки разделяет <br>."""
    text = escape(value or "")
    text = EMAIL_RE.sub(lambda m: f'<a href="mailto:{m.group(0)}">{m.group(0)}</a>', text)

    def tel(m):
        digits = re.sub(r"[^\d+]", "", m.group(0))
        return f'<a href="tel:{digits}">{m.group(0)}</a>'

    text = PHONE_RE.sub(tel, text)
    return mark_safe(text.replace("\n", "<br>"))


@register.filter
def team_lines(value):
    """«Должность: Имя» -> жирная должность и имя, по строке на человека."""
    out = []
    for line in (value or "").splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            role, name = line.split(":", 1)
            out.append(f'<span class="pj-role">{escape(role.strip())}:</span> {escape(name.strip())}')
        else:
            out.append(escape(line))
    return mark_safe("<br>".join(out))
