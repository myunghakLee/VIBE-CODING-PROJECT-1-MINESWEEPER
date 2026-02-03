import pygame
from constants import *

class InputBox:
    def __init__(self, x, y, w, h, font, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_GRAY
        self.text = text
        self.font = font
        self.txt_surface = self.font.render(text, True, COLOR_WHITE)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = COLOR_LIGHT_GRAY if self.active else COLOR_GRAY
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = COLOR_GRAY
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.unicode.isdigit():
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, COLOR_WHITE)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

class Button:
    def __init__(self, x, y, w, h, font, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font

    def draw(self, screen, color=COLOR_GRAY):
        pygame.draw.rect(screen, color, self.rect)
        txt_surface = self.font.render(self.text, True, COLOR_WHITE)
        text_rect = txt_surface.get_rect(center=self.rect.center)
        screen.blit(txt_surface, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

class MessageBox:
    def __init__(self, w, h, font):
        self.rect = pygame.Rect((SCREEN_WIDTH - w) / 2, (SCREEN_HEIGHT - h) / 2, w, h)
        self.font = font
        self.message = ""
        self.active = False
        self.ok_button = Button(self.rect.centerx - 50, self.rect.bottom - 60, 100, 40, font, "OK")
        self.proceed_button = Button(self.rect.centerx - 110, self.rect.bottom - 60, 100, 40, font, "Proceed")
        self.cancel_button = Button(self.rect.centerx + 10, self.rect.bottom - 60, 100, 40, font, "Cancel")
        self.show_proceed_cancel = False

    def show(self, message, show_proceed_cancel=False):
        self.message = message
        self.active = True
        self.show_proceed_cancel = show_proceed_cancel

    def handle_event(self, event):
        if not self.active:
            return None
        if self.show_proceed_cancel:
            if self.proceed_button.is_clicked(event):
                self.active = False
                return "proceed"
            if self.cancel_button.is_clicked(event):
                self.active = False
                return "cancel"
        else:
            if self.ok_button.is_clicked(event):
                self.active = False
                return "ok"
        return None

    def draw(self, screen):
        if self.active:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            pygame.draw.rect(screen, COLOR_DARK_GRAY, self.rect)
            pygame.draw.rect(screen, COLOR_WHITE, self.rect, 2)
            
            lines = self.message.split('\n')
            y_offset = self.rect.top + 20
            for line in lines:
                txt_surface = self.font.render(line, True, COLOR_WHITE)
                text_rect = txt_surface.get_rect(center=(self.rect.centerx, y_offset))
                screen.blit(txt_surface, text_rect)
                y_offset += self.font.get_height() + 5

            if self.show_proceed_cancel:
                self.proceed_button.draw(screen, COLOR_GREEN)
                self.cancel_button.draw(screen, COLOR_RED)
            else:
                self.ok_button.draw(screen, COLOR_BLUE)
