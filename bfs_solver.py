import time
import sys
import csv
from typing import FrozenSet, List, Tuple, Optional, Set
from sokoban_common import SokobanState, MOVES
from collections import deque
from pympler import asizeof

class BFSSolver:
    def __init__(self, max_iterations: int = 1000000, csv_file: str = 'results.csv'):
        """
        Khởi tạo bộ giải BFS.
        
        Arguments:
        max_iterations (int): Số vòng lặp tối đa để tìm kiếm.
        csv_file (str): Đường dẫn tệp CSV lưu kết quả.
        """
        self.max_iterations = max_iterations
        self.csv_file = csv_file
        self._initialize_csv()

    def _initialize_csv(self):
        """
        Khởi tạo tệp CSV với tiêu đề nếu tệp không tồn tại hoặc trống.
        
        Nếu tệp CSV không tồn tại, phương thức sẽ tạo tệp mới và ghi tiêu đề cột.
        Nếu tệp đã tồn tại, chỉ thêm tiêu đề nếu tệp trống.
        """
        try:
            with open(self.csv_file, mode='a', newline='') as file:  # Chế độ 'a' cho phép thêm vào file nếu nó tồn tại
                if file.tell() == 0:  # Kiểm tra nếu file trống
                    writer = csv.writer(file)
                    writer.writerow([f"{'Algorithm':<15}"  # Căn chỉnh 'Algorithm' sang trái với độ rộng 15
                                    f"{'Storage (MB)':>10}"  # Căn chỉnh 'Storage (MB)' sang phải với độ rộng 10
                                    f"{'States Visited':>15}"  # Căn chỉnh 'States Visited' sang phải với độ rộng 15
                                    f"{'Time (s)':>10}"])  # Căn chỉnh 'Time (s)' sang phải với độ rộng 10
        except FileNotFoundError:
            with open(self.csv_file, mode='w', newline='') as file:  # Chế độ 'w' để tạo mới file và ghi tiêu đề
                writer = csv.writer(file)
                writer.writerow([f"{'Algorithm':<15}"  # Căn chỉnh 'Algorithm' sang trái với độ rộng 15
                                f"{'Storage (MB)':>10}"  # Căn chỉnh 'Storage (MB)' sang phải với độ rộng 10
                                f"{'States Visited':>15}"  # Căn chỉnh 'States Visited' sang phải với độ rộng 15
                                f"{'Time (s)':>10}"])  # Căn chỉnh 'Time (s)' sang phải với độ rộng 10


    def solve(self, initial_state: SokobanState) -> Optional[List[Tuple[int, int]]]:
        """
        Giải bài toán Sokoban bằng thuật toán BFS.
        
        Arguments:
        initial_state (SokobanState): Trạng thái ban đầu của trò chơi.
        
        Returns:
        Optional[List[Tuple[int, int]]]: Một danh sách các bước di chuyển, hoặc None nếu không tìm được lời giải.
        """
        
        # Tạo hàng đợi (queue) để lưu trữ các trạng thái và đường đi
        queue = deque([(initial_state, [])])
        visited = set()  # Lưu trữ các trạng thái đã thăm

        # Bắt đầu tính thời gian
        start_time = time.time()

        # Vòng lặp chính của thuật toán BFS
        for iteration in range(self.max_iterations):
            if not queue:
                # Nếu hàng đợi trống, không có giải pháp
                return None
            
            # Lấy phần tử đầu tiên trong hàng đợi (FIFO)
            current_state, path = queue.popleft()

            # Kiểm tra nếu trạng thái hiện tại là trạng thái mục tiêu
            if current_state.is_goal():
                end_time = time.time()
                # Ghi kết quả vào file CSV
                self._log_results('BFS', iteration, visited, start_time, end_time)
                # Trả về đường đi từ trạng thái ban đầu đến mục tiêu
                return path

            # Chuyển trạng thái hiện tại thành một giá trị có thể so sánh (hashable)
            state_hash = self.state_to_hashable(current_state)
            if state_hash in visited:
                # Nếu trạng thái đã được thăm, bỏ qua
                continue
            
            # Đánh dấu trạng thái hiện tại là đã thăm
            visited.add(state_hash)

            # Lấy các trạng thái kế tiếp từ trạng thái hiện tại
            for move in MOVES:
                next_state = current_state.apply_move(move)
                if next_state != current_state:
                    # Nếu trạng thái kế tiếp khác trạng thái hiện tại, thêm vào hàng đợi
                    queue.append((next_state, path + [move]))

        # Nếu không tìm được lời giải sau max_iterations, ghi kết quả và trả về None
        end_time = time.time()
        self._log_results('BFS', iteration, visited, start_time, end_time)
        return None

    @staticmethod
    def state_to_hashable(state: SokobanState) -> Tuple[Tuple[int, int], FrozenSet[Tuple[int, int]]]:
        """
        Chuyển trạng thái của trò chơi thành một kiểu có thể so sánh được để sử dụng trong tập đã thăm.
        
        Arguments:
        state (SokobanState): Trạng thái của trò chơi cần chuyển đổi.
        
        Returns:
        Tuple[Tuple[int, int], FrozenSet[Tuple[int, int]]]: Trạng thái đã được chuyển thành một tuple.
        """
        return (state.player_pos, state.boxes)

    def _log_results(self, algorithm: str, iteration: int, state: SokobanState, start_time: float, end_time: float):
        """
        Ghi kết quả giải thuật vào tệp CSV.

        Arguments:
            algorithm (str): Tên thuật toán.
            iteration (int): Số lần lặp.
            state (SokobanState): Trạng thái cuối cùng của bài toán.
            start_time (float): Thời điểm bắt đầu.
            end_time (float): Thời điểm kết thúc.
        """
        # Sử dụng pympler để đo bộ nhớ của đối tượng state và các đối tượng con
        storage_used = asizeof.asizeof(state) / (1024 * 1024)  # Chuyển sang MB
        states_visited = iteration
        elapsed_time = end_time - start_time

        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([f"{algorithm:<15}"
                            f"{storage_used:>10.2f}"
                            f"{states_visited:>15}"
                            f"{elapsed_time:>10.4f}"])

def solve_sokoban_bfs(maze: List[List[int]], 
                      player_pos: Tuple[int, int],
                      boxes: List[Tuple[int, int]], 
                      targets: List[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
    """
    Giải bài toán Sokoban bằng thuật toán BFS.
    
    Arguments:
    maze (List[List[int]]): Ma trận của mê cung.
    player_pos (Tuple[int, int]): Vị trí ban đầu của người chơi.
    boxes (List[Tuple[int, int]]): Danh sách các hộp trong trò chơi.
    targets (List[Tuple[int, int]]): Danh sách các vị trí mục tiêu của hộp.
    
    Returns:
    Optional[List[Tuple[int, int]]]: Một danh sách các bước di chuyển, hoặc None nếu không tìm được lời giải.
    """
    initial_state = SokobanState(tuple(tuple(row) for row in maze), player_pos, frozenset(boxes), frozenset(targets))
    solver = BFSSolver(csv_file='results.csv')  # Chỉ định tệp CSV
    return solver.solve(initial_state)
