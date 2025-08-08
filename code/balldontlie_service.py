import requests
from datetime import datetime
class BalldontlieService:
    BASE_URL = "https://api.balldontlie.io/v1"
    API_KEY = "fd8d5216-9ce3-45d1-99c7-ffaa3b716871"

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    @staticmethod
    def get_teams():
        try:
            response = requests.get(f"{BalldontlieService.BASE_URL}/teams", headers=BalldontlieService.headers)
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.RequestException as e:
            print(f"Erreur lors de la récupération des équipes : {e}")
            return []

    @staticmethod
    def get_players(page=1, per_page=100):
        url = f"{BalldontlieService.BASE_URL}/players"
        headers = {
            "Authorization": f"Bearer {BalldontlieService.API_KEY}"
        }
        params = {
            "page": page,
            "per_page": per_page
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()  # ✅ retourne bien tout le JSON (data + meta)
        except requests.RequestException as e:
            print(f"Erreur lors de la récupération des joueurs : {e}")
            return {"data": [], "meta": {"total_pages": 1}}

    
    @staticmethod
    def get_games(season=None, team_ids=None, page=1, per_page=100):
        if season is None:
            today = datetime.today()
            season = today.year if today.month >= 10 else today.year - 1

        # Définir les dates de début et fin selon la saison (format YYYY-MM-DD)
        start_date = f"{season}-10-01"
        end_date = f"{season + 1}-06-30"

        params = {
            "start_date": start_date,
            "end_date": end_date,
            "page": page,
            "per_page": per_page
        }
        if team_ids:
            params["team_ids[]"] = team_ids

        try:
            response = requests.get(
                f"{BalldontlieService.BASE_URL}/games",
                headers=BalldontlieService.headers,
                params=params
            )
            response.raise_for_status()
            data = response.json()

            # Si aucun match trouvé, on essaie la saison précédente
            if not data.get("data"):
                print(f"Aucun match trouvé entre {start_date} et {end_date}, tentative avec saison précédente")
                start_date = f"{season - 1}-10-01"
                end_date = f"{season}-06-30"
                params["start_date"] = start_date
                params["end_date"] = end_date

                response = requests.get(
                    f"{BalldontlieService.BASE_URL}/games",
                    headers=BalldontlieService.headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()

            return data
        except requests.RequestException as e:
            print(f"Erreur lors de la récupération des matchs : {e}")
            return {"data": [], "meta": {}}
