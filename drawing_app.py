import pygame
import sys
import math
from pygame import gfxdraw

# Inisialisasi Pygame
pygame.init()

# Konstanta
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
TOOLBAR_HEIGHT = 100  # Slightly taller toolbar
DRAWING_AREA_HEIGHT = SCREEN_HEIGHT - TOOLBAR_HEIGHT

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (240, 240, 240)
DARK_GRAY = (60, 60, 60)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
BROWN = (139, 69, 19)
NAVY = (0, 0, 128)
LIME = (0, 255, 128)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
OLIVE = (128, 128, 0)
MAROON = (128, 0, 0)
TEAL = (0, 128, 128)
VIOLET = (238, 130, 238)

# Daftar warna yang tersedia
COLORS = [
    BLACK, RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, PINK, CYAN,
    BROWN, NAVY, LIME, GOLD, SILVER, OLIVE, MAROON, TEAL, VIOLET
]
COLOR_NAMES = [
    "Hitam", "Merah", "Hijau", "Biru", "Kuning", "Oranye", "Ungu", "Pink", "Cyan",
    "Coklat", "Navy", "Lime", "Gold", "Silver", "Olive", "Maroon", "Teal", "Violet"
]

# Mode menggambar
MODES = ["Titik", "Garis", "Persegi", "Lingkaran", "Elipse", "Poligon"]

class DrawingApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PyDraw - Aplikasi Menggambar")
        
        self.clock = pygame.time.Clock()
        self.running = True

        # Load custom font if available
        try:
            self.title_font = pygame.font.Font("segoeui.ttf", 28)
            self.font = pygame.font.Font("segoeui.ttf", 20)
            self.small_font = pygame.font.Font("segoeui.ttf", 16)
            self.mode_font = pygame.font.Font("segoeui.ttf", 14)
        except:
            # Fallback to system fonts
            self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
            self.font = pygame.font.SysFont("Arial", 20)
            self.small_font = pygame.font.SysFont("Arial", 16)
            self.mode_font = pygame.font.SysFont("Arial", 14)

        # State aplikasi
        self.current_mode = 0
        self.current_color = 0
        self.drawing = False
        self.start_pos = None
        self.current_pos = None
        self.brush_size = 3
        self.fill_mode = False

        # Surface untuk area menggambar
        self.drawing_surface = pygame.Surface((SCREEN_WIDTH, DRAWING_AREA_HEIGHT))
        self.drawing_surface.fill(WHITE)

        # List untuk menyimpan titik-titik
        self.connected_points = []
        self.connecting_mode = False

        # UI elements
        self.ui_rect = pygame.Rect(0, 0, SCREEN_WIDTH, TOOLBAR_HEIGHT)
        self.logo_text = self.title_font.render("PyDraw", True, (50, 50, 50))
        
        # Load icons (fallback to text if icons not available)
        self.icons = {}
        try:
            # Try to load simple icons (in a real app, you'd have actual image files)
            self.icons["point"] = self.create_icon("•", (20, 20))
            self.icons["line"] = self.create_icon("/", (20, 20))
            self.icons["rect"] = self.create_icon("□", (20, 20))
            self.icons["circle"] = self.create_icon("○", (20, 20))
            self.icons["ellipse"] = self.create_icon("~", (20, 20))
            self.icons["polygon"] = self.create_icon("⬟", (20, 20))
        except:
            self.icons = None

    def create_icon(self, text, size):
        """Create a simple icon from text"""
        icon = pygame.Surface(size, pygame.SRCALPHA)
        text_surf = self.mode_font.render(text, True, BLACK)
        icon.blit(text_surf, (size[0]//2 - text_surf.get_width()//2, 
                             size[1]//2 - text_surf.get_height()//2))
        return icon

    def draw_toolbar(self):
        # Modern toolbar background with subtle shadow
        pygame.draw.rect(self.screen, LIGHT_GRAY, self.ui_rect)
        pygame.draw.line(self.screen, (200, 200, 200), 
                         (0, TOOLBAR_HEIGHT), 
                         (SCREEN_WIDTH, TOOLBAR_HEIGHT), 2)
        
        # App logo/title
        self.screen.blit(self.logo_text, (20, 15))
        
        # Separator line
        pygame.draw.line(self.screen, (200, 200, 200), (150, 10), (150, TOOLBAR_HEIGHT-10), 1)

        # Tools panel
        tools_x = 170
        tools_y = 15
        tool_size = 40
        
        # Draw tools with icons or text
        for i, mode in enumerate(MODES):
            # Tool background (selected/unselected)
            tool_rect = pygame.Rect(tools_x, tools_y, tool_size, tool_size)
            bg_color = (220, 240, 255) if i == self.current_mode else LIGHT_GRAY
            border_color = (100, 180, 255) if i == self.current_mode else (180, 180, 180)
            
            pygame.draw.rect(self.screen, bg_color, tool_rect, border_radius=6)
            pygame.draw.rect(self.screen, border_color, tool_rect, 2, border_radius=6)
            
            # Tool icon or text
            if self.icons and mode in ["Titik", "Garis", "Persegi", "Lingkaran", "Elipse", "Poligon"]:
                icon_key = mode.lower()[:4]
                if icon_key in self.icons:
                    icon_pos = (tools_x + tool_size//2 - self.icons[icon_key].get_width()//2,
                                tools_y + tool_size//2 - self.icons[icon_key].get_height()//2)
                    self.screen.blit(self.icons[icon_key], icon_pos)
            else:
                # Fallback to text
                mode_text = self.mode_font.render(mode[:4], True, DARK_GRAY)
                self.screen.blit(mode_text, (tools_x + tool_size//2 - mode_text.get_width()//2,
                                           tools_y + tool_size//2 - mode_text.get_height()//2))
            
            tools_x += tool_size + 10

        # Color palette with better layout
        colors_x = tools_x + 20
        colors_y = 15
        color_size = 30
        
        # Color palette label
        color_label = self.small_font.render("Warna:", True, DARK_GRAY)
        self.screen.blit(color_label, (colors_x, colors_y - 20))
        
        # Draw color palette in a grid
        for i, color in enumerate(COLORS):
            row = i // 6
            col = i % 6
            
            color_rect = pygame.Rect(colors_x + col * (color_size + 5), 
                                    colors_y + row * (color_size + 5), 
                                    color_size, color_size)
            
            # Color swatch with shadow
            pygame.draw.rect(self.screen, (220, 220, 220), color_rect.inflate(4, 4), border_radius=4)
            pygame.draw.rect(self.screen, color, color_rect, border_radius=2)
            
            # Selection indicator
            if i == self.current_color:
                pygame.draw.rect(self.screen, (0, 0, 0), color_rect.inflate(4, 4), 2, border_radius=4)
                pygame.draw.rect(self.screen, (255, 255, 255), color_rect.inflate(2, 2), 2, border_radius=3)

        # Brush size control
        brush_x = colors_x + 6 * (color_size + 5) + 20
        brush_y = 15
        
        # Brush label
        brush_label = self.small_font.render("Ukuran:", True, DARK_GRAY)
        self.screen.blit(brush_label, (brush_x, brush_y - 20))
        
        # Brush size buttons
        for i, size in enumerate([1, 3, 5, 8]):
            btn_rect = pygame.Rect(brush_x + i * 35, brush_y, 30, 30)
            btn_color = (200, 230, 255) if size == self.brush_size else LIGHT_GRAY
            
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=4)
            pygame.draw.rect(self.screen, (180, 180, 180), btn_rect, 1, border_radius=4)
            
            # Draw brush size preview
            pygame.draw.circle(self.screen, DARK_GRAY, 
                             (btn_rect.centerx, btn_rect.centery), 
                             size)
        
        # Fill mode toggle
        fill_x = brush_x + 4 * 35 + 20
        fill_rect = pygame.Rect(fill_x, brush_y, 80, 30)
        fill_color = (200, 230, 255) if self.fill_mode else LIGHT_GRAY
        
        pygame.draw.rect(self.screen, fill_color, fill_rect, border_radius=4)
        pygame.draw.rect(self.screen, (180, 180, 180), fill_rect, 1, border_radius=4)
        
        fill_text = self.small_font.render("Isi", True, DARK_GRAY)
        self.screen.blit(fill_text, (fill_x + 40 - fill_text.get_width()//2, 
                                    brush_y + 15 - fill_text.get_height()//2))

        # Status bar at bottom of toolbar
        status_bar = pygame.Rect(0, TOOLBAR_HEIGHT - 25, SCREEN_WIDTH, 25)
        pygame.draw.rect(self.screen, (230, 230, 230), status_bar)
        pygame.draw.line(self.screen, (200, 200, 200), 
                         (0, TOOLBAR_HEIGHT - 25), 
                         (SCREEN_WIDTH, TOOLBAR_HEIGHT - 25), 1)
        
        # Status text
        status_text = f"Mode: {MODES[self.current_mode]} | Warna: {COLOR_NAMES[self.current_color]} | Ukuran: {self.brush_size}"
        if self.fill_mode:
            status_text += " | Mode Isi"
        if self.connecting_mode:
            status_text += " | Mode Poligon (Klik kanan untuk selesai)"
        
        status_surface = self.small_font.render(status_text, True, DARK_GRAY)
        self.screen.blit(status_surface, (10, TOOLBAR_HEIGHT - 20))

        # Help text
        help_text = "Tips: C = Poligon | R = Reset | Q = Keluar | F = Mode Isi"
        help_surface = self.small_font.render(help_text, True, (100, 100, 100))
        self.screen.blit(help_surface, (SCREEN_WIDTH - help_surface.get_width() - 10, 
                                      TOOLBAR_HEIGHT - 20))

    def handle_toolbar_click(self, pos):
        x, y = pos

        # Check tool selection
        tools_x = 170
        tools_y = 15
        tool_size = 40
        
        if tools_y <= y <= tools_y + tool_size:
            for i in range(len(MODES)):
                if tools_x <= x <= tools_x + tool_size:
                    self.current_mode = i
                    if i != 5:  # If not polygon mode
                        self.connecting_mode = False
                        self.connected_points = []
                    return
                tools_x += tool_size + 10

        # Check color selection
        colors_x = tools_x + 20
        colors_y = 15
        color_size = 30
        
        for i in range(len(COLORS)):
            row = i // 6
            col = i % 6
            
            if (colors_x + col * (color_size + 5) <= x <= colors_x + col * (color_size + 5) + color_size and
                colors_y + row * (color_size + 5) <= y <= colors_y + row * (color_size + 5) + color_size):
                self.current_color = i
                return

        # Check brush size selection
        brush_x = colors_x + 6 * (color_size + 5) + 20
        brush_y = 15
        
        if brush_y <= y <= brush_y + 30:
            for i, size in enumerate([1, 3, 5, 8]):
                if brush_x + i * 35 <= x <= brush_x + i * 35 + 30:
                    self.brush_size = size
                    return

        # Check fill mode toggle
        fill_x = brush_x + 4 * 35 + 20
        if fill_x <= x <= fill_x + 80 and brush_y <= y <= brush_y + 30:
            self.fill_mode = not self.fill_mode

    def draw_point(self, pos):
        pygame.draw.circle(self.drawing_surface, COLORS[self.current_color], pos, self.brush_size)

    def draw_line(self, start, end):
        pygame.draw.line(self.drawing_surface, COLORS[self.current_color], start, end, self.brush_size)

    def draw_rectangle(self, start, end):
        width = abs(end[0] - start[0])
        height = abs(end[1] - start[1])
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        
        if self.fill_mode:
            pygame.draw.rect(self.drawing_surface, COLORS[self.current_color], (x, y, width, height))
        else:
            pygame.draw.rect(self.drawing_surface, COLORS[self.current_color], (x, y, width, height), self.brush_size)

    def draw_circle(self, center, end):
        radius = int(math.sqrt((end[0] - center[0])**2 + (end[1] - center[1])**2))
        if radius > 0:
            if self.fill_mode:
                pygame.draw.circle(self.drawing_surface, COLORS[self.current_color], center, radius)
            else:
                pygame.draw.circle(self.drawing_surface, COLORS[self.current_color], center, radius, self.brush_size)

    def draw_ellipse(self, start, end):
        width = abs(end[0] - start[0])
        height = abs(end[1] - start[1])
        if width > 0 and height > 0:
            x = min(start[0], end[0])
            y = min(start[1], end[1])
            
            if self.fill_mode:
                pygame.draw.ellipse(self.drawing_surface, COLORS[self.current_color], (x, y, width, height))
            else:
                pygame.draw.ellipse(self.drawing_surface, COLORS[self.current_color], (x, y, width, height), self.brush_size)

    def draw_polygon(self):
        if len(self.connected_points) >= 3:
            if self.fill_mode:
                pygame.draw.polygon(self.drawing_surface, COLORS[self.current_color], self.connected_points)
            else:
                pygame.draw.polygon(self.drawing_surface, COLORS[self.current_color], self.connected_points, self.brush_size)

    def draw_preview(self):
        # Gambar preview untuk shape yang sedang digambar
        if self.drawing and self.start_pos and self.current_pos:
            preview_surface = self.drawing_surface.copy()
            
            if self.current_mode == 1:  # Garis
                pygame.draw.line(preview_surface, COLORS[self.current_color], 
                               self.start_pos, self.current_pos, self.brush_size)
            elif self.current_mode == 2:  # Persegi
                width = abs(self.current_pos[0] - self.start_pos[0])
                height = abs(self.current_pos[1] - self.start_pos[1])
                x = min(self.start_pos[0], self.current_pos[0])
                y = min(self.start_pos[1], self.current_pos[1])
                
                if self.fill_mode:
                    pygame.draw.rect(preview_surface, COLORS[self.current_color], (x, y, width, height))
                else:
                    pygame.draw.rect(preview_surface, COLORS[self.current_color], (x, y, width, height), self.brush_size)
            elif self.current_mode == 3:  # Lingkaran
                radius = int(math.sqrt((self.current_pos[0] - self.start_pos[0])**2 + 
                                     (self.current_pos[1] - self.start_pos[1])**2))
                if radius > 0:
                    if self.fill_mode:
                        pygame.draw.circle(preview_surface, COLORS[self.current_color], 
                                         self.start_pos, radius)
                    else:
                        pygame.draw.circle(preview_surface, COLORS[self.current_color], 
                                         self.start_pos, radius, self.brush_size)
            elif self.current_mode == 4:  # Elipse
                width = abs(self.current_pos[0] - self.start_pos[0])
                height = abs(self.current_pos[1] - self.start_pos[1])
                if width > 0 and height > 0:
                    x = min(self.start_pos[0], self.current_pos[0])
                    y = min(self.start_pos[1], self.current_pos[1])
                    
                    if self.fill_mode:
                        pygame.draw.ellipse(preview_surface, COLORS[self.current_color], 
                                          (x, y, width, height))
                    else:
                        pygame.draw.ellipse(preview_surface, COLORS[self.current_color], 
                                          (x, y, width, height), self.brush_size)
            
            return preview_surface
        
        # Draw connected points preview
        if self.connecting_mode and self.connected_points:
            preview_surface = self.drawing_surface.copy()
            
            if len(self.connected_points) > 1:
                pygame.draw.lines(preview_surface, COLORS[self.current_color], False, 
                                self.connected_points, self.brush_size)
            
            # Draw current line to mouse position if available
            if self.current_pos:
                pygame.draw.line(preview_surface, COLORS[self.current_color], 
                                self.connected_points[-1], self.current_pos, self.brush_size)
            
            return preview_surface
        
        return self.drawing_surface

    def handle_drawing_click(self, pos, button):
        drawing_pos = (pos[0], pos[1] - TOOLBAR_HEIGHT)
        
        if button == 1:  # Left click
            if self.connecting_mode or self.current_mode == 5:  # Polygon mode
                self.connecting_mode = True
                self.connected_points.append(drawing_pos)
                self.draw_point(drawing_pos)
                
                if len(self.connected_points) > 1:
                    self.draw_line(self.connected_points[-2], self.connected_points[-1])
            
            elif self.current_mode == 0:  # Titik
                self.draw_point(drawing_pos)
            
            else:  # Shapes yang membutuhkan drag
                if not self.drawing:
                    self.drawing = True
                    self.start_pos = drawing_pos
                else:
                    self.drawing = False
                    if self.current_mode == 1:  # Garis
                        self.draw_line(self.start_pos, drawing_pos)
                    elif self.current_mode == 2:  # Persegi
                        self.draw_rectangle(self.start_pos, drawing_pos)
                    elif self.current_mode == 3:  # Lingkaran
                        self.draw_circle(self.start_pos, drawing_pos)
                    elif self.current_mode == 4:  # Elipse
                        self.draw_ellipse(self.start_pos, drawing_pos)
                    
                    self.start_pos = None
                    self.current_pos = None
        
        elif button == 3:  # Right click
            if self.connecting_mode:
                if len(self.connected_points) >= 3:
                    self.draw_polygon()
                self.connecting_mode = False
                self.connected_points = []

    def handle_mouse_motion(self, pos):
        if self.drawing:
            self.current_pos = (pos[0], pos[1] - TOOLBAR_HEIGHT)
        elif self.connecting_mode:
            self.current_pos = (pos[0], pos[1] - TOOLBAR_HEIGHT)

    def reset_canvas(self):
        self.drawing_surface.fill(WHITE)
        self.drawing = False
        self.start_pos = None
        self.current_pos = None
        self.connecting_mode = False
        self.connected_points = []

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False
                    elif event.key == pygame.K_r:
                        self.reset_canvas()
                    elif event.key == pygame.K_c:
                        self.connecting_mode = not self.connecting_mode
                        if self.connecting_mode:
                            self.current_mode = 5  # Set ke mode poligon
                            self.connected_points = []
                        else:
                            self.connected_points = []
                    elif event.key == pygame.K_f:
                        self.fill_mode = not self.fill_mode
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.pos[1] < TOOLBAR_HEIGHT:
                        self.handle_toolbar_click(event.pos)
                    else:
                        self.handle_drawing_click(event.pos, event.button)
                
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event.pos)
            
            # Render
            self.screen.fill(WHITE)
            
            # Gambar area drawing dengan preview
            preview_surface = self.draw_preview()
            self.screen.blit(preview_surface, (0, TOOLBAR_HEIGHT))
            
            # Gambar toolbar
            self.draw_toolbar()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = DrawingApp()
    app.run()