from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class SingletonModel(models.Model):
    """Модель с единственной записью (настройки, страница «О нас»)."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SiteSettings(SingletonModel):
    site_name = models.CharField("Название студии", max_length=120, default="Coloroom Interiors")
    meta_description = models.CharField(
        "Описание для поисковиков", max_length=300, blank=True,
        default="Coloroom Interiors — студия архитектуры и дизайна интерьеров в Ташкенте.",
    )
    logo = models.ImageField("Логотип (необязательно)", upload_to="site/", blank=True,
                             help_text="Если не загружен, показывается стандартный знак с названием.")

    service_banner = models.ImageField("Баннер страниц «Контакты» и 404", upload_to="site/", blank=True,
                                       help_text="Широкое фото сверху, пропорции около 7 : 1.")
    hero_image = models.ImageField("Баннер на главной", upload_to="site/", blank=True,
                                   help_text="Широкое фото, лучше от 2400 px по ширине.")

    about_title = models.CharField("Заголовок блока «О нас»", max_length=60, default="О нас")
    about_button = models.CharField("Текст кнопки «О нас»", max_length=40, default="Подробнее")
    about_short = models.TextField(
        "Текст блока «О нас» на главной",
        default=(
            "Добро пожаловать в **Coloroom Interiors**. Мы — команда архитекторов, дизайнеров и "
            "инженеров, объединенных общей страстью к созданию эстетичных, умных и современных "
            "пространств. Наша студия реализует проекты полного цикла: от разработки "
            "архитектурной концепции с нуля до продумывания мельчайших деталей интерьера и "
            "экстерьера."
        ),
        help_text="Пустая строка — новый абзац. **Текст** — жирным.",
    )
    about_note = models.TextField(
        "Короткий текст справа от заголовка «О нас»",
        default=("Для нас каждый проект — это не просто чертежи и визуализации, это отражение вашего "
                 "характера, образа жизни или философии вашего бизнеса."),
    )
    about_image_small = models.ImageField("Малое фото блока «О нас» (справа от текста)", upload_to="site/", blank=True)
    about_image = models.ImageField("Большое фото блока «О нас»", upload_to="site/", blank=True)

    projects_title = models.CharField("Заголовок блока «Проекты»", max_length=60, default="Проекты")
    projects_button = models.CharField("Текст кнопки «Проекты»", max_length=40, default="Все проекты")
    projects_note = models.TextField(
        "Короткий текст справа от заголовка «Проекты»",
        default=("Для нас каждый проект — это не просто чертежи и визуализации, это отражение вашего "
                 "характера, образа жизни или философии вашего бизнеса."),
    )
    projects_middle_text = models.TextField(
        "Текст под проектами (слева от кнопки «Все проекты»)",
        default=("Мы создаем не просто интерьеры, а живую архитектуру ощущений. От частных резиденций до "
                 "коммерческих пространств — здесь собраны проекты, в которых каждая текстура и деталь "
                 "работают на создание единого характера."),
    )

    footer_left_title = models.CharField("Заголовок блока «Сотрудничество» (страница «Контакты»)", max_length=60, default="Сотрудничество")
    footer_right_title = models.CharField("Заголовок подвала", max_length=60, default="Заказать проект")
    footer_bg = models.ImageField("Фото подвала (затемняется)", upload_to="site/", blank=True)
    copyright_text = models.TextField("Текст в самом низу сайта", default="© 2018. Coloroom Interiors")

    class Meta:
        verbose_name = "Главная страница и подвал"
        verbose_name_plural = "Главная страница и подвал"

    def __str__(self):
        return "Основные настройки сайта"


class AboutPage(SingletonModel):
    title = models.CharField("Название страницы (вкладка браузера)", max_length=60, default="О нас")
    banner = models.ImageField("Баннер сверху", upload_to="site/", blank=True,
                               help_text="Очень широкое фото, пропорции около 4,3 : 1.")
    lead = models.CharField("Крупный заголовок вступления (необязательно)", max_length=300, blank=True, default="")
    body = models.TextField(
        "Текст вступления", blank=True,
        default=(
            "Добро пожаловать в студию дизайна **Coloroom Interiors**. Мы — команда архитекторов, дизайнеров и "
            "инженеров, объединенных общей страстью к созданию эстетичных, умных и современных пространств. "
            "Наша студия реализует проекты полного цикла: от разработки архитектурной концепции с нуля до "
            "продумывания мельчайших деталей интерьера и экстерьера.\n\n"
            "Для нас каждый проект — это не просто чертежи и визуализации, это отражение вашего характера, "
            "образа жизни или философии вашего бизнеса."
        ),
        help_text="Пустая строка — новый абзац. **Текст** — жирным.",
    )
    image = models.ImageField("Большое фото под вступлением", upload_to="site/", blank=True)
    statement = models.TextField("Крупная фраза под фото (необязательно)", blank=True, default="")
    philosophy_title = models.CharField("Заголовок «Философия»", max_length=60, default="Философия")
    philosophy_text = models.TextField("Текст «Философия»", blank=True, default=(
        "Мы отдаем предпочтение передовым направлениям в архитектуре и дизайне. Осознавая, что для многих заказчиков смелые новаторские решения и современные тренды становятся принципиально новым опытом, мы берем на себя роль надежного проводника. Мы выстраиваем работу так, чтобы путь от первой идеи до финальной реализации был для вас прозрачным, комфортным и по-настоящему увлекательным."
    ))
    philosophy_image = models.ImageField("Фото «Философия»", upload_to="site/", blank=True)
    team_title = models.CharField("Заголовок «Команда»", max_length=60, default="Команда")
    team_text = models.TextField("Текст «Команда»", blank=True, default=(
        "Мы отдаем предпочтение передовым направлениям в архитектуре и дизайне. Осознавая, что для многих заказчиков смелые новаторские решения и современные тренды становятся принципиально новым опытом, мы берем на себя роль надежного проводника. Мы выстраиваем работу так, чтобы путь от первой идеи до финальной реализации был для вас прозрачным, комфортным и по-настоящему увлекательным."
    ))
    team_image = models.ImageField("Фото «Команда»", upload_to="site/", blank=True)

    class Meta:
        verbose_name = "Страница «О нас»"
        verbose_name_plural = "Страница «О нас»"

    def __str__(self):
        return "Страница «О нас»"


class ProjectsPage(SingletonModel):
    title = models.CharField("Название страницы (вкладка браузера)", max_length=60, default="Проекты")
    banner = models.ImageField("Баннер сверху", upload_to="site/", blank=True,
                               help_text="Очень широкое фото, пропорции около 5,4 : 1.")
    intro = models.TextField(
        "Текст под баннером",
        default=("Реализованные пространства и архитектурные концепции, где форма следует за смыслом. "
                 "Каждое решение отражает баланс эстетики, света и функциональности."),
    )
    load_more_label = models.CharField("Текст кнопки «Загрузить ещё»", max_length=40, default="Загрузить ещё")

    class Meta:
        verbose_name = "Страница «Проекты»"
        verbose_name_plural = "Страница «Проекты»"

    def __str__(self):
        return "Страница «Проекты»"


class MenuItem(models.Model):
    PAGES = [
        ("home", "Главная"),
        ("about", "О нас"),
        ("projects", "Проекты"),
        ("contacts", "Контакты"),
        ("custom", "Своя ссылка"),
    ]
    title = models.CharField("Название в меню", max_length=40)
    page = models.CharField("Куда ведёт", max_length=20, choices=PAGES, default="home")
    custom_url = models.CharField("Своя ссылка", max_length=300, blank=True,
                                  help_text="Заполняется, только если выбрано «Своя ссылка».")
    new_tab = models.BooleanField("Открывать в новой вкладке", default=False)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Пункт меню"
        verbose_name_plural = "Меню сайта"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    def get_url(self):
        if self.page == "custom":
            return self.custom_url or "#"
        return reverse(self.page)


class Category(models.Model):
    name = models.CharField("Название", max_length=40)
    slug = models.SlugField("Код для адреса", unique=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Категория проекта"
        verbose_name_plural = "Категории проектов"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField("Название (1-я строка, жирная)", max_length=80)
    subtitle = models.CharField("Тип (2-я строка)", max_length=80, blank=True,
                                help_text="Например: House, Apartment, Restaurant.")
    slug = models.SlugField("Адрес страницы", unique=True)
    cover = models.ImageField("Обложка (карточка в списках)", upload_to="projects/")
    short_description = models.CharField("Короткое описание (для поисковиков)", max_length=240, blank=True)

    banner = models.ImageField("Баннер на странице проекта", upload_to="projects/", blank=True,
                               help_text="Очень широкое фото сверху, пропорции около 5,4 : 1. Если не загружен, берётся обложка.")
    plan_image = models.ImageField("Планировка (чертёж справа от названия)", upload_to="projects/", blank=True)
    project_type = models.CharField("Проект", max_length=120, blank=True, help_text="Например: Дизайн интерьера жилого помещения.")
    location = models.CharField("Локация", max_length=80, blank=True)
    status = models.CharField("Статус", max_length=60, blank=True, help_text="Например: Завершён.")
    year = models.PositiveSmallIntegerField("Год", null=True, blank=True)
    plot_area = models.CharField("Площадь участка", max_length=40, blank=True, help_text="Например: 600 кв.м.")
    area = models.CharField("Площадь помещения", max_length=40, blank=True, help_text="Например: 120 кв.м.")
    team = models.TextField("Команда", blank=True,
                            help_text="По одной строке: «Должность: Имя». Должность выводится жирным.")

    categories = models.ManyToManyField(Category, verbose_name="Категории", blank=True, related_name="projects",
                                        help_text="По ним посетители фильтруют проекты на странице «Проекты».")
    order = models.PositiveIntegerField("Порядок", default=0, help_text="Меньше число — выше в списке.")
    is_published = models.BooleanField("Опубликован", default=True)
    show_in_slider = models.BooleanField(
        "Показывать в слайдере на главной", default=False,
        help_text="Обложка проекта добавится в слайдер вверху главной страницы, с названием и ссылкой на проект. "
                  "Лучше подходят горизонтальные фото от 2400 px по ширине. Порядок слайдов — по полю «Порядок».",
    )
    show_on_home = models.BooleanField("Показывать на главной", default=True,
                                       help_text="На главной выводятся первые 6 отмеченных проектов (3 × 2).")

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["order", "-id"]

    def __str__(self):
        return f"{self.title} {self.subtitle}".strip()

    def get_absolute_url(self):
        return reverse("project_detail", args=[self.slug])


class ProjectItem(models.Model):
    """Элемент содержимого страницы проекта. Страница — это ряды на сетке из 6 колонок."""

    KINDS = [("image", "Фото"), ("text", "Текст")]
    ALIGNS = [("start", "Сверху"), ("center", "По центру"), ("end", "Снизу")]
    SPACES = [("s", "Малый"), ("m", "Средний"), ("l", "Большой")]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="items")
    row = models.PositiveSmallIntegerField("Ряд", default=1,
                                           help_text="Элементы с одинаковым номером ряда стоят на одной линии.")
    kind = models.CharField("Что это", max_length=10, choices=KINDS, default="image")
    image = models.ImageField("Фото", upload_to="projects/content/", blank=True,
                              width_field="image_width", height_field="image_height")
    image_width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    image_height = models.PositiveIntegerField(null=True, blank=True, editable=False)
    text = models.TextField("Текст", blank=True, help_text="Пустая строка — новый абзац. **Текст** — жирным.")
    col_start = models.PositiveSmallIntegerField("С колонки (1–6)", default=1,
                                                 validators=[MinValueValidator(1), MaxValueValidator(6)])
    col_span = models.PositiveSmallIntegerField("Ширина в колонках (1–6)", default=2,
                                                validators=[MinValueValidator(1), MaxValueValidator(6)])
    align = models.CharField("Выравнивание в ряду", max_length=10, choices=ALIGNS, default="start")
    space = models.CharField("Отступ сверху", max_length=1, choices=SPACES, default="m",
                             help_text="Для ряда берётся значение из его первого (левого) элемента.")
    full_bleed = models.BooleanField("Фото на всю ширину экрана", default=False,
                                     help_text="Тексты из того же ряда ложатся поверх такого фото.")
    light_text = models.BooleanField("Светлый текст", default=False,
                                     help_text="Для текста поверх тёмного фото.")
    bring_to_front = models.BooleanField("На передний план", default=False,
                                         help_text="Элемент ляжет поверх соседей по ряду, если их колонки пересекаются.")

    class Meta:
        verbose_name = "Элемент страницы"
        verbose_name_plural = "Содержимое страницы проекта"
        ordering = ["row", "col_start", "id"]

    def __str__(self):
        return f"Ряд {self.row}: {self.get_kind_display()}"

    def clean(self):
        if self.col_start and self.col_span and self.col_start + self.col_span > 7:
            raise ValidationError("Колонка начала + ширина не должны выходить за 6-ю колонку.")
        if self.kind == "image" and not self.image:
            raise ValidationError("Для элемента «Фото» загрузите изображение.")
        if self.kind == "text" and not self.text.strip():
            raise ValidationError("Для элемента «Текст» заполните текст.")


class ContactBlock(models.Model):
    COLUMNS = [("order", "Подвал сайта («Заказать проект»)"), ("coop", "Страница «Контакты» («Сотрудничество»)")]
    column = models.CharField("Где показывать", max_length=10, choices=COLUMNS, default="order")
    label = models.CharField("Подпись", max_length=60, help_text="Например: Подрядчикам, Почта, Адрес.")
    text = models.TextField("Текст", help_text="Телефоны и e-mail автоматически становятся ссылками. Новая строка — перенос.")
    show_in_footer = models.BooleanField("Показывать в подвале", default=True,
                                         help_text="На странице «Контакты» показываются все контакты.")
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Контакт в подвале"
        verbose_name_plural = "Контакты в подвале"
        ordering = ["column", "order", "id"]

    def __str__(self):
        return self.label


class ContactRequest(models.Model):
    name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=40)
    email = models.EmailField("E-mail", blank=True)
    message = models.TextField("Сообщение")
    created_at = models.DateTimeField("Получена", auto_now_add=True)
    is_processed = models.BooleanField("Обработана", default=False)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки с сайта"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}, {self.phone}"
