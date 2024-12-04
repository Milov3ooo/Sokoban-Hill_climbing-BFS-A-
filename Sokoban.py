import threading
import pygame
import sys
import time
import os

from typing import List, Tuple, Optional
from sokoban_common import SokobanState, MOVES
from astar_solver import solve_sokoban_astar
from hill_climbing_solver import solve_sokoban_hillclimbing
from bfs_solver import solve_sokoban_bfs

class SokobanGame:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    GREEN =(34,139,34)
    RED = (220,20,60)
    BLUE = (0, 122, 204)          
    LIGHT_BLUE = (173, 216, 230)
    DARK_BLUE = (0, 0, 139)
    DARK_GRAY = (64, 64, 64)
    MEDIUM_GRAY = (70, 70, 70)    
    LIGHT_GRAY = (100, 100, 100)  
    WHITE = (255, 255, 255)         
    BACKGROUND = (255, 160, 122)

# Khởi tạo
    def __init__(self, window_size: Tuple[int, int] = (1100, 600)):
        pygame.init()
        self.window_size = window_size
        self.screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Sokoban Game (Noel version)")
 
        self.cell_size = 50
        self.load_assets()
        self.maps = self.load_maps('maps.txt')
        self.current_algorithm = 'hillclimbing'
        self.algorithms = ['hillclimbing','astar','bfs']
        self.player_direction = 'player' 
        self.game_time = 0
        self.start_time = None
        self.pause_time = 0
        self.is_paused = False
        self.solve_time = 0
        self.solve_steps = 0      
        self.player_moves = []
        self.player_moves_by_space = []
        self.FONT = pygame.font.Font(None, 48)   
        self.screen = pygame.display.set_mode(self.window_size) 

# Tài nguyên      

    def load_assets(self):
        """
        Tải tài nguyên hình ảnh cho các đối tượng trong trò chơi.

        Hàm Load sẽ đọc danh sách các tài nguyên hình ảnh từ thư mục `img/` và 
        lưu chúng vào `self.images`. Mỗi hình ảnh sẽ được chuyển đổi kích thước 
        để phù hợp với kích thước ô lưới (`self.cell_size`).
               
        """
        assets = ['wall', 'player', 'box', 'target', 'left', 'right', 'up', 'down']
        self.images = {}
        for asset in assets:
            image = pygame.image.load(f'img/{asset}.png')
            self.images[asset] = pygame.transform.scale(image, (self.cell_size, self.cell_size))  

# Giải pháp

    # chuyển bước đi thành dạng kí tự
    def move_to_string(self, move: Tuple[int, int]) -> str:
        """
        Chuyển tuple di chuyển thành ký tự hướng.

           - (-1, 0): 'L' (trái)
           - (1, 0): 'R' (phải)
           - (0, -1): 'U' (lên)
           - (0, 1): 'D' (xuống)
    
        Trả về: Ký tự hướng hoặc '' nếu không hợp lệ.
        """
        move_map = {
            (-1, 0): 'L',
            (1, 0): 'R',
            (0, -1): 'U',
            (0, 1): 'D'
        }
        return move_map.get(move, '')
    
    # Lưu giải pháp
    def save_solution(self, map_index: int):     
        """Lưu giải pháp di chuyển của game Sokoban vào file solution.

        Chức năng:
        - Lưu các bước di chuyển từ người chơi và AI 
        - Tránh trùng lặp các giải pháp đã tồn tại
        - Tạo file solution theo từng map

        Arguments:
            map_index (int): Chỉ số của map hiện tại (zero-indexed)

        Note:
        - Bỏ qua nếu không có bước di chuyển nào
        - Hỗ trợ lưu từ di chuyển thủ công và AI
        - Thêm dấu '#' để phân tách các solution
        """

        if not self.player_moves and not self.player_moves_by_space:
            return

        # Tạo chuỗi cho cả hai loại giải pháp
        solutions_to_save = []
        
        if self.player_moves:
            solution_str = ' '.join(self.move_to_string(move) for move in self.player_moves)
            solutions_to_save.append(solution_str)
        
        if self.player_moves_by_space:
            solution_str_by_space = ' '.join(self.move_to_string(move) for move in self.player_moves_by_space)
            if solution_str_by_space not in solutions_to_save:
                solutions_to_save.append(solution_str_by_space)

        # Đọc các giải pháp hiện có
        existing_solutions = set()
        try:
            with open(f'solution/solution_{map_index + 1}.txt', 'r') as file:
                content = file.read().strip()
                if content:
                    existing_solutions = set(solution.strip() for solution in content.split('#') if solution.strip())
        except FileNotFoundError:
            pass
        new_solutions = [sol for sol in solutions_to_save if sol not in existing_solutions]
        
        if new_solutions:
            with open(f'solution/solution_{map_index + 1}.txt', 'a') as file:
                for solution in new_solutions:
                    if existing_solutions:  # Nếu file không trống, thêm dấu # trước
                        file.write('\n')
                    file.write(f'{solution}\n#')       
                             
    # Sắp xếp giải pháp
    def sort_solutions(self, map_index):
        """Sắp xếp các giải pháp trong file solution theo độ dài.

        Chức năng:
        - Đọc các giải pháp từ file solution của map cụ thể
        - Sắp xếp các giải pháp tăng dần theo số bước di chuyển
        - Ghi lại file với thứ tự giải pháp mới

        Arguments:
            map_index (int): Chỉ số của map (zero-indexed)

        note:
        - Bỏ qua nếu file solution trống
        - Loại bỏ khoảng trắng khi tính độ dài giải pháp
        - Giữ nguyên định dạng file với dấu '#' phân tách
        """
        file_path = f'solution/solution_{map_index+1}.txt'
        try:
        # Đọc nội dung file
            with open(file_path, 'r') as file:
                content = file.read().strip()
                
                # Kiểm tra nếu file trống, bỏ qua
                if not content:
                    # dùng pass để chỉ bỏ qua file này
                    pass  
                
                else:
                    # Tách các dãy kí tự bằng dấu '#' và loại bỏ khoảng trắng thừa
                    sequences = [seq.strip() for seq in content.split('#') if seq.strip()]
                    
                    # Sắp xếp các dãy theo độ dài (không tính khoảng trắng)
                    sorted_sequences = sorted(sequences, key=lambda x: len(x.replace(" ", "")))
                    
                    # Ghi các dãy đã sắp xếp trở lại file
                    with open(file_path, 'w') as file:
                        file.write('\n#\n'.join(sorted_sequences))  # Kết hợp các dãy đã sắp xếp với '#' giữa các dãy
                        file.write('\n#\n')  # Đảm bảo định dạng cuối file giống như ban đầu
        
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")

    # Đọc các giải pháp
    @staticmethod
    def read_solutions(map_index):
        try:
            with open(f'solution/solution_{map_index + 1}.txt', 'r') as file:
                solutions = file.read().split('#')
            return [solution.strip().split() for solution in solutions if solution.strip()]
        except FileNotFoundError:
            return []
        
    # Chuyển giải pháp về đúng dạng
    @staticmethod
    def parse_solution(solution):
        move_dict = {
            'L': (-1, 0),
            'R': (1, 0),
            'U': (0, -1),
            'D': (0, 1)
        }
        return [move_dict[move] for move in solution]
    
# Map
    # Đọc map
    @staticmethod
    def load_maps(filename: str) -> List[List[str]]:
        maps = []
        current_map = []
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('#'):
                    if current_map:
                        maps.append(current_map)
                        current_map = []
                elif line:
                    current_map.append(line)
            if current_map:
                maps.append(current_map)
        return maps
    
    # Chuyển map thành mê cung
    @staticmethod
    def map_to_game_state(map_data: List[str]) -> Tuple[List[List[int]], Tuple[int, int], List[Tuple[int, int]], List[Tuple[int, int]]]:
        maze = []
        player_pos = None
        boxes = []
        targets = []
        
        for y, row in enumerate(map_data):
            maze_row = []
            for x, cell in enumerate(row):
                if cell == 'W':
                    maze_row.append(1)
                elif cell == 'P':
                    maze_row.append(0)
                    player_pos = (x, y)
                elif cell == 'B':
                    maze_row.append(0)
                    boxes.append((x, y))
                elif cell == 'T':
                    maze_row.append(0)
                    targets.append((x, y))
                else:
                    maze_row.append(0)
            maze.append(maze_row)
        return maze, player_pos, boxes, targets
    
    def draw_background(self):
        # Tải hình ảnh nền
        self.background_image = pygame.image.load(os.path.join('img', 'background.png'))
        
        # Điều chỉnh kích thước hình nền cho phù hợp với kích thước cửa sổ
        self.background_image = pygame.transform.scale(self.background_image, (self.window_size[0], self.window_size[1]))
        
        # Vẽ hình nền lên màn hình
        self.screen.blit(self.background_image, (0, 0))

    
    # Vẽ mê cung
    def draw_maze(self, maze: List[List[int]], boxes: List[Tuple[int, int]], targets: List[Tuple[int, int]]):
        self.screen.fill(self.BACKGROUND)
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                pos = (x * self.cell_size, y * self.cell_size)
                if cell == 1:
                    self.screen.blit(self.images['wall'], pos)
                
        for target in targets:
            pos = (target[0] * self.cell_size, target[1] * self.cell_size)
            self.screen.blit(self.images['target'], pos)
            
        for box in boxes:
            pos = (box[0] * self.cell_size, box[1] * self.cell_size)
            self.screen.blit(self.images['box'], pos)

        self.draw_info_panel()

# # Vẽ khung chức năng  
    def draw_info_panel(self):
        panel_rect = pygame.Rect(800, 0, 300, self.window_size[1])
        pygame.draw.rect(self.screen, self.GRAY, panel_rect)

        font = pygame.font.Font(None, 32)

        # Draw time
        clock_icon = pygame.image.load(os.path.join(os.path.dirname(__file__), 'img', 'clock.png')).convert_alpha()
        clock_icon = pygame.transform.scale(clock_icon, (30, 30))
        self.screen.blit(clock_icon, (820, 20))
        time_text = font.render(f"{self.game_time:.5f}s", True, self.BLACK)
        self.screen.blit(time_text, (860, 20))

        # Draw steps
        steps_icon = pygame.image.load(os.path.join(os.path.dirname(__file__), 'img', 'footsteps.png')).convert_alpha()
        steps_icon = pygame.transform.scale(steps_icon, (30, 30))
        self.screen.blit(steps_icon, (820, 50))
        steps_text = font.render(f"{self.solve_steps} steps", True, self.BLACK)
        self.screen.blit(steps_text, (860, 50))

        # Draw algorithm
        algorithm_text = font.render(f"Algorithm: {self.current_algorithm.upper()}", True, self.BLACK)
        self.screen.blit(algorithm_text, (820, 140))

        # Load button images
        pause_button = pygame.image.load(os.path.join(os.path.dirname(__file__), 'img', 'pause.png')).convert_alpha()
        reset_button = pygame.image.load(os.path.join(os.path.dirname(__file__), 'img', 'reset.png')).convert_alpha()
        select_button = pygame.image.load(os.path.join(os.path.dirname(__file__), 'img', 'select.png')).convert_alpha()
        quit_button = pygame.image.load(os.path.join(os.path.dirname(__file__), 'img', 'quit.png')).convert_alpha()

        # Resize images to fit button size
        button_images = [
            pygame.transform.scale(pause_button, (40, 40)),
            pygame.transform.scale(reset_button, (40, 40)),
            pygame.transform.scale(select_button, (40, 40)),
            pygame.transform.scale(quit_button, (40, 40))
        ]

        # Button labels (key shortcuts)
        button_texts = ["Pause (P)", "Reset (R)", "SELECT (Esc)", "Quit (Q)"]

        # Draw button images and texts
        font = pygame.font.Font(None, 36)
        for i, (button_image, text) in enumerate(zip(button_images, button_texts)):
            y_offset = 220 + i * 60  # Adjust vertical spacing between buttons
            
            # Center icon and text in the same row
            icon_pos = (830, y_offset + 10)  # Icon position
            text_pos = (880, y_offset + 15)  # Text position, aligned with the icon vertically

            # Draw icon
            self.screen.blit(button_image, icon_pos)

            # Render and draw text
            button_text = font.render(text, True, self.BLACK)
            self.screen.blit(button_text, text_pos)

        # Add notification box for "Press SPACE for AI solves"
        notification_rect = pygame.Rect(820, 500, 260, 80)
        pygame.draw.rect(self.screen, self.DARK_GRAY, notification_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.WHITE, notification_rect.inflate(-6, -6), border_radius=10)

        notification_font = pygame.font.Font(None, 28)

        # Text for "Press SPACE for AI solves"
        ai_solve_text = notification_font.render("Press SPACE for AI solves", True, self.BLACK)
        ai_solve_rect = ai_solve_text.get_rect(center=(notification_rect.centerx, notification_rect.top + 20))
        self.screen.blit(ai_solve_text, ai_solve_rect)

        # Text for "Solve Time"
        solve_time_text = notification_font.render(f"Solve Time: {self.solve_time:.5f}s", True, self.GREEN)
        solve_time_rect = solve_time_text.get_rect(center=(notification_rect.centerx, notification_rect.top + 50))
        self.screen.blit(solve_time_text, solve_time_rect)

    #vẽ nút
    def draw_button(self, text, rect, color, hover=False):
        shadow_offset = 5
        pygame.draw.rect(self.screen, self.DARK_GRAY, rect.move(shadow_offset, shadow_offset), border_radius=10)
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        if hover:
            pygame.draw.rect(self.screen, self.LIGHT_GRAY, rect, 2, border_radius=10)
        font = pygame.font.Font(None, 30)
        label = font.render(text, True, self.WHITE)
        self.screen.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

    # # Vẽ map (Preview)  
    def draw_map_preview(self, map_data: List[str], preview_rect: pygame.Rect):
        """Vẽ bản xem trước của map Sokoban tại vị trí được chỉ định."""
        
        # Load hình ảnh nền cho bản đồ
        self.background_image = pygame.image.load(os.path.join('img', 'background.png'))
        
        # Điều chỉnh kích thước hình nền cho phù hợp với kích thước khu vực preview
        preview_width, preview_height = preview_rect.width, preview_rect.height
        self.background_image = pygame.transform.scale(self.background_image, (preview_width, preview_height))
        
        # Vẽ hình nền vào khu vực preview
        self.screen.blit(self.background_image, preview_rect.topleft)
        
        # Sau đó vẽ các phần tử của map
        self.wall_image = pygame.image.load(os.path.join('img', 'wall.png'))
        self.player_image = pygame.image.load(os.path.join('img', 'player.png'))
        self.block_image = pygame.image.load(os.path.join('img', 'box2.png'))
        self.target_image = pygame.image.load(os.path.join('img', 'target.png'))

        # Scale các hình ảnh để phù hợp với kích thước ô
        cell_width = preview_width // len(map_data[0])
        cell_height = preview_height // len(map_data)
        
        self.wall_image = pygame.transform.scale(self.wall_image, (cell_width, cell_height))
        self.player_image = pygame.transform.scale(self.player_image, (cell_width, cell_height))
        self.block_image = pygame.transform.scale(self.block_image, (cell_width, cell_height))
        self.target_image = pygame.transform.scale(self.target_image, (cell_width, cell_height))

        # Vẽ các phần tử map (tường, người chơi, hộp, mục tiêu)
        for row_index, row in enumerate(map_data):
            for col_index, cell in enumerate(row):
                rect = pygame.Rect(
                    preview_rect.x + col_index * cell_width,
                    preview_rect.y + row_index * cell_height,
                    cell_width, cell_height
                )
                if cell == 'W':
                    self.screen.blit(self.wall_image, rect.topleft)
                elif cell == 'P':
                    self.screen.blit(self.player_image, rect.topleft)
                elif cell == 'B':
                    self.screen.blit(self.block_image, rect.topleft)
                elif cell == 'T':
                    self.screen.blit(self.target_image, rect.topleft)


# # Vẽ phần chọn map   
    def map_selection_screen(self) -> Tuple[int, str]:
        current_map = 0
        preview_width, preview_height = 400, 300
        preview_x = (self.window_size[0] - preview_width) // 2
        preview_y = 150
        preview_rect = pygame.Rect(preview_x, preview_y, preview_width, preview_height)

        # Các nút chọn
        buttons = {
            'left': pygame.Rect(preview_x - 60, preview_y + preview_height // 2 - 25, 50, 50),
            'right': pygame.Rect(preview_x + preview_width + 10, preview_y + preview_height // 2 - 25, 50, 50),
            'select': pygame.Rect(self.window_size[0] // 2 - 50, preview_y + preview_height + 20, 100, 50),
            'algorithm': pygame.Rect(self.window_size[0] // 2 - 100, preview_y + preview_height + 80, 200, 50),
        }

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if buttons['left'].collidepoint(mouse_pos):
                        current_map = (current_map - 1) % len(self.maps)
                    elif buttons['right'].collidepoint(mouse_pos):
                        current_map = (current_map + 1) % len(self.maps)
                    elif buttons['select'].collidepoint(mouse_pos):
                        return current_map, self.current_algorithm
                    elif buttons['algorithm'].collidepoint(mouse_pos):
                        current_index = self.algorithms.index(self.current_algorithm)
                        next_index = (current_index + 1) % len(self.algorithms)
                        self.current_algorithm = self.algorithms[next_index]
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        current_map = (current_map - 1) % len(self.maps)
                    elif event.key == pygame.K_RIGHT:
                        current_map = (current_map + 1) % len(self.maps)
                    elif event.key in (pygame.K_UP, pygame.K_DOWN):
                        current_index = self.algorithms.index(self.current_algorithm)
                        next_index = (current_index + 1) % len(self.algorithms)
                        self.current_algorithm = self.algorithms[next_index]
                    elif event.key == pygame.K_RETURN:
                        return current_map, self.current_algorithm
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                self.screen.fill(self.DARK_GRAY)
                font = pygame.font.Font(None, 40)
                title = font.render(f"Select a Map ({current_map + 1}/{len(self.maps)})", True, self.WHITE)
                self.screen.blit(title, (self.window_size[0] // 2 - title.get_width() // 2, 50))

                # Hiển thị preview map
                pygame.draw.rect(self.screen, self.BLACK, preview_rect.inflate(4, 4), 2)
                self.draw_map_preview(self.maps[current_map], preview_rect)

                # Vẽ các nút
                self.draw_button("<", buttons['left'], self.BLUE, True)
                self.draw_button(">", buttons['right'], self.BLUE, True)
                self.draw_button("Select", buttons['select'], self.DARK_BLUE, True)
                self.draw_button(f"{self.current_algorithm.upper()}", buttons['algorithm'], self.DARK_BLUE, True)

                pygame.display.flip()

#Update hướng di chuyển
    def update_player_direction(self, move):
        if move == (-1, 0):
            self.player_direction = 'left'
        elif move == (1, 0):
            self.player_direction = 'right'
        elif move == (0, -1):
            self.player_direction = 'up'
        elif move == (0, 1):
            self.player_direction = 'down'

    # Hoạt ảnh giải pháp
    def animate_solution(self, initial_state: SokobanState, solution: List[Tuple[int, int]]):
        """Hiển thị hoạt ảnh giải pháp tự động cho map Sokoban.

        Chức năng:
        - Thực thi các bước di chuyển từ giải pháp đã cho
        - Cập nhật trạng thái game và vẽ lại màn hình sau mỗi bước
        - Xử lý sự kiện thoát game
        - Kiểm tra điều kiện hoàn thành level

        Arguments:
            initial_state (SokobanState): Trạng thái ban đầu của map
            solution (List[Tuple[int, int]]): Danh sách các bước di chuyển

        Returns:
            str: Trạng thái kết quả ("COMPLETE" nếu giải quyết thành công)

        Các bước thực hiện:
        - Lặp qua từng bước di chuyển
        - Cập nhật hướng người chơi
        - Vẽ lại map sau mỗi bước
        - Tạo độ trễ giữa các bước để tạo hiệu ứng động
        - Kiểm tra điều kiện hoàn thành level
        """
        current_state = initial_state
        for move in solution:
            self.solve_steps += 1
            self.player_moves_by_space.append(move)
            self.player_moves.append(move)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.update_player_direction(move)  
            current_state = current_state.apply_move(move)
            self.game_time = time.time() - self.start_time - self.pause_time
            self.draw_maze(current_state.maze, list(current_state.boxes), list(current_state.targets))
            player_pos = (current_state.player_pos[0] * self.cell_size, 
                        current_state.player_pos[1] * self.cell_size)
            self.screen.blit(self.images[self.player_direction], player_pos)
            font = pygame.font.Font(None, 36)                
            pygame.display.flip()
            pygame.time.wait(100)
            if current_state.is_goal():
                self.handle_level_complete()
                return "COMPLETE"
                
    # Hành động hoàn thành trò chơi
    def handle_level_complete(self):
        font = pygame.font.Font(None, 74)
        text = font.render('Level Complete!', True, self.GREEN)
        self.screen.blit(text, (200, 250))
        
        current_map = self.maps.index(self.current_map)
   
        self.save_solution(current_map)
        self.sort_solutions(current_map)

        instruction_font = pygame.font.Font(None, 36)
        instruction_text = instruction_font.render('Press SPACE to restart', True, self.WHITE)
        self.screen.blit(instruction_text, (270, 350))
        
        pygame.display.flip()

    # Dừng thời gian
    def toggle_pause(self):
        if self.is_paused:
            self.start_time += time.time() - self.pause_start_time
        else:
            self.pause_start_time = time.time()
        self.is_paused = not self.is_paused

    # Sự kiện click chuột
    def handle_mouse_click(self, pos: Tuple[int, int], first_move: bool) -> Optional[str]:
        if 820 <= pos[0] <= 1080:
            if 220 <= pos[1] <= 270:  # Pause button
                if first_move:
                    self.is_paused = not self.is_paused
                else:
                    self.toggle_pause()
            elif 280 <= pos[1] <= 330:  # Reset button
                return "RESET"
            elif 340 <= pos[1] <= 390:  # Select button
                return "SELECT"
            elif 400 <= pos[1] <= 450:  # Quit button
                return "QUIT"
        return None
      
    # Sự kiện nhấn nút
    def handle_key_press(self, event: pygame.event.Event, current_state: SokobanState, first_move: bool) -> Tuple[Optional[str], SokobanState, bool]:
        if event.key == pygame.K_r:
            # Reset lại màn chơi
            return "RESET", current_state, first_move
        elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
            # Quay lại màn hình chọn map
            return "SELECT", current_state, first_move
        elif event.key == pygame.K_p:
            # Tạm dừng hoặc tiếp tục trò chơi
            self.toggle_pause()
            return None, current_state, first_move
        elif event.key == pygame.K_SPACE:
            # AI giải đố
            self.player_moves_by_space = []
            result = self.handle_solution(current_state)
            if result == "COMPLETE":
                return "COMPLETE", current_state, first_move
            return None, current_state, first_move

        # Xử lý di chuyển khi không ở chế độ tạm dừng và không phải bước đầu tiên
        if not self.is_paused and not first_move:
            new_state, moved = self.move_player(event.key, current_state)
            if moved:
                self.solve_steps += 1
                return None, new_state, first_move
        return None, current_state, first_move
    
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        
    def draw_pause_message(self):
        if self.is_paused:
            pause_text = self.FONT.render("Game Paused", True, self.RED)
            pause_rect = pause_text.get_rect(center=(self.window_size[0] // 2, self.window_size[1] // 2))
            self.screen.blit(pause_text, pause_rect)

    # Di chuyển nhân vật
    def move_player(self, key: int, current_state: SokobanState) -> Tuple[SokobanState, bool]:
        direction = {
            pygame.K_LEFT: (-1, 0, 'left'),
            pygame.K_RIGHT: (1, 0, 'right'),
            pygame.K_UP: (0, -1, 'up'),
            pygame.K_DOWN: (0, 1, 'down')
        }.get(key)
        
        if not direction:
            return current_state, False

        dx, dy, new_direction = direction
        new_x = current_state.player_pos[0] + dx
        new_y = current_state.player_pos[1] + dy
        
        if not (0 <= new_x < len(current_state.maze[0]) and 
                0 <= new_y < len(current_state.maze) and
                current_state.maze[new_y][new_x] != 1):
            return current_state, False

        new_boxes = set(current_state.boxes)
        
        if (new_x, new_y) in current_state.boxes:
            box_new_x = new_x + dx
            box_new_y = new_y + dy
            
            if not (0 <= box_new_x < len(current_state.maze[0]) and 
                    0 <= box_new_y < len(current_state.maze) and
                    current_state.maze[box_new_y][box_new_x] != 1 and
                    (box_new_x, box_new_y) not in current_state.boxes):
                return current_state, False
            
            new_boxes.remove((new_x, new_y))
            new_boxes.add((box_new_x, box_new_y))
        
        self.player_direction = new_direction  # Cập nhật hướng của nhân vật
        self.player_moves.append((dx, dy))
        return SokobanState(
            current_state.maze,
            (new_x, new_y),
            frozenset(new_boxes),
            current_state.targets,
            current_state._zone_map,
            current_state._deadlock_cache
        ), True
    
    # Giới hạn thời gian tìm kiếm
    def solve_with_timeout(self, solver_func, *args):
        solution = [None]
        def target():
            solution[0] = solver_func(*args)
        
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(30)  # Đợi tối đa 30 giây
        
        if thread.is_alive():
            # Nếu thread vẫn đang chạy sau 30 giây
            return None
        return solution[0]
    
    # Tìm kếm giải pháp
    def handle_solution(self, current_state: SokobanState) -> Optional[str]:
        solve_start_time = time.time()
        font = pygame.font.Font(None, 74)
        text = font.render('Solving ...', True, self.WHITE)
        self.screen.blit(text, (300, 250))
        pygame.display.flip()
        if self.current_algorithm == 'astar':
            solution = self.solve_with_timeout(solve_sokoban_astar, current_state.maze, current_state.player_pos,
                                               list(current_state.boxes), list(current_state.targets))
        elif self.current_algorithm == 'hillclimbing':
            solution = self.solve_with_timeout(solve_sokoban_hillclimbing, current_state.maze, current_state.player_pos,
                                               list(current_state.boxes), list(current_state.targets))
        elif self.current_algorithm == 'bfs':
            solution = self.solve_with_timeout(solve_sokoban_bfs, current_state.maze, current_state.player_pos,
                                               list(current_state.boxes), list(current_state.targets))
        
        self.solve_time = time.time() - solve_start_time
        
        if solution:
            self.start_time = time.time()
            for move in solution:
                self.update_player_direction(move)  # Cập nhật hướng của nhân vật cho mỗi bước di chuyển
            result = self.animate_solution(current_state, solution)
            if result == "COMPLETE":
                return "COMPLETE"
        else:
            current_map = self.maps.index(self.current_map)
            file_solutions = self.read_solutions(current_map)
            for file_solution in file_solutions:
                parsed_solution = self.parse_solution(file_solution) 
                if self.is_valid_solution(current_state,parsed_solution):
                    self.start_time = time.time()
                    for move in parsed_solution:
                        self.update_player_direction(move)
                    result = self.animate_solution(current_state, parsed_solution)
                    if result == "COMPLETE":
                        return "COMPLETE"
            self.handle_no_solution(current_state)
        return None
    
    # Kiểm tra khả năng giải
    def is_valid_solution(self, state: SokobanState, solution: List[Tuple[int, int]]) -> bool:
        for move in solution:
            new_state = state.apply_move(move)
            if new_state == state:  # Nếu trạng thái không thay đổi thì động thái đó không có hiệu lực
                return False
            state = new_state
        return state.is_goal()
    
    # Hành động không hoàn thành trò chơi
    def handle_no_solution(self, current_state: SokobanState):
        self.game_time = 0
        self.draw_maze(current_state.maze, list(current_state.boxes), list(current_state.targets))
        player_pos = (current_state.player_pos[0] * self.cell_size, 
                     current_state.player_pos[1] * self.cell_size)
        self.screen.blit(self.images['player'], player_pos)
        font = pygame.font.Font(None, 74)
        text = font.render('No solution found!', True, self.RED)
        self.screen.blit(text, (300, 250))
        pygame.display.flip()
        pygame.time.wait(2000)

    # Cập nhật hình của màn chơi
    def update_game_state(self, current_state: SokobanState, first_move: bool):
        if not self.is_paused:
            self.draw_maze(current_state.maze, list(current_state.boxes), list(current_state.targets))
            player_pos = (current_state.player_pos[0] * self.cell_size, 
                        current_state.player_pos[1] * self.cell_size)
            self.screen.blit(self.images[self.player_direction], player_pos)
            
            if current_state.is_goal():
                self.handle_level_complete()
                return "COMPLETE"
            
            if not first_move:
                self.game_time = time.time() - self.start_time - self.pause_time
        else:
            font = pygame.font.Font(None, 74)
            text = font.render('PAUSED', True, self.WHITE)
            text_rect = text.get_rect(center=(self.window_size[0] // 2, self.window_size[1] // 2))
            self.screen.blit(text, text_rect)
        return None

    def play_game(self, initial_state: SokobanState) -> str:
        current_state = initial_state
        clock = pygame.time.Clock()
        first_move = True
        result = None

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        result = self.handle_mouse_click(event.pos, first_move)
                        if result:
                            return result
                elif event.type == pygame.KEYDOWN:
                      # Xử lý di chuyển đầu tiên
                    if first_move and event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                        self.start_time = time.time()
                        first_move = False
                    
                     # Loại bỏ điều kiện first_move để các phím khác luôn được xử lý
                    result, current_state, first_move = self.handle_key_press(event, current_state, first_move)
                    if result:
                        return result

            result = self.update_game_state(current_state, first_move)
            if result:
                return result

            pygame.display.flip()
            clock.tick(60)

    def run(self):
        while True:
            selected_map, algorithm = self.map_selection_screen()
            self.current_map = self.maps[selected_map]
            maze, player_pos, boxes, targets = self.map_to_game_state(self.current_map)
            initial_state = SokobanState(tuple(tuple(row) for row in maze), player_pos, frozenset(boxes), frozenset(targets))

            font = pygame.font.Font(None, 36)
            text = font.render('Press SPACE to solve automatically', True, self.BLACK)
            self.screen.blit(text, (330, 100))
            pygame.display.flip()
            pygame.time.wait(100)

            self.game_time = 0
            self.start_time = None
            self.pause_time = 0
            self.is_paused = False
            self.solve_steps = 0
            self.player_moves = []
            self.player_moves_by_space = []

            while True:
                result = self.play_game(initial_state)
                if result == "QUIT":
                    pygame.quit()
                    sys.exit()
                elif result == "RESET":
                    current_algorithm = self.current_algorithm
                    self.__init__()
                    self.current_algorithm = current_algorithm
                    pygame.display.flip()
                elif result == "SELECT":
                    break
                elif result == "COMPLETE":
                    waiting_for_input = True
                    while waiting_for_input:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_SPACE:
                                    current_algorithm = self.current_algorithm
                                    self.__init__()
                                    self.current_algorithm = current_algorithm
                                    waiting_for_input = False
                                    break

if __name__ == "__main__":
    game = SokobanGame()
    game.run()