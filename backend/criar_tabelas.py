"""Cria o esquema PostgreSQL e prepara o catálogo de grupos e permissões."""

from banco import inicializar_banco


def main():
    inicializar_banco(semear_demos=False)
    print("Tabelas criadas e catálogo de permissões preparado.")


if __name__ == "__main__":
    main()
