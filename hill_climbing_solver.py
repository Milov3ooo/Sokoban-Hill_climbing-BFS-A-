# import random
# from typing import List, Tuple, Optional
# from sokoban_common import SokobanState, MOVES

# class HillClimbingSolver:
#     """
#     Summary:
#         Giải thuật leo đồi (Hill Climbing) cho bài toán Sokoban. 
#         Giải thuật này tìm kiếm giải pháp bằng cách di chuyển theo hướng có điểm số tốt hơn, 
#         và dừng lại khi không thể tìm thấy trạng thái tốt hơn hoặc đạt được trạng thái đích.

#     Arguments:
#         max_iterations -- Số vòng lặp tối đa (mặc định: 1000).
#         max_sideways -- Số lần di chuyển ngang tối đa (mặc định: 100).
#     """
#     def __init__(self, max_iterations: int = 1000, max_sideways: int = 100):
#         """
#         Summary:
#             Khởi tạo đối tượng giải thuật leo đồi với các tham số giới hạn số vòng lặp và số lần di chuyển ngang.

#         Arguments:
#             max_iterations -- Số vòng lặp tối đa (mặc định: 1000).
#             max_sideways -- Số lần di chuyển ngang tối đa (mặc định: 100).
#         """
#         self.max_iterations = max_iterations  # Số vòng lặp tối đa
#         self.max_sideways = max_sideways  # Số lần di chuyển ngang tối đa

#     def solve(self, initial_state: SokobanState) -> Optional[List[Tuple[int, int]]]:
#         """
#         Summary:
#             Giải quyết bài toán Sokoban bằng giải thuật leo đồi (Hill Climbing).

#         Arguments:
#             initial_state -- Trạng thái ban đầu của trò chơi.

#         Returns:
#             Optional[List[Tuple[int, int]]] -- Danh sách các bước di chuyển (nếu có giải pháp), hoặc None nếu không tìm thấy giải pháp.
#         """
#         current_state = initial_state
#         current_score = self.evaluate_state(current_state)  # Đánh giá điểm số của trạng thái hiện tại
#         path = []  # Danh sách lưu các bước di chuyển

#         for _ in range(self.max_iterations):  # Lặp tối đa max_iterations lần
#             if current_state.is_goal():  # Kiểm tra nếu đã đạt trạng thái đích
#                 return path  # Trả về lộ trình

#             neighbors = self.get_neighbors(current_state)  # Lấy các trạng thái liền kề
#             if not neighbors:  # Nếu không có hàng xóm, không thể tiếp tục
#                 return None

#             # Lọc ra các hàng xóm có điểm số lớn hơn điểm số hiện tại
#             better_neighbors = [(neighbor, move) for neighbor, move in neighbors if self.evaluate_state(neighbor) > current_score]

#             if better_neighbors:  # Nếu có hàng xóm có điểm số lớn hơn
#                 best_neighbor = random.choice(better_neighbors)  # Chọn ngẫu nhiên một trong số đó
#             else:
#                 # Nếu không có hàng xóm nào có điểm lớn hơn, lọc các hàng xóm có điểm số bằng
#                 best_neighbors = [(neighbor, move) for neighbor, move in neighbors if self.evaluate_state(neighbor) == current_score]
#                 if best_neighbors:  # Nếu có hàng xóm điểm số bằng
#                     best_neighbor = random.choice(best_neighbors)  # Chọn ngẫu nhiên
#                 else:
#                     # Nếu không có hàng xóm nào có điểm bằng hoặc lớn hơn, thiết lập lại ngẫu nhiên
#                     current_state = self.get_random_state(initial_state)  # Tạo lại trạng thái ngẫu nhiên
#                     current_score = self.evaluate_state(current_state)  # Đánh giá lại điểm số
#                     path = []  # Reset lộ trình
#                     continue

#             # Cập nhật trạng thái hiện tại
#             current_state = best_neighbor[0]
#             current_score = self.evaluate_state(current_state)
#             path.append(best_neighbor[1])  # Thêm nước đi vào lộ trình

#         return None  # Nếu không tìm thấy giải pháp, trả về None

#     def evaluate_state(self, state: SokobanState) -> float:
#         """
#         Summary:
#             Đánh giá điểm số của một trạng thái, dựa trên khoảng cách Manhattan từ các hộp đến mục tiêu.

#         Arguments:
#             state -- Trạng thái cần đánh giá.

#         Returns:
#             float -- Điểm số của trạng thái.
#         """
#         if state.is_goal():  # Nếu là trạng thái đích, trả về điểm vô cùng
#             return float('inf')

#         score = 0
#         for box in state.boxes:  # Duyệt qua các hộp
#             # Tính khoảng cách Manhattan tới mục tiêu gần nhất
#             min_distance = min(abs(box[0] - target[0]) + abs(box[1] - target[1]) for target in state.targets)
#             score -= min_distance  # Trừ khoảng cách để tính điểm số

#         return score

#     def get_neighbors(self, state: SokobanState) -> List[Tuple[SokobanState, Tuple[int, int]]]:
#         """
#         Summary:
#             Lấy các trạng thái liền kề (hàng xóm) từ trạng thái hiện tại.

#         Arguments:
#             state -- Trạng thái hiện tại.

#         Returns:
#             List[Tuple[SokobanState, Tuple[int, int]]] -- Danh sách các trạng thái liền kề và nước đi tương ứng.
#         """
#         neighbors = []
#         for move in MOVES:  # Duyệt qua các hướng di chuyển
#             new_state = state.apply_move(move)  # Áp dụng nước đi vào trạng thái hiện tại
#             if new_state != state:  # Nếu trạng thái mới khác trạng thái hiện tại
#                 neighbors.append((new_state, move))  # Thêm vào danh sách hàng xóm
#         return neighbors

#     def get_random_state(self, initial_state: SokobanState) -> SokobanState:
#         """
#         Summary:
#             Tạo một trạng thái ngẫu nhiên từ trạng thái ban đầu.

#         Arguments:
#             initial_state -- Trạng thái ban đầu.

#         Returns:
#             SokobanState -- Trạng thái ngẫu nhiên.
#         """
#         current_state = initial_state
#         for _ in range(random.randint(1, 20)):  # Di chuyển ngẫu nhiên từ 1 đến 20 lần
#             neighbors = self.get_neighbors(current_state)  # Lấy các hàng xóm
#             if neighbors:
#                 current_state = random.choice(neighbors)[0]  # Chọn ngẫu nhiên một trạng thái mới
#             else:
#                 break  # Nếu không có hàng xóm, dừng lại
#         return current_state

# def solve_sokoban_hillclimbing(maze: List[List[int]], 
#                                player_pos: Tuple[int, int],
#                                boxes: List[Tuple[int, int]], 
#                                targets: List[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
#     """
#     Summary:
#         Giải quyết bài toán Sokoban bằng giải thuật leo đồi (Hill Climbing) từ trạng thái ban đầu.

#     Arguments:
#         maze -- Bản đồ trò chơi dưới dạng ma trận 2D.
#         player_pos -- Vị trí ban đầu của người chơi.
#         boxes -- Tập hợp các tọa độ của các hộp.
#         targets -- Tập hợp các tọa độ mục tiêu.

#     Returns:
#         Optional[List[Tuple[int, int]]] -- Danh sách các bước di chuyển nếu giải pháp tồn tại, hoặc None nếu không.
#     """
#     # Tạo trạng thái ban đầu từ bản đồ, vị trí người chơi, các hộp và mục tiêu
#     initial_state = SokobanState(tuple(tuple(row) for row in maze), player_pos, frozenset(boxes), frozenset(targets))
    
#     # Khởi tạo solver leo đồi và trả về kết quả
#     solver = HillClimbingSolver()
#     return solver.solve(initial_state)  # Tìm giải pháp từ trạng thái ban đầu

import random
from typing import List, Tuple, Optional
from sokoban_common import SokobanState, MOVES

class HillClimbingSolver:
    def __init__(self, max_iterations: int = 1000, max_sideways: int = 100):
        self.max_iterations = max_iterations
        self.max_sideways = max_sideways

    def solve(self, initial_state: SokobanState) -> Optional[List[Tuple[int, int]]]:
        current_state = initial_state
        current_score = self.evaluate_state(current_state)
        path = []

        for _ in range(self.max_iterations):
            if current_state.is_goal():
                return path

            neighbors = self.get_neighbors(current_state)
            if not neighbors:
                return None

            # Lọc ra các hàng xóm có điểm số lớn hơn điểm số hiện tại
            better_neighbors = [(neighbor, move) for neighbor, move in neighbors if self.evaluate_state(neighbor) > current_score]

            if better_neighbors:
                # Nếu có hàng xóm có điểm lớn hơn, chọn ngẫu nhiên một trong số đó
                best_neighbor = random.choice(better_neighbors)
            else:
                # Nếu không có hàng xóm nào lớn hơn, lọc các hàng xóm có điểm số bằng
                best_neighbors = [(neighbor, move) for neighbor, move in neighbors if self.evaluate_state(neighbor) == current_score]
                if best_neighbors:
                    # Chọn ngẫu nhiên một trong các hàng xóm có điểm số bằng
                    best_neighbor = random.choice(best_neighbors)
                else:
                    # Nếu không có hàng xóm nào có điểm bằng hoặc lớn hơn, thiết lập lại ngẫu nhiên
                    current_state = self.get_random_state(initial_state)
                    current_score = self.evaluate_state(current_state)
                    path = []
                    continue

            # Cập nhật trạng thái hiện tại
            current_state = best_neighbor[0]
            current_score = self.evaluate_state(current_state)
            path.append(best_neighbor[1])

        return None



    def evaluate_state(self, state: SokobanState) -> float:
        if state.is_goal():
            return float('inf')

        score = 0
        for box in state.boxes:
            min_distance = min(abs(box[0] - target[0]) + abs(box[1] - target[1]) for target in state.targets)
            score -= min_distance

        return score

    def get_neighbors(self, state: SokobanState) -> List[Tuple[SokobanState, Tuple[int, int]]]:
        neighbors = []
        for move in MOVES:
            new_state = state.apply_move(move)
            if new_state != state:
                neighbors.append((new_state, move))
        return neighbors

    def get_random_state(self, initial_state: SokobanState) -> SokobanState:
        current_state = initial_state
        for _ in range(random.randint(1, 20)):
            neighbors = self.get_neighbors(current_state)
            if neighbors:
                current_state = random.choice(neighbors)[0]
            else:
                break
        return current_state

def solve_sokoban_hillclimbing(maze: List[List[int]], 
                               player_pos: Tuple[int, int],
                               boxes: List[Tuple[int, int]], 
                               targets: List[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
    initial_state = SokobanState(tuple(tuple(row) for row in maze), player_pos, frozenset(boxes), frozenset(targets))
    solver = HillClimbingSolver()
    return solver.solve(initial_state)