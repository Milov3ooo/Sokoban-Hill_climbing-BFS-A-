import heapq
from typing import List, Tuple, Optional, FrozenSet
from sokoban_common import SokobanState, MOVES

class AStarSolver:
    """
    Summary:
        Lớp giải thuật A* tối ưu cho bài toán Sokoban.
        Lớp này áp dụng thuật toán A* để tìm kiếm giải pháp từ trạng thái ban đầu đến trạng thái đích,
        với việc tối ưu hóa tìm kiếm bằng cách sử dụng heuristic và phát hiện bế tắc.

    Arguments:
        max_iterations -- Số vòng lặp tối đa (mặc định là 1000000).
    """
    def __init__(self, max_iterations: int = 1000000):
        """
        Summary:
            Khởi tạo đối tượng giải thuật A* với số vòng lặp tối đa.

        Arguments:
            max_iterations -- Số vòng lặp tối đa (mặc định là 1000000).
        """
        self.max_iterations = max_iterations  # Giới hạn số vòng lặp tối đa
    
    def solve(self, initial_state: SokobanState) -> Optional[List[Tuple[int, int]]]:
        """
        Summary:
            Giải quyết bài toán Sokoban bằng giải thuật A* tối ưu.

        Arguments:
            initial_state -- Trạng thái ban đầu của trò chơi.

        Returns:
            Optional[List[Tuple[int, int]]] -- Danh sách các bước di chuyển (nếu có giải pháp), hoặc None nếu không có.
        """
        # Khởi tạo node bắt đầu với heuristic, chi phí ban đầu, và lộ trình rỗng
        start_node = (initial_state.heuristic(), 0, [], initial_state)
        frontier = [start_node]  # Hàng đợi ưu tiên (min-heap)
        explored = set()  # Tập các trạng thái đã thăm
        deadlock_cache = {}  # Bộ nhớ đệm để kiểm tra trạng thái bế tắc

        for _ in range(self.max_iterations):  # Lặp tối đa max_iterations lần
            if not frontier:  # Nếu không còn node trong hàng đợi, không tìm thấy giải pháp
                return None

            # Lấy node có chi phí thấp nhất từ hàng đợi
            _, cost, path, current_state = heapq.heappop(frontier)

            if current_state.is_goal():  # Kiểm tra nếu đã đạt trạng thái đích
                return path  # Trả về lộ trình

            # Chuyển trạng thái thành dạng có thể so sánh (hashable)
            state_hash = self.state_to_hashable(current_state)
            if state_hash in explored:  # Nếu trạng thái đã được thăm, bỏ qua
                continue
            explored.add(state_hash)  # Đánh dấu trạng thái là đã thăm

            # Duyệt qua các nước đi hợp lệ
            for move in MOVES:
                next_state = current_state.apply_move(move)  # Áp dụng nước đi vào trạng thái hiện tại
                if next_state != current_state and not self.is_deadlock(next_state, deadlock_cache):
                    # Tính toán chi phí và heuristic cho trạng thái tiếp theo
                    next_cost = cost + 1
                    next_heuristic = next_state.heuristic()
                    # Tạo node mới với chi phí tổng cộng là chi phí hiện tại cộng heuristic
                    next_node = (next_cost + next_heuristic, next_cost, path + [move], next_state)
                    heapq.heappush(frontier, next_node)  # Thêm node mới vào hàng đợi

        return None  # Nếu không tìm thấy giải pháp, trả về None

    @staticmethod
    def state_to_hashable(state: SokobanState) -> Tuple[Tuple[int, int], FrozenSet[Tuple[int, int]]]:
        """
        Summary:
            Chuyển trạng thái thành dạng có thể so sánh được để kiểm tra các trạng thái đã thăm.

        Arguments:
            state -- Trạng thái của trò chơi.

        Returns:
            Tuple[Tuple[int, int], FrozenSet[Tuple[int, int]]] -- Trạng thái được chuyển thành tuple có thể so sánh được.
        """
        return (state.player_pos, state.boxes)  # Trả về tuple chứa vị trí người chơi và các hộp

    def is_deadlock(self, state: SokobanState, deadlock_cache: dict) -> bool:
        """
        Summary:
            Kiểm tra trạng thái có phải bế tắc không bằng cách sử dụng bộ nhớ đệm.

        Arguments:
            state -- Trạng thái của trò chơi.
            deadlock_cache -- Bộ nhớ đệm để kiểm tra các trạng thái bế tắc.

        Returns:
            bool -- True nếu trạng thái là bế tắc, False nếu không.
        """
        state_hash = self.state_to_hashable(state)  # Chuyển trạng thái thành dạng có thể so sánh
        if state_hash in deadlock_cache:  # Nếu trạng thái đã được kiểm tra
            return deadlock_cache[state_hash]  # Trả về kết quả từ bộ nhớ đệm

        # Kiểm tra trạng thái có bế tắc không
        is_deadlock = self.check_deadlock(state)
        deadlock_cache[state_hash] = is_deadlock  # Lưu kết quả vào bộ nhớ đệm
        return is_deadlock

    def check_deadlock(self, state: SokobanState) -> bool:
        """
        Summary:
            Kiểm tra trạng thái có bế tắc không bằng cách kiểm tra từng hộp.

        Arguments:
            state -- Trạng thái của trò chơi.

        Returns:
            bool -- True nếu có bế tắc, False nếu không.
        """
        for box in state.boxes:
            if self.is_corner_deadlock(state, box):  # Kiểm tra nếu hộp bị bế tắc ở góc
                return True
        return False

    def is_corner_deadlock(self, state: SokobanState, box: Tuple[int, int]) -> bool:
        """
        Summary:
            Kiểm tra xem một hộp có bị bế tắc ở góc không.

        Arguments:
            state -- Trạng thái của trò chơi.
            box -- Vị trí của hộp cần kiểm tra.

        Returns:
            bool -- True nếu hộp bị bế tắc ở góc, False nếu không.
        """
        x, y = box
        if box in state.targets:  # Nếu hộp đã nằm trên mục tiêu, không phải bế tắc
            return False
        
        # Kiểm tra nếu có các tường xung quanh hộp (góc bế tắc)
        walls = [
            (state.maze[y-1][x] == 1 and state.maze[y][x-1] == 1),
            (state.maze[y-1][x] == 1 and state.maze[y][x+1] == 1),
            (state.maze[y+1][x] == 1 and state.maze[y][x-1] == 1),
            (state.maze[y+1][x] == 1 and state.maze[y][x+1] == 1)
        ]
        
        return any(walls)  # Nếu có bất kỳ tường nào, hộp sẽ bị bế tắc

def solve_sokoban_astar(maze: List[List[int]], 
                        player_pos: Tuple[int, int],
                        boxes: List[Tuple[int, int]], 
                        targets: List[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
    """
    Summary:
        Giải quyết bài toán Sokoban bằng giải thuật A* tối ưu từ trạng thái ban đầu.

    Arguments:
        maze -- Bản đồ trò chơi dưới dạng ma trận 2D.
        player_pos -- Vị trí ban đầu của người chơi.
        boxes -- Tập hợp các tọa độ của các hộp.
        targets -- Tập hợp các tọa độ mục tiêu.

    Returns:
        Optional[List[Tuple[int, int]]] -- Danh sách các bước di chuyển nếu giải pháp tồn tại, hoặc None nếu không.
    """
    # Tạo trạng thái ban đầu từ bản đồ, vị trí người chơi, các hộp và mục tiêu
    initial_state = SokobanState(tuple(tuple(row) for row in maze), player_pos, frozenset(boxes), frozenset(targets))
    
    # Khởi tạo solver A* và trả về kết quả
    solver = AStarSolver()  # Khởi tạo đối tượng giải thuật A* tối ưu
    return solver.solve(initial_state)  # Tìm giải pháp từ trạng thái ban đầu
