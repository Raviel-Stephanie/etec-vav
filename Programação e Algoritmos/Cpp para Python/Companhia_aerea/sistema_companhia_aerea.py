import json
import os
import csv
import shutil

DATA_FILE = "companhia_aerea_dados.json"

passengers = []
flights = []
tickets = []


def load_data():
    global passengers, flights, tickets

    if not os.path.exists(DATA_FILE):
        passengers = []
        flights = []
        tickets = []
        return

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            passengers = data.get("passengers", [])
            flights = data.get("flights", [])
            tickets = data.get("tickets", [])
    except (json.JSONDecodeError, OSError):
        print("Não foi possível carregar os dados. Iniciando com listas vazias.")
        passengers = []
        flights = []
        tickets = []


def save_data():
    data = {
        "passengers": passengers,
        "flights": flights,
        "tickets": tickets
    }

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def find_passenger_by_cpf(cpf):
    for passenger in passengers:
        if passenger["cpf"] == cpf:
            return passenger
    return None


def find_flight_by_code(code):
    for flight in flights:
        if flight["code"].lower() == code.lower():
            return flight
    return None


def find_ticket_by_code(code):
    for ticket in tickets:
        if ticket["code"].lower() == code.lower():
            return ticket
    return None


def register_passenger():
    print("\n--- Cadastro de passageiro ---")
    cpf = input("CPF: ").strip()

    if not cpf:
        print("O CPF não pode ficar vazio.")
        return

    if find_passenger_by_cpf(cpf) is not None:
        print("Já existe um passageiro cadastrado com este CPF.")
        return

    name = input("Nome completo: ").strip()
    phone = input("Telefone: ").strip()
    email = input("E-mail: ").strip()

    if not name:
        print("O nome não pode ficar vazio.")
        return

    passenger = {
        "name": name,
        "cpf": cpf,
        "phone": phone,
        "email": email
    }

    passengers.append(passenger)
    save_data()
    print("Passageiro cadastrado com sucesso!")


def list_passengers():
    if not passengers:
        print("Nenhum passageiro cadastrado.")
        return

    print("\n--- Passageiros cadastrados ---")
    for passenger in passengers:
        print(f"Nome: {passenger['name']}")
        print(f"CPF: {passenger['cpf']}")
        print(f"Telefone: {passenger['phone']}")
        print(f"E-mail: {passenger['email']}")
        print("-" * 30)


def register_flight():
    print("\n--- Cadastro de voo ---")
    code = input("Número/código do voo: ").strip()

    if not code:
        print("O código do voo não pode ficar vazio.")
        return

    if find_flight_by_code(code) is not None:
        print("Já existe um voo com este código.")
        return

    origin = input("Origem: ").strip()
    destination = input("Destino: ").strip()
    date = input("Data (DD/MM/AAAA): ").strip()
    time = input("Horário (HH:MM): ").strip()

    try:
        price = float(input("Preço da passagem (R$): ").replace(",", "."))
        seats = int(input("Quantidade de assentos do voo: "))
    except ValueError:
        print("Preço ou quantidade de assentos inválidos.")
        return

    if not origin or not destination or not date or not time:
        print("Preencha todos os dados do voo.")
        return

    if price <= 0 or seats <= 0:
        print("O preço e a quantidade de assentos devem ser maiores que zero.")
        return

    flight = {
        "code": code,
        "origin": origin,
        "destination": destination,
        "date": date,
        "time": time,
        "price": round(price, 2),
        "seats": seats,
        "occupied_seats": []
    }

    flights.append(flight)
    save_data()
    print("Voo cadastrado com sucesso!")


def list_flights():
    if not flights:
        print("Nenhum voo cadastrado.")
        return

    print("\n--- Voos disponíveis ---")
    for flight in flights:
        available = flight["seats"] - len(flight["occupied_seats"])
        print(f"Voo: {flight['code']}")
        print(f"Origem: {flight['origin']} | Destino: {flight['destination']}")
        print(f"Data: {flight['date']} | Horário: {flight['time']}")
        print(f"Preço: R$ {flight['price']:.2f}")
        print(f"Assentos disponíveis: {available}/{flight['seats']}")
        print("-" * 35)


def buy_ticket():
    if not flights:
        print("Não há voos cadastrados.")
        return

    cpf = input("Informe o CPF do passageiro: ").strip()
    passenger = find_passenger_by_cpf(cpf)

    if passenger is None:
        print("Passageiro não encontrado. Cadastre-o primeiro.")
        return

    list_flights()
    flight_code = input("Código do voo desejado: ").strip()
    flight = find_flight_by_code(flight_code)

    if flight is None:
        print("Voo não encontrado.")
        return

    available_seats = [
        number for number in range(1, flight["seats"] + 1)
        if number not in flight["occupied_seats"]
    ]

    if not available_seats:
        print("Não há assentos disponíveis neste voo.")
        return

    print("Assentos disponíveis:", ", ".join(map(str, available_seats)))
    try:
        seat = int(input("Escolha o número do assento: "))
    except ValueError:
        print("Número de assento inválido.")
        return

    if seat not in available_seats:
        print("Assento inválido ou já ocupado.")
        return

    extra_baggage = input("Deseja adicionar bagagem extra? (s/n): ").strip().lower()
    baggage_fee = 0.0

    if extra_baggage == "s":
        try:
            baggage_weight = float(input("Peso da bagagem extra em kg: ").replace(",", "."))
        except ValueError:
            print("Peso inválido.")
            return

        if baggage_weight <= 0:
            print("O peso deve ser maior que zero.")
            return

        # Regra demonstrativa: R$ 10,00 por kg de bagagem extra.
        baggage_fee = baggage_weight * 10
    elif extra_baggage != "n":
        print("Resposta inválida. Digite s ou n.")
        return

    total = flight["price"] + baggage_fee
    ticket_code = f"PA{len(tickets) + 1:04d}"

    ticket = {
        "code": ticket_code,
        "passenger_cpf": passenger["cpf"],
        "passenger_name": passenger["name"],
        "flight_code": flight["code"],
        "origin": flight["origin"],
        "destination": flight["destination"],
        "date": flight["date"],
        "time": flight["time"],
        "seat": seat,
        "flight_price": flight["price"],
        "baggage_fee": round(baggage_fee, 2),
        "total": round(total, 2),
        "status": "Ativa"
    }

    flight["occupied_seats"].append(seat)
    tickets.append(ticket)
    save_data()

    print("\nPassagem comprada com sucesso!")
    print(f"Código da passagem: {ticket_code}")
    print(f"Passageiro: {passenger['name']}")
    print(f"Voo: {flight['code']} - {flight['origin']} para {flight['destination']}")
    print(f"Assento: {seat}")
    print(f"Valor da passagem: R$ {flight['price']:.2f}")
    print(f"Taxa de bagagem: R$ {baggage_fee:.2f}")
    print(f"Total: R$ {total:.2f}")


def list_tickets():
    if not tickets:
        print("Nenhuma passagem registrada.")
        return

    print("\n--- Passagens registradas ---")
    for ticket in tickets:
        print(f"Código: {ticket['code']} | Status: {ticket['status']}")
        print(f"Passageiro: {ticket['passenger_name']} (CPF: {ticket['passenger_cpf']})")
        print(f"Voo: {ticket['flight_code']} - {ticket['origin']} para {ticket['destination']}")
        print(f"Data: {ticket['date']} | Horário: {ticket['time']}")
        print(f"Assento: {ticket['seat']} | Total: R$ {ticket['total']:.2f}")
        print("-" * 35)


def cancel_ticket():
    code = input("Código da passagem que deseja cancelar: ").strip()
    ticket = find_ticket_by_code(code)

    if ticket is None:
        print("Passagem não encontrada.")
        return

    if ticket["status"] == "Cancelada":
        print("Esta passagem já foi cancelada.")
        return

    flight = find_flight_by_code(ticket["flight_code"])
    if flight is not None and ticket["seat"] in flight["occupied_seats"]:
        flight["occupied_seats"].remove(ticket["seat"])

    ticket["status"] = "Cancelada"
    save_data()
    print("Passagem cancelada e assento liberado com sucesso.")


def calculate_extra_baggage():
    try:
        weight = float(input("Peso da bagagem extra em kg: ").replace(",", "."))
    except ValueError:
        print("Peso inválido.")
        return

    if weight <= 0:
        print("O peso deve ser maior que zero.")
        return

    fee = weight * 10
    print("Taxa demonstrativa: R$ 10,00 por kg.")
    print(f"Taxa de bagagem extra: R$ {fee:.2f}")


def administrative_report():
    active_tickets = [ticket for ticket in tickets if ticket["status"] == "Ativa"]
    revenue = sum(ticket["total"] for ticket in active_tickets)
    occupied = sum(len(flight["occupied_seats"]) for flight in flights)
    total_seats = sum(flight["seats"] for flight in flights)

    print("\n--- Relatório administrativo ---")
    print(f"Voos cadastrados: {len(flights)}")
    print(f"Passageiros cadastrados: {len(passengers)}")
    print(f"Passagens ativas: {len(active_tickets)}")
    print(f"Passagens canceladas: {sum(1 for ticket in tickets if ticket['status'] == 'Cancelada')}")
    print(f"Assentos ocupados: {occupied}/{total_seats}")
    print(f"Total arrecadado em passagens ativas: R$ {revenue:.2f}")


def export_csv():
    if not tickets:
        print("Nenhuma passagem para exportar.")
        return

    with open("relatorio_passagens.csv", "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow([
            "Código da passagem", "Passageiro", "CPF", "Voo",
            "Origem", "Destino", "Data", "Horário", "Assento",
            "Taxa de bagagem", "Total", "Status"
        ])

        for ticket in tickets:
            writer.writerow([
                ticket["code"], ticket["passenger_name"], ticket["passenger_cpf"],
                ticket["flight_code"], ticket["origin"], ticket["destination"],
                ticket["date"], ticket["time"], ticket["seat"],
                ticket["baggage_fee"], ticket["total"], ticket["status"]
            ])

    print("Relatório exportado com sucesso!")
    print("Arquivo criado: relatorio_passagens.csv")


def create_backup():
    if not os.path.exists(DATA_FILE):
        save_data()

    shutil.copy(DATA_FILE, "backup_companhia_aerea.json")
    print("Backup criado com sucesso!")
    print("Arquivo criado: backup_companhia_aerea.json")


def show_menu():
    print("\n=== Sistema de Companhia Aérea ===")
    print("1 - Cadastrar passageiro")
    print("2 - Listar passageiros")
    print("3 - Cadastrar voo")
    print("4 - Consultar voos")
    print("5 - Comprar passagem")
    print("6 - Consultar passagens")
    print("7 - Cancelar passagem")
    print("8 - Calcular taxa de bagagem extra")
    print("9 - Relatório administrativo")
    print("10 - Exportar relatório para CSV")
    print("11 - Criar backup")
    print("0 - Sair")


def main():
    load_data()

    while True:
        show_menu()
        option = input("Escolha uma opção: ").strip()

        if option == "1":
            register_passenger()
        elif option == "2":
            list_passengers()
        elif option == "3":
            register_flight()
        elif option == "4":
            list_flights()
        elif option == "5":
            buy_ticket()
        elif option == "6":
            list_tickets()
        elif option == "7":
            cancel_ticket()
        elif option == "8":
            calculate_extra_baggage()
        elif option == "9":
            administrative_report()
        elif option == "10":
            export_csv()
        elif option == "11":
            create_backup()
        elif option == "0":
            save_data()
            print("Sistema encerrado.")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
