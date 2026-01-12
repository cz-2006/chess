# -*- coding: utf-8 -*-
import pygame
import sys
from enum import Enum
import random

class Player(Enum):
    HUMAN = 1
    AI = 2
    EMPTY = 0

class Difficulty(Enum):
    EASY = 1
    HARD = 2

class GomokuGame:
    def __init__(self, board_size=15, window_size=900, difficulty=Difficulty.HARD):
        self.board_size = board_size
        self.window_size = window_size
        self.margin = 60
        self.board_width = window_size - 2 * self.margin
        self.cell_size = self.board_width // (board_size - 1)
        self.board = [[Player.EMPTY for _ in range(board_size)] for _ in range(board_size)]
        self.game_over = False
        self. winner = None
        self.last_move = None
        self. human_turn = True
        self. ai_thinking = False
        self. human_win_rate = 50.0
        self.ai_win_rate = 50.0
        self.difficulty = difficulty
        self.in_menu = True
        
        pygame.init()
        self.screen = pygame.display.set_mode((window_size, window_size))
        pygame.display.set_caption("Five in a Row")
        self.font_large = pygame.font.Font(None, 56)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 20)
        self.clock = pygame.time.Clock()
        
    def draw_menu(self):
        """Draw difficulty selection menu"""
        self.screen. fill((40, 30, 20))
        
        title = self.font_large.render("Gomoku", True, (200, 160, 100))
        title_rect = title.get_rect(center=(self.window_size // 2, 100))
        self.screen.blit(title, title_rect)
        
        prompt = self.font_medium.render("Select Difficulty", True, (200, 200, 150))
        prompt_rect = prompt.get_rect(center=(self.window_size // 2, 200))
        self.screen.blit(prompt, prompt_rect)
        
        easy_button_rect = pygame.Rect(150, 320, 200, 80)
        easy_color = (100, 200, 255) if self.difficulty == Difficulty. EASY else (80, 150, 200)
        pygame.draw.rect(self.screen, easy_color, easy_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, (150, 200, 255), easy_button_rect, 3, border_radius=10)
        
        easy_text = self.font_medium.render("Easy", True, (255, 255, 255))
        easy_text_rect = easy_text.get_rect(center=easy_button_rect.center)
        self.screen.blit(easy_text, easy_text_rect)
        
        hard_button_rect = pygame. Rect(550, 320, 200, 80)
        hard_color = (255, 150, 100) if self.difficulty == Difficulty.HARD else (200, 100, 80)
        pygame.draw.rect(self.screen, hard_color, hard_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 200, 150), hard_button_rect, 3, border_radius=10)
        
        hard_text = self.font_medium.render("Hard", True, (255, 255, 255))
        hard_text_rect = hard_text.get_rect(center=hard_button_rect.center)
        self.screen.blit(hard_text, hard_text_rect)
        
        start_hint = self.font_small.render("Click to start", True, (200, 200, 150))
        start_hint_rect = start_hint.get_rect(center=(self.window_size // 2, 500))
        self.screen.blit(start_hint, start_hint_rect)
        
        easy_desc = self.font_tiny.render("Easy AI - Weak", True, (150, 200, 150))
        easy_desc_rect = easy_desc.get_rect(center=(250, 410))
        self.screen.blit(easy_desc, easy_desc_rect)
        
        hard_desc = self.font_tiny.render("Hard AI - Strong", True, (255, 150, 100))
        hard_desc_rect = hard_desc.get_rect(center=(650, 410))
        self.screen.blit(hard_desc, hard_desc_rect)
        
        return {
            'easy': easy_button_rect,
            'hard':  hard_button_rect
        }
    
    def draw_board(self):
        """Draw game board"""
        self.screen. fill((40, 30, 20))
        
        board_color = (200, 160, 100)
        board_rect = pygame.Rect(
            self.margin - 5,
            self.margin - 5,
            self.board_width + 10,
            self.board_width + 10
        )
        pygame.draw.rect(self. screen, board_color, board_rect)
        
        shadow_color = (150, 120, 80)
        pygame.draw.line(
            self.screen,
            shadow_color,
            (self.margin - 5 + 5, self.margin - 5 + self.board_width + 10),
            (self.margin - 5 + self.board_width + 10, self.margin - 5 + self.board_width + 10),
            8
        )
        pygame.draw.line(
            self.screen,
            shadow_color,
            (self.margin - 5 + self.board_width + 10, self.margin - 5 + 5),
            (self.margin - 5 + self.board_width + 10, self.margin - 5 + self.board_width + 10),
            8
        )
        
        for i in range(self.board_size):
            x = self.margin + i * self.cell_size
            pygame.draw.line(
                self.screen,
                (0, 0, 0),
                (x, self.margin),
                (x, self.window_size - self.margin - 100),
                2
            )
            y = self.margin + i * self.cell_size
            pygame. draw.line(
                self. screen,
                (0, 0, 0),
                (self.margin, y),
                (self.window_size - self.margin, y),
                2
            )
        
        star_positions = [
            (3, 3), (3, 11), (11, 3), (11, 11),
            (7, 7)
        ]
        for row, col in star_positions:
            x = self.margin + col * self.cell_size
            y = self.margin + row * self.cell_size
            pygame. draw.circle(self.screen, (0, 0, 0), (x, y), 5)
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] != Player.EMPTY:
                    self.draw_piece(row, col, self.board[row][col])
        
        if self.last_move:
            row, col = self.last_move
            x = self.margin + col * self.cell_size
            y = self.margin + row * self. cell_size
            pygame.draw.circle(self.screen, (255, 100, 100), (x, y), 4)
    
    def draw_piece(self, row, col, player):
        """Draw a piece"""
        x = self.margin + col * self.cell_size
        y = self.margin + row * self. cell_size
        radius = self.cell_size // 2 - 5
        
        if player == Player.HUMAN:
            shadow_offset = 2
            pygame.draw.circle(self.screen, (50, 50, 50), (x + shadow_offset, y + shadow_offset), radius)
            pygame.draw.circle(self.screen, (0, 0, 0), (x, y), radius)
            pygame. draw.circle(self.screen, (80, 80, 80), (x - radius // 3, y - radius // 3), radius // 4)
        else:
            shadow_offset = 2
            pygame.draw.circle(self.screen, (100, 100, 100), (x + shadow_offset, y + shadow_offset), radius)
            pygame.draw.circle(self. screen, (255, 255, 255), (x, y), radius)
            pygame.draw.circle(self. screen, (220, 220, 220), (x - radius // 3, y - radius // 3), radius // 4)
            pygame.draw.circle(self. screen, (100, 100, 100), (x, y), radius, 2)
    
    def get_board_position(self, mouse_pos):
        """Get board position from mouse click"""
        x, y = mouse_pos
        
        board_x = x - self.margin
        board_y = y - self.margin
        
        if board_x < 0 or board_y < 0 or board_x > self.board_width or board_y > self.board_width:
            return None, None
        
        col = round(board_x / self.cell_size)
        row = round(board_y / self.cell_size)
        
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            return row, col
        
        return None, None
    
    def is_valid_move(self, row, col):
        """Check if move is valid"""
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            return False
        return self.board[row][col] == Player.EMPTY
    
    def place_piece(self, row, col, player):
        """Place a piece"""
        if self.is_valid_move(row, col):
            self.board[row][col] = player
            self.last_move = (row, col)
            self.update_win_rates()
            return True
        return False
    
    def check_winner(self, row, col, player):
        """Check if player has won"""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            count = 1
            
            x, y = row + dx, col + dy
            while 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == player:
                count += 1
                x += dx
                y += dy
            
            x, y = row - dx, col - dy
            while 0 <= x < self. board_size and 0 <= y < self.board_size and self.board[x][y] == player:
                count += 1
                x -= dx
                y -= dy
            
            if count >= 5:
                return True
        
        return False
    
    def get_available_moves(self):
        """Get available moves"""
        moves = []
        
        if all(self.board[r][c] == Player.EMPTY for r in range(self.board_size) for c in range(self.board_size)):
            center = self.board_size // 2
            return [(center, center)]
        
        nearby = set()
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] != Player.EMPTY: 
                    for dr in range(-2, 3):
                        for dc in range(-2, 3):
                            new_row = row + dr
                            new_col = col + dc
                            if 0 <= new_row < self.board_size and 0 <= new_col < self.board_size:
                                if self.board[new_row][new_col] == Player. EMPTY:
                                    nearby. add((new_row, new_col))
        
        return list(nearby) if nearby else [(self.board_size // 2, self.board_size // 2)]
    
    def evaluate_position(self, row, col, player):
        """Evaluate position score"""
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            count = 1
            
            x, y = row + dx, col + dy
            while 0 <= x < self.board_size and 0 <= y < self. board_size and self.board[x][y] == player: 
                count += 1
                x += dx
                y += dy
            
            x, y = row - dx, col - dy
            while 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == player:
                count += 1
                x -= dx
                y -= dy
            
            if count >= 5:
                return 100000
            elif count == 4:
                score += 10000
            elif count == 3:
                score += 1000
            elif count == 2:
                score += 100
            elif count == 1:
                score += 10
        
        return score
    
    def update_win_rates(self):
        """Update win rates"""
        human_score = 0.0
        ai_score = 0.0
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == Player.HUMAN: 
                    human_score += self.evaluate_position(row, col, Player.HUMAN)
                elif self.board[row][col] == Player.AI:
                    ai_score += self.evaluate_position(row, col, Player.AI)
        
        total = human_score + ai_score
        if total > 0:
            ratio = human_score / total
            self.human_win_rate = ratio * 100
            self.ai_win_rate = (1 - ratio) * 100
        else:
            self. human_win_rate = 50.0
            self.ai_win_rate = 50.0
        
        if self.human_win_rate + self.ai_win_rate != 100:
            self.ai_win_rate = 100 - self.human_win_rate
    
    def ai_move_easy(self):
        """Easy AI move"""
        available_moves = self.get_available_moves()
        
        if not available_moves: 
            return False
        
        for row, col in available_moves: 
            self.board[row][col] = Player. AI
            if self.check_winner(row, col, Player.AI):
                self.board[row][col] = Player. EMPTY
                self.place_piece(row, col, Player.AI)
                if self.check_winner(row, col, Player.AI):
                    self.game_over = True
                    self.winner = Player.AI
                return True
            self.board[row][col] = Player.EMPTY
        
        for row, col in available_moves:
            self.board[row][col] = Player. HUMAN
            if self.check_winner(row, col, Player. HUMAN):
                self.board[row][col] = Player. EMPTY
                self.place_piece(row, col, Player.AI)
                return True
            self.board[row][col] = Player.EMPTY
        
        best_move = random.choice(available_moves)
        self.place_piece(best_move[0], best_move[1], Player.AI)
        return True
    
    def ai_move_hard(self):
        """Hard AI move"""
        available_moves = self.get_available_moves()
        
        if not available_moves:
            return False
        
        best_move = None
        best_score = -float('inf')
        
        for row, col in available_moves: 
            self.board[row][col] = Player.AI
            
            if self.check_winner(row, col, Player.AI):
                self.board[row][col] = Player.EMPTY
                best_move = (row, col)
                break
            
            ai_score = self.evaluate_position(row, col, Player.AI)
            
            self.board[row][col] = Player.EMPTY
            self.board[row][col] = Player. HUMAN
            
            human_score = self.evaluate_position(row, col, Player. HUMAN)
            
            self.board[row][col] = Player.EMPTY
            
            total_score = ai_score * 1.2 + human_score * 0.8
            
            if total_score > best_score: 
                best_score = total_score
                best_move = (row, col)
        
        if best_move:
            row, col = best_move
            self.place_piece(row, col, Player.AI)
            if self.check_winner(row, col, Player.AI):
                self.game_over = True
                self.winner = Player.AI
            return True
        
        return False
    
    def ai_move(self):
        """AI move"""
        if self.difficulty == Difficulty.EASY: 
            return self.ai_move_easy()
        else:
            return self.ai_move_hard()
    
    def draw_status_bar(self):
        """Draw status bar"""
        bar_height = 100
        bar_y = self.window_size - bar_height
        
        for y in range(bar_height):
            ratio = y / bar_height
            color = (
                int(40 + (60 - 40) * ratio),
                int(30 + (50 - 30) * ratio),
                int(20 + (40 - 20) * ratio)
            )
            pygame.draw.line(self.screen, color, (0, bar_y + y), (self.window_size, bar_y + y))
        
        pygame.draw.line(self.screen, (180, 150, 100), (0, bar_y), (self.window_size, bar_y), 2)
        
        if self.game_over:
            if self.winner == Player.HUMAN:
                text = "You win!"
                color = (100, 255, 100)
            else:
                text = "AI wins!"
                color = (255, 100, 100)
            font = self.font_medium
            hint_text = "Press R to menu"
            hint_color = (200, 200, 150)
        else:
            font = self.font_medium
            hint_color = (200, 200, 150)
            
            if self.human_turn and not self.ai_thinking:
                text = "Your turn"
                color = (150, 220, 255)
            else:
                text = "AI thinking..."
                color = (255, 200, 100)
        
        difficulty_text = "Easy" if self.difficulty == Difficulty.EASY else "Hard"
        difficulty_surface = self.font_tiny.render("Difficulty: " + difficulty_text, True, (200, 200, 150))
        difficulty_rect = difficulty_surface.get_rect(topleft=(20, bar_y + 10))
        self.screen.blit(difficulty_surface, difficulty_rect)
        
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self.window_size // 2, bar_y + 20))
        self.screen.blit(text_surface, text_rect)
        
        self.draw_win_rate_bars(bar_y + 50)
        
        if self.game_over:
            hint_surface = self.font_small.render(hint_text, True, hint_color)
            hint_rect = hint_surface.get_rect(center=(self.window_size // 2, bar_y + 85))
            self.screen.blit(hint_surface, hint_rect)
    
    def draw_win_rate_bars(self, y_pos):
        """Draw win rate bars"""
        bar_width = 300
        bar_height = 20
        left_margin = (self.window_size - bar_width * 2 - 40) // 2
        
        black_x = left_margin
        self.draw_single_bar(black_x, y_pos, bar_width, bar_height,
                            self.human_win_rate, (0, 0, 0), "Black")
        
        white_x = left_margin + bar_width + 40
        self.draw_single_bar(white_x, y_pos, bar_width, bar_height,
                            self.ai_win_rate, (255, 255, 255), "White")
    
    def draw_single_bar(self, x, y, width, height, percentage, color, label):
        """Draw single win rate bar"""
        pygame.draw.rect(self.screen, (80, 80, 80), (x, y, width, height))
        pygame.draw.rect(self.screen, (150, 150, 150), (x, y, width, height), 2)
        
        fill_width = int(width * percentage / 100)
        pygame.draw.rect(self.screen, color, (x, y, fill_width, height))
        
        percentage_text = "{:.1f}%".format(percentage)
        text_surface = self.font_tiny.render(percentage_text, True, (200, 200, 200))
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)
        
        label_surface = self.font_tiny.render(label, True, (200, 200, 200))
        label_rect = label_surface.get_rect(topright=(x - 10, y))
        self.screen.blit(label_surface, label_rect)
    
    def reset_game(self):
        """Reset game"""
        self.__init__(self.board_size, self.window_size, self.difficulty)
    
    def run(self):
        """Run game"""
        running = True
        
        while running:
            if self.in_menu:
                buttons = self.draw_menu()
                pygame.display.flip()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    
                    if event.type == pygame.MOUSEBUTTONDOWN: 
                        mouse_pos = event.pos
                        if buttons['easy']. collidepoint(mouse_pos):
                            self.difficulty = Difficulty.EASY
                            self.in_menu = False
                        elif buttons['hard'].collidepoint(mouse_pos):
                            self.difficulty = Difficulty.HARD
                            self.in_menu = False
                
                self.clock.tick(60)
                continue
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                
                if event. type == pygame.MOUSEBUTTONDOWN and self.human_turn and not self.game_over and not self.ai_thinking:
                    row, col = self.get_board_position(event.pos)
                    if row is not None and col is not None:
                        if self.place_piece(row, col, Player.HUMAN):
                            if self.check_winner(row, col, Player.HUMAN):
                                self.game_over = True
                                self.winner = Player.HUMAN
                            else:
                                self.human_turn = False
                                self.ai_thinking = True
                
                if event.type == pygame.KEYDOWN:
                    if event. key == pygame.K_r:
                        self.in_menu = True
                        self.reset_game()
            
            self.draw_board()
            self.draw_status_bar()
            
            if self.ai_thinking:
                pygame.display.flip()
                pygame.time.wait(400)
                
                if self.ai_move():
                    self.human_turn = True
                    self.ai_thinking = False
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__": 
    game = GomokuGame(board_size=15, window_size=900)
    game.run()