import flet as ft

def main(page : ft.Page):
    page.add(ft.Container(
        content=ft.Text("Hello Riško\n-Ryško", size=50),
        expand=True,
        alignment = ft.Alignment.CENTER
    ))


if __name__ == "__main__":
    ft.run(main)