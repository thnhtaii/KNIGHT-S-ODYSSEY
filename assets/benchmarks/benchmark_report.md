# BÁO CÁO ĐÁNH GIÁ HIỆU SUẤT THUẬT TOÁN AI THEO TỪNG LEVEL
## Dự án: Stickyman-Battle

Báo cáo này trình bày kết quả đo lường, đánh giá và so sánh hiệu năng thực tế của các giải thuật Trí tuệ Nhân tạo (AI) được triển khai riêng biệt cho từng Level từ 1 đến 6.

---

### 1. LEVEL 1: Uninformed Pathfinding (BFS, DFS, UCS)
Ở Màn 1, các quái vật Slime tìm đường đi tiếp cận người chơi dựa trên các thuật toán tìm kiếm mù (Uninformed Search).

#### Biểu đồ so sánh:
![So sánh Level 1](comparison_level1_classic.png)

#### Phân tích kết quả:
* **BFS (Breadth-First Search):** Loang đều theo các hướng vuông góc. Đảm bảo tìm thấy **đường đi ngắn nhất tối ưu** (ví dụ: 30 ô). Tuy nhiên, số lượng nút duyệt lớn khiến thời gian xử lý lâu hơn các thuật toán có tri thức định hướng.
* **DFS (Depth-First Search):** Đi sâu tối đa theo một hướng trước khi quay lui. Thuật toán chạy nhanh nhưng **đường đi tìm được cực kỳ kém tối ưu** (bị đi vòng, dài hơn rất nhiều so với BFS).
* **UCS (Uniform-Cost Search / Dijkstra):** Trong môi trường lưới đồng nhất chi phí di chuyển giữa mỗi ô là 1, UCS hoạt động hoàn toàn giống BFS, đảm bảo tìm thấy đường đi tối ưu.

---

### 2. LEVEL 2: Informed Pathfinding (Greedy BFS, A*, IDA*)
Ở Màn 2, quái vật Ice Wolf sử dụng tri thức heuristic (Khoảng cách Manhattan) để tối ưu hóa hiệu năng tìm đường.

#### Biểu đồ so sánh:
![So sánh Level 2](comparison_level2_heuristic.png)

#### Phân tích kết quả:
* **Greedy Best-First Search:** Chỉ dựa vào hàm heuristic $h(n)$ để chọn ô tiếp theo gần đích nhất. Thuật toán này có **thời gian thực thi nhanh nhất** nhưng đường đi tìm được không phải lúc nào cũng tối ưu (dễ bị đi chệch nếu gặp chướng ngại vật phức tạp).
* **A\* Search:** Kết hợp chi phí thực tế $g(n)$ và chi phí ước lượng $h(n)$. A* cho ra **đường đi ngắn nhất tối ưu** với **số lượng nút duyệt cực kỳ tối giản**, khắc phục hoàn toàn điểm yếu đi vòng của Greedy.
* **IDA\* (Iterative Deepening A\*):** Tìm kiếm sâu dần kết hợp A*. Thích hợp để tiết kiệm bộ nhớ trên bản đồ cực kỳ lớn, nhưng trên lưới 2D kích thước trung bình này, việc lặp đi lặp lại các ngưỡng độ sâu khiến thời gian xử lý của nó lâu nhất.

---

### 3. LEVEL 3: Local Search (Hill Climbing, Simulated Annealing, Local Beam)
Binh sĩ ở Màn 3 sử dụng thuật toán tìm kiếm cục bộ để định hướng di chuyển theo hàm mục tiêu tối thiểu hóa khoảng cách Manhattan đến người chơi.

#### Biểu đồ so sánh:
![So sánh Level 3](comparison_level3_local_search.png)

#### Phân tích kết quả:
* **Hill Climbing (Leo đồi có khởi động ngẫu nhiên):**
  * *Tỷ lệ thành công (Success Rate):* Thấp nhất do thuật toán chỉ đi lên theo hướng tốt hơn và rất dễ kẹt ở các vùng cực trị địa phương (ngõ cụt).
  * *Độ dài đường đi:* Rất ngắn nếu thuật toán may mắn tìm thấy đích.
* **Simulated Annealing (Mô phỏng luyện kim):**
  * *Tỷ lệ thành công:* Đạt tỷ lệ **rất cao (gần như 100%)** nhờ cơ chế chấp nhận các bước đi tệ hơn với xác suất dựa trên nhiệt độ $T$ giảm dần, giúp nó thoát khỏi các vùng kẹt một cách thông minh.
* **Local Beam Search (Tìm kiếm chùm tia k=3):**
  * Duy trì song song $k$ trạng thái tốt nhất. Thuật toán cho ra đường đi mượt mà, tối ưu nhất với tỷ lệ thành công cao.

---

### 4. LEVEL 4: Search Under Uncertainty (BFS, And-Or Search, Belief State A*)
Các Zombie ở Màn 4 tìm đường trong môi trường bất định, không chắc chắn về vị trí chính xác của người chơi hoặc các điều kiện ngoại cảnh.

#### Biểu đồ so sánh:
![So sánh Level 4](comparison_level4_uncertainty.png)

#### Phân tích kết quả:
* **BFS (Standard):** Tìm đường thẳng thông thường, không xử lý các yếu tố bất định hay không chắc chắn.
* **And-Or Graph Search:** Xây dựng một cây kế hoạch xử lý mọi khả năng xảy ra (kết quả hành động không chắc chắn). Thời gian tính toán lâu hơn do phải sinh các nút AND và OR để đảm bảo kế hoạch luôn thành công.
* **Belief State A\* (A\* trạng thái tin tưởng):** Biểu diễn sự không chắc chắn bằng tập hợp các trạng thái khả thi (Belief State) và tìm đường đi tối ưu đưa toàn bộ tập trạng thái này về đích. Giúp Zombie truy đuổi người chơi thông minh hơn ngay cả khi không biết chính xác vị trí.

---

### 5. LEVEL 5: Constraint Satisfaction Problem - CSP (Backtracking, AC-3, Min-Conflicts)
Ở Màn 5, các rồng (Dragon) cùng phối hợp để tìm các vị trí bao vây xung quanh người chơi sao cho không vị trí nào bị trùng lặp (thỏa mãn ràng buộc khoảng cách và vị trí).

#### Biểu đồ so sánh:
![So sánh Level 5](comparison_level5_csp.png)

#### Phân tích kết quả:
* **Backtracking CSP:** Thuật toán quay lui thuần túy. Gán giá trị thử và sai từng bước. Số vòng lặp (iterations) nhiều nhất do không có bộ lọc trước.
* **AC-3 + Backtracking CSP:** Sử dụng thuật toán lan truyền ràng buộc AC-3 để rút gọn không gian tìm kiếm (Domain) trước khi chạy Backtracking. **Số vòng lặp giảm đi đáng kể**, thời gian chạy nhanh và mượt mà hơn.
* **Min-Conflicts CSP:** Thuật toán tìm kiếm địa phương cho CSP. Bắt đầu bằng một gán nhãn hoàn chỉnh (có thể xung đột) và sửa đổi từng biến để giảm thiểu xung đột. Rất nhanh và hiệu quả trong việc tìm phương án bao vây nhanh chóng.

---

### 6. LEVEL 6: Adversarial Search (Minimax, Alpha-Beta, Expectimax)
Trong Màn 6, Boss ra quyết định đối kháng trực tiếp với người chơi bằng cách duyệt cây trò chơi ở các độ sâu khác nhau.

#### Biểu đồ so sánh:
![So sánh Level 6](comparison_level6_adversarial.png)

#### Phân tích kết quả:
* **Minimax (Độ sâu 3):** Duyệt qua toàn bộ 100% cây quyết định quyết định ở độ sâu 3. Thời gian chạy cao và số nút duyệt lớn (do không có cắt tỉa).
* **Alpha-Beta Pruning (Độ sâu 3):** Cho ra quyết định **tối ưu hoàn toàn giống Minimax** nhưng **cắt tỉa bỏ từ 50% đến 70% số lượng nút không cần thiết**. Thời gian phản xạ cực kỳ nhanh (dưới 1ms).
* **Expectimax (Độ sâu 3):** Tính toán giá trị trung bình có trọng số (kỳ vọng) tại các nút cơ hội để đối phó với lối đánh ngẫu nhiên của người chơi.
