import heapq
import time
import sys
import csv
from typing import List, Tuple, Optional, FrozenSet
from sokoban_common import SokobanState, MOVES
from pympler import asizeof

class AStarSolver:
    """
    Lớp giải quyết bài toán Sokoban sử dụng thuật toán A*.
    
    Thuật toán A* được sử dụng để tìm đường đi ngắn nhất trong trò chơi Sokoban, 
    có tính đến các ràng buộc và trạng thái của các hộp.

    Attributes:
        max_iterations (int): Số lần lặp tối đa để tìm giải pháp.
        csv_file (str): Đường dẫn tới tệp CSV để ghi kết quả.
    """
    def __init__(self, max_iterations: int = 1000000, csv_file: str = 'results.csv'):
        """
        Khởi tạo bộ giải A* Sokoban.

        Arguments:
            max_iterations (int): Số lần lặp tối đa để tìm giải pháp. Mặc định là 1.000.000.
            csv_file (str): Tên tệp CSV để lưu kết quả. Mặc định là 'results.csv'.
        """
        self.max_iterations = max_iterations
        self.csv_file = csv_file
        self._initialize_csv()  # Khởi tạo tệp CSV khi tạo đối tượng

    def _initialize_csv(self):
        """
        Khởi tạo tệp CSV, thêm tiêu đề nếu tệp trống hoặc chưa tồn tại.
        
        Chức năng này đảm bảo tệp CSV luôn có tiêu đề được định dạng đúng.
        """
        try:
            # Mở file ở chế độ nối thêm để tránh ghi đè
            with open(self.csv_file, mode='a', newline='') as file:
                if file.tell() == 0:  # Kiểm tra nếu file trống
                    writer = csv.writer(file)
                    # Viết tiêu đề với căn chỉnh phù hợp
                    writer.writerow([f"{'Algorithm':<15}"
                                    f"{'Storage (MB)':>10}"
                                    f"{'States Visited':>15}"
                                    f"{'Time (s)':>10}"])
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
        Giải quyết bài toán Sokoban bằng thuật toán A*.

        Arguments:
            initial_state (SokobanState): Trạng thái ban đầu của bản đồ Sokoban.

        Returns:
            Optional[List[Tuple[int, int]]]: Danh sách các nước đi để giải quyết bài toán,
            hoặc None nếu không tìm thấy giải pháp.
        """
        
        # Khởi tạo điểm xuất phát cho thuật toán A*
        start_node = (initial_state.heuristic(), 0, [], initial_state)
        # frontier: hàng đợi ưu tiên (min-heap) lưu trữ các trạng thái cần kiểm tra, theo thứ tự chi phí thấp nhất
        frontier = [start_node]
        # explored: tập trạng thái đã được kiểm tra
        explored = set()
        # deadlock_cache: bộ nhớ lưu trữ các trạng thái đã xác định là deadlock (bế tắc)
        deadlock_cache = {}

        # Thời gian bắt đầu
        start_time = time.time()

        # Vòng lặp chính của thuật toán A*
        for iteration in range(self.max_iterations):
            # Nếu frontier trống, tức là không còn trạng thái nào để kiểm tra, trả về None
            if not frontier:
                return None

            # Lấy phần tử có chi phí thấp nhất từ frontier
            _, cost, path, current_state = heapq.heappop(frontier)

            # Kiểm tra xem trạng thái hiện tại có phải là trạng thái mục tiêu không
            if current_state.is_goal():
                # Nếu là mục tiêu, tính toán thời gian kết thúc và trả về các nước đi
                end_time = time.time()
                self._log_results('A*', iteration, current_state, start_time, end_time)
                return path

            # Chuyển trạng thái hiện tại thành dạng có thể so sánh (hashable) để kiểm tra đã thăm chưa
            state_hash = self.state_to_hashable(current_state)
            # Nếu trạng thái đã được thăm, bỏ qua
            if state_hash in explored:
                continue
            # Thêm trạng thái hiện tại vào tập explored
            explored.add(state_hash)

            # Duyệt qua tất cả các nước đi có thể có
            for move in MOVES:
                # Áp dụng nước đi và tạo ra trạng thái tiếp theo
                next_state = current_state.apply_move(move)
                # Nếu trạng thái tiếp theo khác với trạng thái hiện tại và không bị deadlock
                if next_state != current_state and not self.is_deadlock(next_state, deadlock_cache):
                    # Tính toán chi phí mới và heuristic cho trạng thái tiếp theo
                    next_cost = cost + 1
                    next_heuristic = next_state.heuristic()
                    # Tạo một node mới cho trạng thái tiếp theo và thêm vào frontier
                    next_node = (next_cost + next_heuristic, next_cost, path + [move], next_state)
                    heapq.heappush(frontier, next_node)

        # Nếu không tìm thấy giải pháp sau khi kiểm tra hết các trạng thái, tính toán thời gian kết thúc và trả về None
        end_time = time.time()
        self._log_results('A*', iteration, current_state, start_time, end_time)
        return None


    @staticmethod
    def state_to_hashable(state: SokobanState) -> Tuple[Tuple[int, int], FrozenSet[Tuple[int, int]]]:
        """
        Chuyển trạng thái Sokoban thành một dạng có thể băm được.

        Arguments:
            state (SokobanState): Trạng thái cần chuyển đổi.

        Returns:
            Tuple chứa vị trí người chơi và vị trí các hộp.
        """
        return (state.player_pos, state.boxes)

    def is_deadlock(self, state: SokobanState, deadlock_cache: dict) -> bool:
        """
        Kiểm tra xem trạng thái hiện tại có phải là bế tắc không.

        Arguments:
            state (SokobanState): Trạng thái cần kiểm tra.
            deadlock_cache (dict): Bộ nhớ đệm để lưu trữ các trạng thái bế tắc.

        Returns:
            bool: True nếu là bế tắc, False nếu ngược lại.
        """
        state_hash = self.state_to_hashable(state)
        if state_hash in deadlock_cache:
            return deadlock_cache[state_hash]

        is_deadlock = self.check_deadlock(state)
        deadlock_cache[state_hash] = is_deadlock
        return is_deadlock

    def check_deadlock(self, state: SokobanState) -> bool:
        """
        Kiểm tra xem có hộp nào ở trạng thái bế tắc không.

        Arguments:
            state (SokobanState): Trạng thái cần kiểm tra.

        Returns:
            bool: True nếu có hộp bị bế tắc, False nếu ngược lại.
        """
        for box in state.boxes:
            if self.is_corner_deadlock(state, box):
                return True
        return False

    def is_corner_deadlock(self, state: SokobanState, box: Tuple[int, int]) -> bool:
        """
        Kiểm tra xem hộp có ở trạng thái bế tắc góc không.

        Arguments:
            state (SokobanState): Trạng thái của bản đồ.
            box (Tuple[int, int]): Vị trí của hộp cần kiểm tra.

        Returns:
            bool: True nếu hộp bị kẹt ở góc, False nếu ngược lại.
        """
        x, y = box
        if box in state.targets:
            return False
        
        walls = [
            (state.maze[y-1][x] == 1 and state.maze[y][x-1] == 1),  # Góc trên trái
            (state.maze[y-1][x] == 1 and state.maze[y][x+1] == 1),  # Góc trên phải
            (state.maze[y+1][x] == 1 and state.maze[y][x-1] == 1),  # Góc dưới trái
            (state.maze[y+1][x] == 1 and state.maze[y][x+1] == 1)   # Góc dưới phải
        ]
        
        return any(walls)

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

def solve_sokoban_astar(maze: List[List[int]], 
                        player_pos: Tuple[int, int],
                        boxes: List[Tuple[int, int]], 
                        targets: List[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
    """
    Hàm giải quyết bài toán Sokoban sử dụng thuật toán A*.

    Arguments:
        maze (List[List[int]]): Bản đồ trò chơi, với 1 là tường, 0 là ô trống.
        player_pos (Tuple[int, int]): Vị trí ban đầu của người chơi.
        boxes (List[Tuple[int, int]]): Danh sách vị trí các hộp.
        targets (List[Tuple[int, int]]): Danh sách vị trí đích của các hộp.

    Returns:
        Optional[List[Tuple[int, int]]]: Danh sách các nước đi để giải quyết bài toán,
        hoặc None nếu không tìm thấy giải pháp.
    """
    initial_state = SokobanState(tuple(tuple(row) for row in maze), player_pos, frozenset(boxes), frozenset(targets))
    solver = AStarSolver(csv_file='results.csv')
    return solver.solve(initial_state)
