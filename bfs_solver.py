from typing import FrozenSet, List, Tuple, Optional, Set
from sokoban_common import SokobanState, MOVES
from collections import deque

class BFSSolver:
    """
    Summary:
        Lớp giải thuật tìm kiếm theo chiều rộng (BFS) cho bài toán Sokoban.
        Lớp này sẽ giải quyết bài toán tìm đường đi từ trạng thái ban đầu đến trạng thái đích bằng cách duyệt qua tất cả các trạng thái hợp lệ.

    Arguments:
        max_iterations -- Số vòng lặp tối đa để tránh vòng lặp vô tận (mặc định: 1000000).
    """
    def __init__(self, max_iterations: int = 1000000):
        """
        Summary:
            Khởi tạo đối tượng giải thuật BFS với giới hạn số vòng lặp.

        Arguments:
            max_iterations -- Số vòng lặp tối đa (mặc định là 1000000).
        """
        self.max_iterations = max_iterations  # Giới hạn số vòng lặp tối đa

    def solve(self, initial_state: SokobanState) -> Optional[List[Tuple[int, int]]]:
        """
        Summary:
            Giải quyết bài toán Sokoban từ trạng thái ban đầu.

        Arguments:
            initial_state -- Trạng thái ban đầu của trò chơi.

        Returns:
            Optional[List[Tuple[int, int]]] -- Danh sách các bước di chuyển (nếu có giải pháp), hoặc None nếu không tìm thấy giải pháp.
        """
        # Khởi tạo hàng đợi với trạng thái ban đầu và lộ trình rỗng
        queue = deque([(initial_state, [])])
        visited = set()  # Tập hợp lưu các trạng thái đã thăm để tránh việc duyệt lại

        for _ in range(self.max_iterations):  # Lặp tối đa max_iterations lần
            if not queue:  # Nếu hàng đợi rỗng, không còn trạng thái nào để duyệt
                return None

            # Lấy trạng thái và lộ trình từ hàng đợi
            current_state, path = queue.popleft()
            if current_state.is_goal():  # Kiểm tra nếu đã đạt trạng thái đích
                return path  # Trả về lộ trình

            # Chuyển trạng thái thành dạng có thể so sánh để kiểm tra đã thăm chưa
            state_hash = self.state_to_hashable(current_state)
            if state_hash in visited:
                continue  # Nếu trạng thái đã thăm, bỏ qua

            visited.add(state_hash)  # Đánh dấu trạng thái là đã thăm

            # Duyệt qua các nước đi hợp lệ từ trạng thái hiện tại
            for move in MOVES:
                next_state = current_state.apply_move(move)  # Áp dụng nước đi vào trạng thái hiện tại
                if next_state != current_state:  # Nếu trạng thái mới khác trạng thái hiện tại
                    queue.append((next_state, path + [move]))  # Thêm trạng thái mới vào hàng đợi và cập nhật lộ trình

        return None  # Nếu không tìm thấy giải pháp, trả về None

    @staticmethod
    def state_to_hashable(state: SokobanState) -> Tuple[Tuple[int, int], FrozenSet[Tuple[int, int]]]:
        """
        Summary:
            Chuyển trạng thái thành một dạng có thể so sánh được (hashable) để lưu vào tập hợp visited.

        Arguments:
            state -- Trạng thái của trò chơi.

        Returns:
            Tuple[Tuple[int, int], FrozenSet[Tuple[int, int]]] -- Trạng thái chuyển thành tuple có thể so sánh được.
        """
        return (state.player_pos, state.boxes)  # Trả về tuple chứa vị trí người chơi và các hộp

def solve_sokoban_bfs(maze: List[List[int]], 
                      player_pos: Tuple[int, int],
                      boxes: List[Tuple[int, int]], 
                      targets: List[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
    """
    Summary:
        Giải quyết bài toán Sokoban bằng giải thuật tìm kiếm theo chiều rộng (BFS) từ trạng thái ban đầu.

    Arguments:
        maze -- Bản đồ trò chơi dưới dạng ma trận 2D.
        player_pos -- Vị trí ban đầu của người chơi.
        boxes -- Tập hợp các tọa độ của các hộp.
        targets -- Tập hợp các tọa độ mục tiêu.

    Returns:
        Optional[List[Tuple[int, int]]] -- Danh sách các bước di chuyển nếu giải pháp tồn tại, hoặc None nếu không.
    """
    # Tạo trạng thái ban đầu từ bản đồ, vị trí người chơi, vị trí các hộp và mục tiêu
    initial_state = SokobanState(tuple(tuple(row) for row in maze), player_pos, frozenset(boxes), frozenset(targets))
    
    # Khởi tạo solver BFS và trả về kết quả
    solver = BFSSolver()
    return solver.solve(initial_state)  # Tìm giải pháp từ trạng thái ban đầu
