--------------------------------
Sinh viên thực hiện

- Nguyễn Huy Bảo - 20033220316
- Đỗ Trung Dũng - 2033220680
- Phạm Nguyễn Thế Anh - 2033220108

####Hướng dẫn cài đặt

1.Sau khi giải nén

2.Mở terminal 

3.Nhập lệnh 

pip install -r requirements.txt

- Để tải các gói cần thiết để game chạy

4. Quay lại file Sokoban.py gõ lệnh 

python Sokoban.py

để chạy game

## Lớp `SokobanState` trong Trò Chơi Sokoban

Lớp `SokobanState` được sử dụng để đại diện cho một trạng thái trong trò chơi Sokoban. Trò chơi này là một trò chơi giải đố trong đó người chơi cần phải di chuyển các thùng vào các vị trí mục tiêu trên bản đồ, tránh các bức tường và không để thùng bị mắc kẹt. Lớp `SokobanState` bao gồm các thuộc tính và phương thức giúp mô phỏng và thao tác trên trạng thái của trò chơi.

### Các Thuộc Tính

1. **maze**: Bản đồ trò chơi, lưu trữ dưới dạng tuple 2D. Trong đó, `1` đại diện cho các bức tường và `0` đại diện cho các không gian trống. Bản đồ này giúp chúng ta xác định các vị trí có thể di chuyển và các chướng ngại vật.

2. **player_pos**: Vị trí của người chơi trên bản đồ, được biểu diễn dưới dạng tuple `(x, y)`. Đây là vị trí hiện tại của người chơi, giúp chúng ta tính toán các nước đi và kiểm tra các hành động hợp lệ.

3. **boxes**: Tập hợp bất biến (`frozenset`) chứa các vị trí của các thùng trên bản đồ, cũng dưới dạng tuple `(x, y)`. Đây là các vị trí mà người chơi cần phải di chuyển thùng đến các vị trí mục tiêu.

4. **targets**: Tập hợp bất biến (`frozenset`) chứa các vị trí mục tiêu của các thùng. Mỗi mục tiêu là một vị trí mà thùng cần phải được đẩy vào để hoàn thành trò chơi.

5. **_zone_map**: Đây là một từ điển ánh xạ các vị trí không phải tường (các không gian trống) tới một mã vùng. Mã vùng này giúp phân biệt các khu vực khác nhau trên bản đồ và hỗ trợ phát hiện các tình huống bế tắc, nơi thùng không thể di chuyển được.

6. **_deadlock_cache**: Đây là bộ nhớ đệm, chứa các kết quả của việc tính toán bế tắc trước đó để tránh phải tính toán lại khi trạng thái giống nhau xuất hiện trong các bước tiếp theo.

### Các Phương Thức Chính

#### `__post_init__`
Phương thức này được gọi tự động sau khi đối tượng `SokobanState` được khởi tạo. Nó đảm nhiệm việc khởi tạo các thuộc tính `_zone_map` và `_deadlock_cache` nếu chúng chưa được cung cấp trước đó. Đây là bước cần thiết để chuẩn bị dữ liệu cho các phép toán sau này.

#### `_create_zone_map`
Phương thức này xây dựng bản đồ vùng của trò chơi, nơi mỗi không gian trống (không phải tường) được ánh xạ đến một mã vùng. Điều này giúp phân vùng các khu vực có thể di chuyển và hỗ trợ phát hiện các tình huống bế tắc.

#### `is_goal`
Phương thức này kiểm tra xem trạng thái hiện tại có phải là trạng thái mục tiêu hay không, tức là kiểm tra xem tất cả các thùng đã được di chuyển vào các vị trí mục tiêu hay chưa.

#### `get_possible_moves`
Phương thức này trả về danh sách các nước đi hợp lệ từ trạng thái hiện tại. Một nước đi hợp lệ nếu người chơi có thể di chuyển đến một không gian trống hoặc đẩy một thùng tới một không gian trống mà không bị cản trở bởi tường hoặc các thùng khác.

#### `apply_move`
Phương thức này áp dụng một nước đi vào trạng thái hiện tại và trả về trạng thái mới sau khi thực hiện động tác di chuyển người chơi hoặc đẩy thùng. Đây là phương thức quan trọng để thay đổi trạng thái của trò chơi khi người chơi thực hiện một hành động.

#### `heuristic`
Phương thức này tính toán giá trị heuristic cho trạng thái hiện tại, giúp đánh giá chi phí từ trạng thái hiện tại đến mục tiêu. Giá trị heuristic này có thể kết hợp nhiều yếu tố, như khoảng cách Manhattan giữa các thùng và mục tiêu, các hình phạt cho thùng bị mắc kẹt, và sự phân tách vùng của các thùng và mục tiêu.

### Phát Hiện Bế Tắc

Phát hiện bế tắc trong trò chơi là rất quan trọng, vì nếu thùng bị mắc kẹt, người chơi sẽ không thể hoàn thành trò chơi. Các phương thức phát hiện bế tắc bao gồm:

- **_is_deadlock_position**: Kiểm tra xem một vị trí có phải là bế tắc hay không.
- **_is_corner_deadlock**: Kiểm tra xem thùng có bị mắc kẹt ở góc không thể di chuyển được.
- **_is_line_deadlock**: Kiểm tra xem thùng có bị mắc kẹt trong một khu vực dọc hoặc ngang không.
- **_is_zone_deadlock**: Kiểm tra xem một thùng có bị mắc kẹt trong một khu vực không thể di chuyển được không.

### Tính Toán Heuristic

Heuristic trong lớp `SokobanState` giúp đánh giá chi phí để đạt được mục tiêu từ trạng thái hiện tại. Heuristic được tính toán dựa trên các yếu tố như:

1. Khoảng cách Manhattan giữa các thùng và các mục tiêu.
2. Các hình phạt cho các thùng bị mắc kẹt.
3. Các hình phạt cho các thùng không ở trong vùng mục tiêu.

Giá trị heuristic là cơ sở để sử dụng trong các thuật toán tìm kiếm, như A* hoặc BFS, nhằm tìm ra con đường tối ưu để đạt được mục tiêu.

### So Sánh Các Trạng Thái

Các phương thức `__hash__` và `__eq__` cho phép so sánh hai trạng thái trò chơi. Điều này rất quan trọng trong các thuật toán tìm kiếm, giúp tránh việc tính toán lại các trạng thái giống nhau. Nếu hai trạng thái có cùng vị trí của người chơi và các thùng, chúng được xem là giống nhau.

### Kết Luận

Lớp `SokobanState` cung cấp đầy đủ các chức năng để mô phỏng và thao tác với trạng thái của trò chơi Sokoban. Nó bao gồm việc kiểm tra mục tiêu, tính toán các nước đi hợp lệ, phát hiện bế tắc và tính toán heuristic. Lớp này là một thành phần quan trọng trong việc xây dựng các thuật toán giải quyết trò chơi Sokoban, giúp các thuật toán như A* có thể tìm ra các giải pháp tối ưu một cách hiệu quả.

-------- 
Hill Climbing (leo đồi) để giải quyết bài toán Sokoban. Trò chơi Sokoban yêu cầu người chơi di chuyển các thùng vào các mục tiêu, và mục tiêu là đạt được trạng thái khi tất cả các thùng đã được đẩy vào vị trí mục tiêu. Giải thuật Hill Climbing tìm kiếm giải pháp bằng cách di chuyển theo hướng có điểm số tốt hơn, và dừng lại khi không thể tìm thấy trạng thái tốt hơn hoặc khi đạt được mục tiêu.

Giải thích Code
1. Khởi tạo lớp HillClimbingSolver
Lớp HillClimbingSolver thực hiện giải quyết bài toán Sokoban bằng thuật toán leo đồi. Dưới đây là các thành phần của lớp:

__init__: Phương thức khởi tạo nhận vào 2 tham số là max_iterations (số vòng lặp tối đa) và max_sideways (số lần di chuyển ngang tối đa). Tham số này giúp giới hạn số vòng lặp để tránh vòng lặp vô tận khi không thể tìm thấy giải pháp tốt hơn.

solve: Phương thức chính giải quyết bài toán Sokoban bằng giải thuật Hill Climbing. Nó thực hiện theo các bước:

Khởi tạo trạng thái hiện tại từ trạng thái ban đầu và đánh giá điểm số của nó.
Lặp qua các vòng lặp tối đa (tới max_iterations). Nếu trạng thái hiện tại là trạng thái mục tiêu, trả về đường đi.
Lấy các trạng thái liền kề của trạng thái hiện tại và tính toán điểm số cho từng trạng thái.
Chọn trạng thái có điểm số cao hơn và di chuyển tới trạng thái đó.
Nếu không tìm thấy trạng thái tốt hơn (hoặc không có hàng xóm), phương thức có thể "đặt lại" trạng thái ngẫu nhiên và thử lại.
evaluate_state: Phương thức này tính điểm số của trạng thái dựa trên khoảng cách Manhattan giữa các thùng và các mục tiêu. Điểm số càng cao (hoặc càng gần các mục tiêu) thì trạng thái càng tốt.

get_neighbors: Phương thức này lấy tất cả các trạng thái liền kề của trạng thái hiện tại. Các trạng thái này được tạo ra bằng cách áp dụng các động tác di chuyển cho người chơi.

get_random_state: Phương thức này tạo ra một trạng thái ngẫu nhiên từ trạng thái ban đầu. Nó di chuyển ngẫu nhiên từ 1 đến 20 lần để tạo ra một trạng thái khác từ trạng thái ban đầu.

2. Giải Thích Các Phương Thức và Cách Liên Quan với Lớp SokobanState
Lớp HillClimbingSolver sử dụng lớp SokobanState để mô phỏng trạng thái của trò chơi. Các phương thức trong HillClimbingSolver tương tác với lớp SokobanState như sau:

Khởi tạo Trạng Thái: Trong phương thức solve_sokoban_hillclimbing, một trạng thái ban đầu của trò chơi được tạo ra từ ma trận bản đồ, vị trí người chơi, các thùng và mục tiêu. Trạng thái này được truyền vào lớp SokobanState, nơi các thông tin này được lưu trữ và xử lý.

Đánh Giá Trạng Thái (evaluate_state): Phương thức evaluate_state sử dụng các thông tin từ lớp SokobanState để tính toán điểm số cho trạng thái hiện tại. Cụ thể, nó duyệt qua tất cả các thùng và tính khoảng cách Manhattan từ mỗi thùng đến các mục tiêu. Khoảng cách này ảnh hưởng trực tiếp đến điểm số trạng thái (điểm càng thấp thì càng tốt).

Lấy Hàng Xóm (get_neighbors): Phương thức này sử dụng SokobanState để lấy danh sách các trạng thái liền kề. Bằng cách áp dụng các nước đi từ danh sách MOVES, phương thức get_neighbors sẽ tạo ra các trạng thái mới và kiểm tra xem các trạng thái này có thay đổi so với trạng thái hiện tại hay không.

Áp Dụng Nước Đi (apply_move): Lớp SokobanState có phương thức apply_move để áp dụng các nước đi cho người chơi. Phương thức này cập nhật vị trí của người chơi và các thùng sau mỗi nước đi. Trong giải thuật Hill Climbing, apply_move là cách để tạo ra trạng thái mới từ trạng thái hiện tại.

Kiểm Tra Mục Tiêu (is_goal): Phương thức is_goal trong lớp SokobanState được sử dụng trong giải thuật để kiểm tra xem trạng thái hiện tại đã đạt được mục tiêu chưa (tức là tất cả các thùng đã được di chuyển vào các mục tiêu).

3. Chi Tiết Cách Tính Điểm (Heuristic)
Trong giải thuật Hill Climbing, evaluate_state đóng vai trò là hàm heuristic, đánh giá chất lượng của một trạng thái. Trong trường hợp này, nó tính điểm dựa trên khoảng cách Manhattan giữa các thùng và các mục tiêu, điểm càng cao hơn càng tốt. Điều này phản ánh mục tiêu của trò chơi là di chuyển các thùng tới các mục tiêu.

4. Quy Trình Giải Quyết
Khởi tạo: Dữ liệu ban đầu như bản đồ, vị trí người chơi, các thùng và các mục tiêu được sử dụng để tạo một đối tượng SokobanState.
Khởi tạo Solver: Một đối tượng HillClimbingSolver được tạo ra và phương thức solve được gọi để giải quyết bài toán.
Lặp qua các bước: Trong phương thức solve, các trạng thái liền kề được kiểm tra, và trạng thái tốt nhất được chọn dựa trên điểm số (heuristic). Nếu không có trạng thái tốt hơn, thuật toán sẽ cố gắng "đặt lại" trạng thái ngẫu nhiên và tiếp tục.
Kết thúc: Nếu đạt được mục tiêu, đường đi (lộ trình) được trả về, nếu không, trả về None.
Kết Luận
Giải thuật Hill Climbing trong bài toán Sokoban sử dụng lớp SokobanState để đại diện cho trạng thái của trò chơi. Lớp này giúp mô phỏng và thao tác với các yếu tố của trò chơi như bản đồ, người chơi, thùng và mục tiêu. Các phương thức trong HillClimbingSolver sử dụng SokobanState để đánh giá trạng thái, tính toán heuristic, áp dụng các nước đi và kiểm tra trạng thái mục tiêu.