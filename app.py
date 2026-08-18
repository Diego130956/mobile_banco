import asyncio
import flet
from flet import ThemeMode, View, Colors, ListView, Icons, ListTile, Image, Column, Text, \
    NavigationBar, NavigationBarDestination, FontWeight, Card, Row, Container, Icon, IconButton

# Importa os módulos externos
from api_endpoints import get_produtos
from models import obter_sessao, Produto, Review

def main(page: flet.Page):
    page.title = "Mercado & SQLAlchemy"
    page.theme_mode = ThemeMode.LIGHT
    page.window.width = 400
    page.window.height = 700

    # Variável de controle de abas ("0" = Vitrine, "1" = Carrinho)
    aba_atual = "0"

    def obter_ids_salvos():
        sessao = obter_sessao()
        ids = {p.id for p in sessao.query(Produto.id).all()}
        sessao.close()
        return ids

    def adicionar_ao_banco(item_dados):
        sessao = obter_sessao()
        try:
            if sessao.query(Produto).filter_by(id=item_dados['id']).first():
                return

            novo_produto = Produto(
                id=item_dados['id'],
                title=item_dados['title'],
                description=item_dados['description'],
                category=item_dados['category'],
                price=item_dados['price'],
                thumbnail=item_dados['thumbnail']
            )

            for item in item_dados.get('reviews', []):
                nova_review = Review(
                    rating=item.get('rating'),
                    comment=item.get('comment'),
                    date=item.get('date'),
                    reviewerName=item.get('reviewerName'),
                    reviewerEmail=item.get('reviewerEmail')
                )
                novo_produto.reviews.append(nova_review)

            sessao.add(novo_produto)
            sessao.commit()
        except Exception as e:
            sessao.rollback()
            print(f"Erro ao salvar: {e}")
        finally:
            sessao.close()

        renderizar_tela()

    def renderizar_tela():
        list_view.controls.clear()

        if aba_atual == "0":
            dados_api = get_produtos()
            ids_salvos = obter_ids_salvos()

            for item in dados_api["products"]:
                ja_adicionado = item["id"] in ids_salvos

                if ja_adicionado:
                    indicador = Icon(Icons.CHECK_CIRCLE, color=Colors.GREEN, size=28)
                else:
                    indicador = IconButton(
                        icon=Icons.ADD_SHOPPING_CART,
                        icon_color=Colors.BLUE,
                        icon_size=24,
                        on_click=lambda e, i=item: [adicionar_ao_banco(i), renderizar_tela()]
                    )

                list_view.controls.append(
                    Card(
                        content=Container(
                            content=Row([
                                Image(src=item["thumbnail"], width=80, height=80, fit="cover"),
                                Column([
                                    Text(item["title"], weight=FontWeight.BOLD, color=Colors.BLACK, max_lines=1),
                                    Text(f"Cat: {item['category']}", color=Colors.GREY_700),
                                    Row([
                                        Text(f"${item['price']:.2f}", color=Colors.ORANGE_700, weight=FontWeight.BOLD,
                                             size=16),
                                        indicador
                                    ], alignment="spaceBetween")
                                ], spacing=2, expand=True)
                            ], alignment="start"),
                            padding=10
                        )
                    )
                )

        elif aba_atual == "1":
            sessao = obter_sessao()
            produtos_carrinho = sessao.query(Produto).all()
            sessao.close()

            if not produtos_carrinho:
                list_view.controls.append(
                    Container(content=Text("Carrinho vazio!", size=14, color=Colors.GREY_600), padding=20)
                )
            else:
                for item in produtos_carrinho:
                    list_view.controls.append(
                        ListTile(
                            leading=Image(src=item.thumbnail, width=50),
                            title=Text(item.title, weight=FontWeight.BOLD),
                            subtitle=Text(f"Preço: ${item.price:.2f}"),
                            trailing=Icon(Icons.CHECK, color=Colors.GREEN)
                        )
                    )

        page.update()

    def ao_mudar_aba(e):
        nonlocal aba_atual
        aba_atual = str(e.data)
        renderizar_tela()

    list_view = ListView(expand=True, spacing=10)

    def route_change(e=None):
        page.views.clear()
        page.views.append(
            View(
                route="/",
                controls=[
                    flet.AppBar(
                        title=Text("Mercado SQLAlchemy", weight=FontWeight.BOLD, color=Colors.WHITE),
                        bgcolor=Colors.ORANGE,
                        automatically_imply_leading=False
                    ),
                    list_view,
                    NavigationBar(
                        selected_index=int(aba_atual),
                        destinations=[
                            NavigationBarDestination(icon=Icons.SHOPPING_BAG, label="Vitrine API"),
                            NavigationBarDestination(icon=Icons.SHOPPING_CART, label="Meu Carrinho"),
                        ],
                        on_change=ao_mudar_aba,
                    )
                ],
                padding=10
            )
        )
        renderizar_tela()

    page.on_route_change = route_change
    route_change()


flet.run(main)
