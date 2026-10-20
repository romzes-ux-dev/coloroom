from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand

from core.models import (AboutPage, Category, ContactBlock, MenuItem, Project, ProjectItem,
                         ProjectsPage, SiteSettings)

SEED = Path(settings.BASE_DIR) / "seed_images"


def attach(obj, field, filename, force=False):
    path = SEED / filename
    if path.exists() and (force or not getattr(obj, field)):
        with path.open("rb") as fh:
            getattr(obj, field).save(filename, File(fh), save=False)


class Command(BaseCommand):
    help = "Заполняет сайт демо-данными из референса. Без --force ничего существующего не затирает."

    def add_arguments(self, parser):
        parser.add_argument("--admin", action="store_true",
                            help="Создать dev-суперпользователя admin / admin12345")
        parser.add_argument("--force", action="store_true",
                            help="Заново подставить демо-фото, порядок проектов и текст блока «О нас»")

    def handle(self, *args, **opts):
        force = opts["force"]

        s = SiteSettings.load()
        attach(s, "hero_image", "hero.jpg", force)
        attach(s, "service_banner", "service-banner.jpg", force)
        attach(s, "about_image", "about-big.jpg", force)
        attach(s, "about_image_small", "about-small.jpg", force)
        attach(s, "footer_bg", "footer-restaurant.jpg", force)
        if force:
            s.about_short = SiteSettings._meta.get_field("about_short").default
            s.copyright_text = SiteSettings._meta.get_field("copyright_text").default
            ContactBlock.objects.filter(label__startswith="Адрес").update(show_in_footer=False)
        s.save()

        about = AboutPage.load()
        attach(about, "banner", "about-banner.jpg", force)
        attach(about, "image", "about-bed.jpg", force)
        attach(about, "philosophy_image", "about-philosophy.jpg", force)
        attach(about, "team_image", "about-team.jpg", force)
        if force:
            for name in ("lead", "body", "statement"):
                setattr(about, name, AboutPage._meta.get_field(name).default)
        about.save()

        pp = ProjectsPage.load()
        attach(pp, "banner", "projects-banner.jpg", force)
        if force:
            pp.intro = ProjectsPage._meta.get_field("intro").default
        pp.save()

        if not MenuItem.objects.exists():
            for i, (title, page) in enumerate([
                ("Главная", "home"), ("О нас", "about"),
                ("Проекты", "projects"), ("Контакты", "contacts"),
            ]):
                MenuItem.objects.create(title=title, page=page, order=i)

        if force or not Project.objects.exists():
            cats = {}
            for i, (slug, name) in enumerate([("architecture", "Архитектура"), ("interiors", "Интерьеры"),
                                              ("commercial", "Коммерческие"), ("residential", "Жилые")]):
                cats[slug], _ = Category.objects.get_or_create(slug=slug, defaults={"name": name, "order": i})

            # (название, тип, slug, фото, год, категории, показывать на главной) — демо-данные
            demo = [
                ("Uzbek Wabi", "Apartment", "uzbek-wabi", "uzbek-wabi.jpg", 2023, ["interiors", "residential"], True),
                ("Eski Shahar", "House", "eski-shahar", "eski-shahar.jpg", 2022, ["architecture", "interiors", "residential"], True),
                ("Mediterranean", "Restaurant", "mediterranean", "mediterranean.jpg", 2024, ["interiors", "commercial"], True),
                ("Quadro", "Restaurant", "quadro", "quadro.jpg", 2024, ["interiors", "commercial"], True),
                ("B&A", "House", "b-a-house", "b-a-house.jpg", 2023, ["architecture", "residential"], True),
                ("Asad", "House", "asad-house", "asad-house.jpg", 2022, ["architecture", "residential"], True),
                ("Sheron", "Residence", "sheron-residence", "sheron-residence.jpg", 2021, ["architecture", "residential"], False),
                ("A&M", "House", "a-m-house", "a-m-house.jpg", 2023, ["interiors", "residential"], False),
            ]
            for i, (title, sub, slug, img, year, cat_slugs, home) in enumerate(demo):
                p, created = Project.objects.get_or_create(slug=slug, defaults=dict(
                    title=title, subtitle=sub, location="Ташкент", year=year, show_on_home=home,
                    short_description="Демо-проект. Замените текст и фото в админке.",
                ))
                p.order = i
                if created or force:
                    p.show_in_slider = home and i < 4   # первые четыре демо-проекта — в слайдер на главной
                attach(p, "cover", img, force)
                p.save()
                if created or force:
                    p.categories.set([cats[c] for c in cat_slugs])

            self.fill_uzbek_wabi(force)

        if not ContactBlock.objects.exists():
            rows = [
                ("coop", "Подрядчикам", "+998 (77) 123-22-33 Анна\ncontractor@coloroom.uz"),
                ("coop", "Соискателям", "+998 (77) 123-33-44\nhr@coloroom.uz"),
                ("coop", "Медиа партнерства", "pr@coloroom.uz"),
                ("order", "Почта :", "info@coloroom.uz\ncoloroominteriors@gmail.com"),
                ("order", "Адрес :", "Центр культуры и искусства, Аллея литераторов,\nориентир метро Миллий бог, г. Ташкент"),
                ("order", "Телефон :", "+998 90 970 08 70\n+998 90 960 07 60"),
            ]
            for i, (col, label, text) in enumerate(rows):
                ContactBlock.objects.create(column=col, label=label, text=text, order=i,
                                            show_in_footer=not label.startswith("Адрес"))

        if opts["admin"]:
            User = get_user_model()
            if not User.objects.filter(username="admin").exists():
                User.objects.create_superuser("admin", "admin@example.com", "admin12345")
                self.stdout.write(self.style.WARNING("Создан admin / admin12345 — только для разработки!"))

        self.stdout.write(self.style.SUCCESS("Готово."))

    # --- страница проекта «Uzbek Wabi» по референсу ---
    def fill_uzbek_wabi(self, force):
        proj = Project.objects.filter(slug="uzbek-wabi").first()
        if not proj:
            return
        proj.year = 2025
        proj.project_type = "Дизайн интерьера жилого помещения"
        proj.status = "Завершён"
        proj.plot_area = "600 кв.м."
        proj.area = "120 кв.м."
        proj.team = ("Художественный руководитель: Заур Мансуров\n"
                     "Арт директор: Ренат Артов\n"
                     "Дизайнер: Маргарита Караваева")
        attach(proj, "banner", "pj-banner.jpg", force)
        attach(proj, "plan_image", "pj-plan.png", force)
        proj.save()

        if proj.items.exists() and not force:
            return
        proj.items.all().delete()

        T = {
            "t1": "Мы проектировали это пространство как тёплый, «живой» дом, в котором современная архитектура сочетается с восточными мотивами. В основе проекта три материала: натуральное дерево, фактурная штукатурка и камень. Основная палитра песочно-бежевая, с тёплыми оттенками дуба. Её оживляют глубокий бирюзовый, сине-серый и насыщенный синий цвета.",
            "t2": "Двухуровневая планировка с антресолью дала нам высокие потолки и открытое пространство. Мы сохранили лёгкость и при этом выделили функциональные зоны с помощью материалов, света и конструкций. Во всех помещениях повторяются одни и те же приёмы: дубовый паркет «ёлочкой», деревянные балки, чёрный металл и плетёные элементы. Благодаря этому квартира воспринимается как единое целое.",
            "t3": "Гостиная объединена с кухней-столовой и стала центром квартиры. Главный акцент здесь — мягкий изогнутый диван сине-серого оттенка. Его плавная форма контрастирует с чёткой геометрией антресоли и лестницы. Светлый ковёр с длинным ворсом заземляет композицию и делает зону отдыха уютной.",
            "t4": "Лестницу на второй уровень мы решили как скульптурный элемент. Ступени из дуба будто парят на металлическом каркасе, а графичное ограждение из тонких чёрных вертикалей с разными промежутками работает как декоративный экран. Два крупных плетёных светильника добавляют объём, натуральную фактуру и мягкий рассеянный свет.",
            "t5": "В прихожей мы хотели сразу задать характер всей квартиры. Стены покрыты фактурной штукатуркой с мягкими скруглёнными углами. На потолке открыты деревянные балки с точечными светильниками, а пол выложен крупноформатной плиткой под травертин.",
            "t6": "Центральным предметом стала консоль из цельного массива дерева с естественным срезом на тонких чёрных металлических опорах. Над ней зеркало в тонкой металлической раме визуально расширяет пространство. Вместо привычной вешалки мы выбрали подвесные металлические крючки, которые крепятся к потолку и не загромождают стену.",
            "t7": "Кухня-столовая — самая яркая по цвету зона. Матовые фасады насыщенного бирюзового оттенка сочетаются с керамическим фартуком в виде чешуи. Блестящая плитка играет на свету и создаёт на стене живой рисунок. Тёплые деревянные элементы уравновешивают холодный цвет.",
            "t8": "Обеденную зону мы определили деревянной балочной конструкцией над столом и другим покрытием пола. Стол из массива с живым краем на чёрных металлических опорах окружают стулья с изогнутыми подлокотниками и мягкими серо-синими сиденьями. Над столом расположен линейный светильник с подвесными плафонами. Лёгкие белые шторы пропускают много дневного света.",
            "t9": "Спальня — самое спокойное и камерное пространство. Стены и потолок мы покрыли единой тёплой штукатуркой в цвете капучино. Они словно обволакивают комнату, а плавно закруглённый переход стены в потолок усиливает ощущение мягкости. Арочная ниша на стене добавляет архитектурной выразительности.",
            "t10": "Главный акцент — резное изголовье из дерева с геометрическим орнаментом в восточном стиле. Этот узор перекликается с традиционными мотивами региона, но выглядит по-современному. Кровать на деревянном основании, прикроватная тумба с округлыми формами и подвесной светильник в виде конуса поддерживают общий язык.",
            "t11": "Ванную мы решили более графично. Стену за ванной облицевали глянцевой плиткой насыщенного синего цвета, уложенной вертикально. Неровная глазурь переливается на свету и создаёт эффект воды. Боковые стены выполнены из крупноформатного керамогранита с рельефной фактурой натурального камня, а пол — в тон прихожей.",
            "t12": "Отдельно стоящая ванна стала центром композиции. Золотистая латунная фурнитура и душевая стойка добавляют благородный акцент и согласуются с тёплыми оттенками остальной квартиры. Полотенцесушитель-полка и встроенная ниша решают бытовые задачи, не нарушая чистоты линий.",
            "t13": "Мы стремились создать интерьер, в котором комфортно жить каждый день и который при этом имеет собственный характер. Натуральные материалы, ручная работа и продуманный свет придают квартире тепло, а смелые цветовые акценты в кухне и ванной не дают ей стать однообразной. Восточные мотивы использованы деликатно: через орнамент, фактуры и предметы декора, поэтому они не превращаются в стилизацию. В результате получился цельный, спокойный и в то же время выразительный дом, в котором каждая деталь работает на общую атмосферу.",
        }

        def img(row, file, start, span, align="start", space="m", full=False):
            it = ProjectItem(project=proj, row=row, kind="image", col_start=start, col_span=span,
                             align=align, space=space, full_bleed=full)
            attach(it, "image", file, True)
            it.save()

        def txt(row, key, start, span, align="start", space="m", light=False):
            ProjectItem.objects.create(project=proj, row=row, kind="text", text=T[key], col_start=start,
                                       col_span=span, align=align, space=space, light_text=light)

        img(1, "pj-full1.jpg", 1, 6, space="l", full=True)
        img(2, "pj-p1.jpg", 3, 2, space="s"); txt(2, "t1", 5, 2, space="s"); txt(2, "t2", 1, 2, "end", "s")
        img(3, "pj-p3.jpg", 1, 2, "end", "s"); img(3, "pj-p2.jpg", 3, 4, space="s")
        txt(4, "t3", 3, 4, space="s")
        txt(5, "t4", 1, 4, space="s")
        img(6, "pj-h1.jpg", 1, 2); img(6, "pj-h2.jpg", 3, 2); img(6, "pj-h3.jpg", 5, 2)
        img(7, "pj-tall.jpg", 1, 6, space="l", full=True)
        txt(7, "t5", 3, 2, light=True); txt(7, "t6", 5, 2, "end", light=True)
        img(8, "pj-bedroom.jpg", 1, 4, space="l"); img(8, "pj-corridor.jpg", 5, 2, space="l")
        txt(9, "t7", 2, 4, space="l")
        img(10, "pj-t1.jpg", 1, 2); img(10, "pj-t2.jpg", 3, 2); img(10, "pj-t3.jpg", 5, 2)
        txt(11, "t8", 2, 4)
        img(12, "pj-living.jpg", 1, 6, space="l", full=True)
        txt(13, "t9", 1, 2, space="l"); img(13, "pj-kitchen.jpg", 3, 4, space="l"); txt(13, "t10", 1, 2, "end", "l")
        img(14, "pj-door.jpg", 1, 4, space="s"); txt(14, "t11", 5, 2, space="s")
        img(15, "pj-bath1.jpg", 1, 2, space="s"); txt(15, "t12", 3, 2, space="s"); img(15, "pj-bath2.jpg", 3, 2, "end", "s")
        img(15, "pj-bath3.jpg", 5, 2, space="s")
        txt(16, "t13", 1, 6)
