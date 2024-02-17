class GameManager:
    def __init__(self, room):
        self.room = []

    def create_game(self, game_name, game_type, game_mode, game_map, game_password, game_max_players, game_owner):
        game = Game(game_name, game_type, game_mode, game_map, game_password, game_max_players, game_owner)
        self.games.append(game)
        return game

    def get_game(self, game_id):
        for game in self.games:
            if game.id == game_id:
                return game
        return None

    def get_games(self):
        return self.games

    def remove_game(self, game_id):
        for game in self.games:
            if game.id == game_id:
                self.games.remove(game)
                return True
        return False