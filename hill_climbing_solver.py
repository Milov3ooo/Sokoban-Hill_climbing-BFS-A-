import random
import time
import sys
import csv
from typing import List, Tuple, Optional
from sokoban_common import SokobanState, MOVES

class HillClimbingSolver:
    """
    Giải quyết bài toán Sokoban sử dụng thuật toán leo đồi (Hill Climbing).

    Thuật toán này tìm kiếm lời giải bằng cách di chuyển tới các trạng thái 'tốt hơn' 
    dựa trên một hàm đánh giá, với khả năng khắc phục vấn đề kẹt tại điểm cực đại địa phương.

    Attributes:
        max_iterations (int): Số lần lặp tối đa để tìm kiếm lời giải.
        max_sideways (int): Số lần di chuyển ngang (không cải thiện) được phép.
        csv_file (str): Đường dẫn file CSV để ghi kết quả thực thi.
    """
    def __init__(self, max_iterations: int = 1000, max_sideways: int = 100, csv_file: str = 'results.csv'):
        """
        Khởi tạo bộ giải Hill Climbing.

        Arguments:
            max_iterations (int): Số lần lặp tối đa. Mặc định là 1000.
            max_sideways (int): Số lần di chuyển ngang được phép. Mặc định là 100.
            csv_file (str): Đường dẫn file CSV ghi kết quả. Mặc định là 'results.csv'.
        """
        self.max_iterations = max_iterations
        self.max_sideways = max_sideways
        self.csv_file = csv_file
        self._initialize_csv()  # Khởi tạo file CSV khi tạo đối tượng

    def _initialize_csv(self):
        """
        Khởi tạo file CSV với các tiêu đề cột, đảm bảo không ghi đè dữ liệu hiện có.
        """
        try:
            # Mở file ở chế độ thêm, không ghi đè
            with open(self.csv_file, mode='a', newline='') as file:
                if file.tell() == 0:  # Kiểm tra nếu file trống
                    writer = csv.writer(file)
                    # Tiêu đề cột được căn chỉnh để dễ đọc
                    writer.writerow([f"{'Algorithm':<15}"   # Tên thuật toán
                                     f"{'Storage (MB)':>10}"  # Bộ nhớ sử dụng
                                     f"{'States Visited':>15}"  # Số trạng thái đã duyệt
                                     f"{'Time (s)':>10}"])  # Thời gian thực thi
        except FileNotFoundError:
            # Nếu file không tồn tại, tạo mới và ghi tiêu đề
            with open(self.csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([f"{'Algorithm':<15}"
                                 f"{'Storage (MB)':>10}"
                                 f"{'States Visited':>15}"
                                 f"{'Time (s)':>10}"])

    def solve(self, initial_state: SokobanState) -> Optional[List[Tuple[int, int]]]:
        """
        Giải quyết bài toán Sokoban bằng thuật toán leo đồi.

        Arguments:
            initial_state (SokobanState): Trạng thái ban đầu của bản đồ Sokoban.

        Returns:
            Optional[List[Tuple[int, int]]]: Danh sách các nước đi để giải bài toán, 
            hoặc None nếu không tìm được lời giải.
        """
        
        # Khởi tạo trạng thái hiện tại và đánh giá điểm số ban đầu
        current_state = initial_state
        current_score = self.evaluate_state(current_state)
        path = []

        # Bắt đầu tính thời gian
        start_time = time.time()

        # Vòng lặp chính của thuật toán leo đồi
        for iteration in range(self.max_iterations):
            # Kiểm tra nếu trạng thái hiện tại đã đạt được trạng thái mục tiêu
            if current_state.is_goal():
                # Nếu là trạng thái mục tiêu, ghi kết quả và trả về các bước đi đã thực hiện
                end_time = time.time()
                self._log_results('Hill Climbing', iteration, current_state, start_time, end_time)
                return path

            # Lấy danh sách các trạng thái kế tiếp từ trạng thái hiện tại
            neighbors = self.get_neighbors(current_state)
            if not neighbors:
                # Nếu không có hàng xóm (trạng thái kế tiếp) nào, trả về None (không có giải pháp)
                return None

            # Lọc ra các trạng thái có điểm số (evaluation score) tốt hơn trạng thái hiện tại
            better_neighbors = [(neighbor, move) for neighbor, move in neighbors if self.evaluate_state(neighbor) > current_score]

            if better_neighbors:
                # Nếu có trạng thái nào tốt hơn, chọn ngẫu nhiên một trạng thái tốt nhất
                best_neighbor = random.choice(better_neighbors)
            else:
                # Nếu không có trạng thái nào tốt hơn, lọc các trạng thái có điểm số bằng điểm số hiện tại
                best_neighbors = [(neighbor, move) for neighbor, move in neighbors if self.evaluate_state(neighbor) == current_score]
                if best_neighbors:
                    # Nếu có trạng thái nào có điểm số bằng, chọn ngẫu nhiên một trạng thái tốt nhất
                    best_neighbor = random.choice(best_neighbors)
                else:
                    # Nếu không có hàng xóm nào, reset trạng thái về trạng thái ngẫu nhiên
                    current_state = self.get_random_state(initial_state)
                    current_score = self.evaluate_state(current_state)
                    path = []
                    continue

            # Cập nhật trạng thái hiện tại và điểm số của nó
            current_state = best_neighbor[0]
            current_score = self.evaluate_state(current_state)
            # Thêm nước đi vào đường đi (path)
            path.append(best_neighbor[1])

        # Nếu không tìm được lời giải sau các vòng lặp, ghi kết quả và trả về None
        end_time = time.time()
        self._log_results('Hill Climbing', iteration, current_state, start_time, end_time)
        return None


    def evaluate_state(self, state: SokobanState) -> float:
        """
        Đánh giá chất lượng của một trạng thái Sokoban.

        Arguments:
            state (SokobanState): Trạng thái cần đánh giá.

        Returns:
            float: Điểm số của trạng thái. Điểm càng cao, trạng thái càng gần đích.
        """
        if state.is_goal():
            return float('inf')  # Trạng thái đích có điểm vô cùng

        score = 0
        for box in state.boxes:
            # Tìm khoảng cách ngắn nhất từ hộp tới các mục tiêu
            min_distance = min(abs(box[0] - target[0]) + abs(box[1] - target[1]) for target in state.targets)
            score -= min_distance  # Điểm số giảm khi khoảng cách tới mục tiêu xa

        return score

    def get_neighbors(self, state: SokobanState) -> List[Tuple[SokobanState, Tuple[int, int]]]:
        """
        Sinh ra các trạng thái liền kề từ trạng thái hiện tại.

        Arguments:
            state (SokobanState): Trạng thái ban đầu.

        Returns:
            List[Tuple[SokobanState, Tuple[int, int]]]: Danh sách các trạng thái mới và nước đi tương ứng.
        """
        neighbors = []
        for move in MOVES:
            new_state = state.apply_move(move)
            if new_state != state:
                neighbors.append((new_state, move))
        return neighbors

    def get_random_state(self, initial_state: SokobanState) -> SokobanState:
        """
        Tạo ra một trạng thái ngẫu nhiên từ trạng thái ban đầu để tránh kẹt tại điểm cực đại địa phương.

        Arguments:
            initial_state (SokobanState): Trạng thái ban đầu.

        Returns:
            SokobanState: Trạng thái ngẫu nhiên.
        """
        current_state = initial_state
        for _ in range(random.randint(1, 20)):
            neighbors = self.get_neighbors(current_state)
            if neighbors:
                current_state = random.choice(neighbors)[0]
            else:
                break
        return current_state

    def _log_results(self, algorithm: str, iteration: int, state: SokobanState, start_time: float, end_time: float):
        """
        Ghi lại kết quả thực thi của thuật toán vào file CSV.

        Arguments:
            algorithm (str): Tên thuật toán.
            iteration (int): Số lần lặp.
            state (SokobanState): Trạng thái cuối cùng.
            start_time (float): Thời điểm bắt đầu.
            end_time (float): Thời điểm kết thúc.
        """
        # Tính toán bộ nhớ và thời gian
        storage_used = sys.getsizeof(state) / (1024 * 1024)  # Chuyển sang MB
        states_visited = iteration
        elapsed_time = end_time - start_time

        # Mở file CSV để ghi kết quả
        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Ghi dữ liệu với định dạng căn chỉnh
            writer.writerow([f"{algorithm:<15}"  
                             f"{storage_used:>10.2f}"
                             f"{states_visited:>15}"
                             f"{elapsed_time:>10.4f}"])


def solve_sokoban_hillclimbing(maze: List[List[int]], 
                               player_pos: Tuple[int, int],
                               boxes: List[Tuple[int, int]], 
                               targets: List[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
    """
    Hàm chính để giải bài toán Sokoban bằng thuật toán leo đồi.

    Arguments:
        maze (List[List[int]]): Bản đồ Sokoban dưới dạng ma trận.
        player_pos (Tuple[int, int]): Vị trí ban đầu của người chơi.
        boxes (List[Tuple[int, int]]): Danh sách vị trí các hộp.
        targets (List[Tuple[int, int]]): Danh sách các vị trí đích.

    Returns:
        Optional[List[Tuple[int, int]]]: Danh sách các nước đi để giải bài toán, 
        hoặc None nếu không tìm được lời giải.
    """
    initial_state = SokobanState(tuple(tuple(row) for row in maze), player_pos, frozenset(boxes), frozenset(targets))
    solver = HillClimbingSolver(csv_file='results.csv')
    return solver.solve(initial_state)
