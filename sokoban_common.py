from typing import List, Tuple, Set, Dict, FrozenSet
from dataclasses import dataclass
import numpy as np
from scipy.optimize import linear_sum_assignment

MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Left, Right, Up, Down

@dataclass(frozen=True)
class SokobanState:
    """
    Summary:
        Biểu diễn trạng thái của trò chơi Sokoban, bao gồm các phương thức để kiểm tra trạng thái đích,
        tính toán chi phí heuristic, và phát hiện các khu vực thùng không thể di chuyển.

    Arguments:
        maze -- Bản đồ trò chơi dưới dạng ma trận 2D (0: trống, 1: tường).
        player_pos -- Vị trí của người chơi trên bản đồ.
        boxes -- Tập hợp các tọa độ của các hộp.
        targets -- Tập hợp các tọa độ của các mục tiêu.
        _zone_map -- Bản đồ vùng để giúp phát hiện các khu vực thùng không thể di chuyển (mặc định là None).
        _deadlock_cache -- Bộ nhớ đệm để kiểm tra các khu vực thùng không thể di chuyển (mặc định là None).
    """
    maze: Tuple[Tuple[int, ...], ...]
    player_pos: Tuple[int, int]
    boxes: FrozenSet[Tuple[int, int]]
    targets: FrozenSet[Tuple[int, int]]
    _zone_map: Dict[Tuple[int, int], int] = None
    _deadlock_cache: Dict[Tuple[int, int], bool] = None

    def __post_init__(self):
        """
        Summary:
            Khởi tạo các thuộc tính bổ sung như _zone_map và _deadlock_cache nếu chúng chưa được thiết lập.
        """
        if self._zone_map is None:
            object.__setattr__(self, '_zone_map', self._create_zone_map())  # Tạo bản đồ vùng
        if self._deadlock_cache is None:
            object.__setattr__(self, '_deadlock_cache', {})  # Khởi tạo bộ nhớ đệm cho khu vực thùng không thể di chuyển

    def _create_zone_map(self) -> Dict[Tuple[int, int], int]:
        """
        Summary:
            Tạo bản đồ phân vùng cho các ô trên bản đồ để hỗ trợ phát hiện các khu vực thùng không thể di chuyển.

        Returns:
            zone_map -- Bản đồ phân vùng, gán mỗi ô vào một vùng riêng.
        """
        zone_map = {}
        current_zone = 0
        for y in range(len(self.maze)):
            for x in range(len(self.maze[0])):
                if (x, y) not in zone_map and self.maze[y][x] != 1:
                    self._flood_fill(x, y, current_zone, zone_map)
                    current_zone += 1
        return zone_map

    def _flood_fill(self, x: int, y: int, zone: int, zone_map: Dict[Tuple[int, int], int]):
        """
        Summary:
            Áp dụng thuật toán tô màu (flood fill) để gán vùng cho các ô trống.

        Arguments:
            x, y -- Tọa độ hiện tại.
            zone -- Mã vùng hiện tại.
            zone_map -- Bản đồ vùng để cập nhật.
        """
        if not (0 <= x < len(self.maze[0]) and 0 <= y < len(self.maze)):
            return
        if self.maze[y][x] == 1 or (x, y) in zone_map:
            return
        zone_map[(x, y)] = zone
        for dx, dy in MOVES:
            self._flood_fill(x + dx, y + dy, zone, zone_map)

    def is_goal(self) -> bool:
        """
        Summary:
            Kiểm tra trạng thái hiện tại có phải trạng thái đích (tất cả các hộp đã nằm trên mục tiêu).

        Returns:
            bool -- True nếu tất cả các hộp nằm trên mục tiêu, False nếu không.
        """
        return self.boxes == self.targets  # Kiểm tra nếu vị trí các hộp khớp với mục tiêu

    def get_possible_moves(self) -> List[Tuple[int, int]]:
        """
        Summary:
            Lấy danh sách các nước đi hợp lệ từ trạng thái hiện tại.

        Returns:
            List[Tuple[int, int]] -- Danh sách các nước đi hợp lệ.
        """
        return [move for move in MOVES if self._is_valid_move(*self._get_new_position(move))]

    def _get_new_position(self, move: Tuple[int, int]) -> Tuple[int, int]:
        """
        Summary:
            Tính toán tọa độ mới của người chơi sau một nước đi.

        Arguments:
            move -- Hướng di chuyển (dx, dy).

        Returns:
            Tuple[int, int] -- Tọa độ mới của người chơi.
        """
        return self.player_pos[0] + move[0], self.player_pos[1] + move[1]

    def _is_valid_move(self, x: int, y: int) -> bool:
        """
        Summary:
            Kiểm tra xem nước đi tới vị trí (x, y) có hợp lệ hay không.

        Arguments:
            x, y -- Tọa độ cần kiểm tra.

        Returns:
            bool -- True nếu nước đi hợp lệ, False nếu không.
        """
        if not self._is_within_bounds(x, y) or self.maze[y][x] == 1:
            return False
        if (x, y) in self.boxes:
            box_new_x, box_new_y = x + (x - self.player_pos[0]), y + (y - self.player_pos[1])
            return self._can_push_box(box_new_x, box_new_y)
        return True

    def _is_within_bounds(self, x: int, y: int) -> bool:
        """
        Summary:
            Kiểm tra xem tọa độ (x, y) có nằm trong phạm vi bản đồ không.

        Arguments:
            x, y -- Tọa độ cần kiểm tra.

        Returns:
            bool -- True nếu tọa độ hợp lệ, False nếu không.
        """
        return 0 <= x < len(self.maze[0]) and 0 <= y < len(self.maze)

    def _can_push_box(self, x: int, y: int) -> bool:
        """
        Summary:
            Kiểm tra xem có thể đẩy một hộp tới vị trí (x, y) hay không.

        Arguments:
            x, y -- Tọa độ vị trí cần kiểm tra.

        Returns:
            bool -- True nếu có thể đẩy hộp, False nếu không.
        """
        return (self._is_within_bounds(x, y) and 
                self.maze[y][x] != 1 and 
                (x, y) not in self.boxes and
                not self._is_deadlock_position(x, y))

    def apply_move(self, move: Tuple[int, int]) -> 'SokobanState':
        """
        Summary:
            Áp dụng một nước đi vào trạng thái hiện tại và trả về trạng thái mới.

        Arguments:
            move -- Hướng di chuyển (dx, dy).
        
        Returns:
            SokobanState -- Trạng thái mới sau khi áp dụng nước đi.
        """
        new_x, new_y = self._get_new_position(move)
        
        if not self._is_valid_move(new_x, new_y):
            return self  # Trả về trạng thái hiện tại nếu nước đi không hợp lệ
        
        new_boxes = set(self.boxes)  # Sao chép tập hợp các hộp
        if (new_x, new_y) in new_boxes:
            # Nếu có hộp tại vị trí mới, đẩy hộp đến vị trí mới
            box_new_x, box_new_y = new_x + move[0], new_y + move[1]
            new_boxes.remove((new_x, new_y))
            new_boxes.add((box_new_x, box_new_y))
        
        # Trả về trạng thái mới sau khi di chuyển người chơi và hộp (nếu có)
        return SokobanState(
            self.maze,
            (new_x, new_y),
            frozenset(new_boxes),
            self.targets,
            self._zone_map,
            self._deadlock_cache
        )

    def _is_deadlock_position(self, x: int, y: int) -> bool:
        """
        Summary:
            Kiểm tra xem vị trí (x, y) có phải là khu vực thùng không thể di chuyển hay không.

        Arguments:
            x, y -- Tọa độ cần kiểm tra.

        Returns:
            bool -- True nếu là khu vực thùng không thể di chuyển, False nếu không.
        """
        if (x, y) in self._deadlock_cache:
            return self._deadlock_cache[(x, y)]  # Kiểm tra bộ nhớ đệm

        # Kiểm tra các loại khu vực thùng không thể di chuyển
        is_deadlock = (self._is_corner_deadlock(x, y) or 
                    self._is_line_deadlock(x, y) or 
                    self._is_zone_deadlock(x, y))

        self._deadlock_cache[(x, y)] = is_deadlock  # Lưu kết quả vào bộ nhớ đệm
        return is_deadlock

    def _is_corner_deadlock(self, x: int, y: int) -> bool:
        """
        Summary:
            Kiểm tra xem vị trí (x, y) có phải là góc khu vực thùng không thể di chuyển hay không.

        Arguments:
            x, y -- Tọa độ cần kiểm tra.

        Returns:
            bool -- True nếu là góc khu vực thùng không thể di chuyển, False nếu không.
        """
        if (x, y) in self.targets:  # Nếu đã là mục tiêu thì không phải bế tắc
            return False

        # Kiểm tra nếu có tường ở cả hai hướng ngang và dọc
        horizontal_wall = (not self._is_within_bounds(x-1, y) or self.maze[y][x-1] == 1 or
                        not self._is_within_bounds(x+1, y) or self.maze[y][x+1] == 1)
        vertical_wall = (not self._is_within_bounds(x, y-1) or self.maze[y-1][x] == 1 or
                        not self._is_within_bounds(x, y+1) or self.maze[y+1][x] == 1)

        return horizontal_wall and vertical_wall  # Nếu có tường ở cả hai chiều thì bị bế tắc

    def _is_line_deadlock(self, x: int, y: int) -> bool:
        """
        Summary:
            Kiểm tra xem vị trí (x, y) có phải là một khu vực thùng không thể di chuyển theo hướng dòng hay không.

        Arguments:
            x, y -- Tọa độ cần kiểm tra.

        Returns:
            bool -- True nếu là khu vực thùng không thể di chuyển theo dòng, False nếu không.
        """
        if (x, y) in self.targets:  # Nếu là mục tiêu, không phải bế tắc
            return False

        # Kiểm tra khu vực thùng không thể di chuyển theo cả hai hướng ngang và dọc
        for axis in ['horizontal', 'vertical']:
            if self._check_line_deadlock(x, y, axis):
                return True  # Nếu có bế tắc theo bất kỳ chiều nào, trả về True
        
        return False  # Nếu không có bế tắc, trả về False

    def _check_line_deadlock(self, x: int, y: int, axis: str) -> bool:
        """
        Summary:
            Kiểm tra xem có khu vực thùng không thể di chuyển trong một dòng hay không (theo hướng ngang hoặc dọc).

        Arguments:
            x, y -- Tọa độ cần kiểm tra.
            axis -- Chọn giữa 'horizontal' hoặc 'vertical'.

        Returns:
            bool -- True nếu có khu vực thùng không thể di chuyển, False nếu không.
        """
        # Kiểm tra nếu có thể di chuyển theo chiều ngang hoặc dọc
        if axis == 'horizontal':
            if not self._is_within_bounds(x, y-1) or self.maze[y-1][x] != 1 or not self._is_within_bounds(x, y+1) or self.maze[y+1][x] != 1:
                return False
            directions = [(-1, 0), (1, 0)]  # Hướng di chuyển ngang
        else:  # vertical
            if not self._is_within_bounds(x-1, y) or self.maze[y][x-1] != 1 or not self._is_within_bounds(x+1, y) or self.maze[y][x+1] != 1:
                return False
            directions = [(0, -1), (0, 1)]  # Hướng di chuyển dọc

        # Duyệt qua từng hướng để kiểm tra nếu có tường hoặc không có lối thoát
        for dx, dy in directions:
            blocked = True
            cx, cy = x, y
            while True:
                cx, cy = cx + dx, cy + dy
                if not self._is_within_bounds(cx, cy) or self.maze[cy][cx] == 1:  # Nếu gặp tường hoặc ra ngoài phạm vi
                    break
                if (cx, cy) in self.targets:  # Nếu gặp mục tiêu, không bị bế tắc
                    blocked = False
                    break
            if not blocked:  # Nếu không bị chặn, không phải bế tắc
                return False
        return True  # Nếu gặp chướng ngại vật, trả về True

    def _is_zone_deadlock(self, x: int, y: int) -> bool:
        """
        Summary:
            Kiểm tra xem khu vực của vị trí (x, y) có phải là một khu vực thùng không thể di chuyển hay không.

        Arguments:
            x, y -- Tọa độ cần kiểm tra.

        Returns:
            bool -- True nếu khu vực thùng không thể di chuyển, False nếu không.
        """
        if (x, y) not in self._zone_map:
            return True  # Nếu không có vùng, thì coi như bế tắc

        box_zone = self._zone_map[(x, y)]  # Lấy vùng của thùng
        return not any(self._zone_map.get(target, -1) == box_zone for target in self.targets)  # Kiểm tra nếu có mục tiêu trong cùng vùng

    def heuristic(self) -> float:
        """
        Summary:
            Tính toán chi phí heuristic cho trạng thái hiện tại, bao gồm khoảng cách Manhattan từ các hộp đến mục tiêu,
            và các yếu tố khu vực thùng không thể di chuyển.

        Returns:
            float -- Chi phí heuristic của trạng thái hiện tại.
        """
        if self.is_goal():
            return 0  # Nếu đã đạt được trạng thái mục tiêu, chi phí heuristic bằng 0
        
        # Tính toán chi phí giữa các hộp và mục tiêu
        boxes = list(self.boxes)
        targets = list(self.targets)
        cost_matrix = np.zeros((len(boxes), len(targets)))

        for i, box in enumerate(boxes):
            for j, target in enumerate(targets):
                manhattan_dist = abs(box[0] - target[0]) + abs(box[1] - target[1])  # Tính khoảng cách Manhattan
                deadlock_penalty = 1000 if self._is_deadlock_position(box[0], box[1]) else 0  # Phạt nếu khu vực thùng không thể di chuyển
                zone_penalty = 500 if self._zone_map.get(box) != self._zone_map.get(target) else 0  # Phạt nếu không ở trong cùng vùng
                cost_matrix[i][j] = manhattan_dist + deadlock_penalty + zone_penalty  # Tổng chi phí

        # Tính toán tổng chi phí dựa trên phép ghép tối ưu
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        total_cost = cost_matrix[row_ind, col_ind].sum()

        # Tính khoảng cách từ người chơi đến hộp chưa khớp
        min_dist_to_unmatched_box = min(
            abs(self.player_pos[0] - box[0]) + abs(self.player_pos[1] - box[1])
            for box in boxes
        )

        return total_cost + min_dist_to_unmatched_box  # Trả về chi phí heuristic tổng cộng


    def __hash__(self) -> int:
        return hash((self.player_pos, self.boxes))

    def __eq__(self, other: 'SokobanState') -> bool:
        return (self.player_pos == other.player_pos and 
                self.boxes == other.boxes)
