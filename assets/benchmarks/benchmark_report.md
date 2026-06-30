# BÁO CÁO ĐÁNH GIÁ HIỆU SUẤT THUẬT TOÁN AI THEO TỪNG LEVEL
## Dự án: Knight's Odyssey

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

---

### 7. TỔNG QUAN: So sánh toàn diện hiệu suất của 6 nhóm thuật toán (Level 1 - 6)
Biểu đồ này so sánh trực tiếp thời gian thực thi trung bình (ms) của cả 6 nhóm thuật toán AI đại diện cho 6 Màn chơi trong game trên cùng một hệ quy chiếu. Do sự chênh lệch thời gian giữa nhóm tìm đường đơn giản (<0.5ms) và nhóm đối kháng nặng (hàng chục ms) là quá lớn, biểu đồ sử dụng **thang đo Logarit (Logarithmic scale)** cho trục Y để có thể biểu diễn trực quan tất cả các nhóm trên cùng một đồ thị.

#### Biểu đồ so sánh:
![So sánh tổng quan 6 nhóm thuật toán](comparison_groups_overall.png)

#### Phân tích kết quả tổng quan:
* **Nhóm 1 & 2 (Tìm đường Uninformed & Informed):** Có tốc độ xử lý nhanh nhất (thường dưới 0.5ms). Việc áp dụng Heuristic (như A* hay Greedy) giúp giảm số nút duyệt, nhưng nhìn chung cả hai nhóm này đều có độ phức tạp thấp vì chỉ tìm đường cho một tác nhân duy nhất trên bản đồ tĩnh.
* **Nhóm 3 (Tìm kiếm cục bộ - Local Search):** Thời gian chạy rất nhanh. Hill Climbing và Simulated Annealing đưa ra quyết định di chuyển dựa trên các trạng thái lân cận trực tiếp nên chi phí tính toán cực nhỏ.
* **Nhóm 4 (Môi trường bất định - Uncertainty):** Thời gian xử lý tăng lên rõ rệt (hàng mili-giây) do không gian trạng thái phình to thành "tập hợp các trạng thái khả thi" (Belief States) và phải tính toán cây And-Or phức tạp hơn.
* **Nhóm 5 (Thỏa mãn ràng buộc - CSP):** Xử lý bài toán gán mục tiêu không trùng lặp cho nhiều rồng cùng lúc. Thời gian chạy ở mức trung bình, trong đó AC-3 giúp lọc trước miền giá trị để giảm số lần quay lui hiệu quả.
* **Nhóm 6 (Tìm kiếm đối kháng - Adversarial):** **Nặng nhất và tốn thời gian nhất (vượt trội hơn hẳn các nhóm khác).** Minimax và Expectimax phải giả lập tất cả các nước đi tương lai của cả Boss lẫn người chơi theo cấu trúc cây trò chơi, dẫn đến số lượng nút duyệt khổng lồ. Việc áp dụng cắt tỉa Alpha-Beta là bắt buộc để giữ cho thời gian phản xạ của Boss nằm trong ngưỡng chấp nhận được của game thời gian thực.

---

### 8. Ý kiến và đánh giá của nhóm về việc áp dụng 6 nhóm thuật toán
Dựa trên yêu cầu thiết kế đồ án và kết quả thực nghiệm, nhóm tác giả đưa ra các đánh giá chuyên môn về tính hợp lý và hiệu quả của việc áp dụng 6 nhóm thuật toán AI để giải quyết các bài toán trong game như sau:

#### a) Về bài toán tìm đường đi (Pathfinding - Áp dụng Nhóm 1 & Nhóm 2)
* **Ý kiến đánh giá:** Việc lựa chọn thuật toán **A\*** (Nhóm 2) làm giải thuật di chuyển chủ đạo cho quái vật đuổi theo người chơi là hoàn toàn tối ưu và chuẩn xác. So với **BFS/DFS/UCS** (Nhóm 1), A* tiết kiệm tài nguyên CPU đáng kể cho game thời gian thực nhờ hàm heuristic định hướng (Manhattan), tránh hiện tượng giật lag khi có nhiều quái vật cùng di chuyển. **Greedy BFS** tuy nhanh nhưng dễ bị kẹt trước các tường chắn phức tạp của bản đồ TMX, vì vậy nhóm đánh giá A* là sự cân bằng hoàn hảo nhất giữa hiệu năng tính toán và tính tối ưu của đường đi.

#### b) Về bài toán di chuyển theo bản năng (Local Search - Áp dụng Nhóm 3)
* **Ý kiến đánh giá:** Phương án áp dụng **Local Search** (Hill Climbing, Simulated Annealing, Local Beam) cho binh sĩ ở Màn 3 là một hướng tiếp cận thông minh. Thay vì phải tính trước một đường đi dài và phức tạp (tốn CPU), quái vật chỉ cần đưa ra quyết định di chuyển từng bước dựa trên phân tích lân cận trực tiếp. 
* Đặc biệt, **Simulated Annealing** và **Local Beam Search** thể hiện tính ứng dụng thực tiễn rất cao vì chúng giúp quái vật vượt qua các chướng ngại vật dạng ngõ cụt (Local Optima) - điểm yếu chí mạng của thuật toán leo đồi truyền thống - mà vẫn duy trì tốc độ xử lý tức thì.

#### c) Về bài toán tìm kiếm trong sương mù (Search Under Uncertainty - Áp dụng Nhóm 4)
* **Ý kiến đánh giá:** Việc xây dựng trạng thái niềm tin (**Belief State**) và hướng đến **Belief Goal** giải quyết xuất sắc bài toán tìm kiếm thiếu thông tin khi Zombie mất dấu người chơi. Thay vì cho quái vật đi lang thang ngẫu nhiên một cách phi thực tế, việc cập nhật tập hợp các vị trí nghi ngờ giúp Zombie chủ động lục soát các khu vực có khả năng chứa người chơi cao nhất. Nhóm đánh giá đây là điểm sáng về mặt thiết kế gameplay, tạo ra cảm giác hồi hộp và tính chiến thuật cao cho người chơi.

#### d) Về bài toán thỏa mãn ràng buộc (Constraint Satisfaction - Áp dụng Nhóm 5)
* **Ý kiến đánh giá:** Mô hình hóa hành vi phối hợp bao vây người chơi của bầy rồng thành bài toán **CSP** là giải pháp cực kỳ khoa học và sáng tạo. Ràng buộc **AllDiff** giải quyết triệt để vấn đề "trùng lặp mục tiêu" (các quái vật không tranh giành hay dẫm chân lên cùng một vị trí). 
* Thực nghiệm cho thấy, việc tích hợp bộ lọc **AC-3** trước khi chạy Backtracking giúp giảm thiểu số vòng lặp thử-sai (iterations), từ đó giúp bầy rồng phân chia vị trí bao vây người chơi một cách trật tự, nhanh chóng và mượt mà trong thời gian thực.

#### e) Về bài toán ra quyết định đối kháng (Adversarial Decision Making - Áp dụng Nhóm 6)
* **Ý kiến đánh giá:** Áp dụng **Minimax, Alpha-Beta và Expectimax** cho Boss Robot ở màn chơi cuối là lựa chọn tối ưu nhất để xây dựng một AI thông minh và thử thách. Nhờ khả năng dự đoán nước đi của người chơi, Boss đưa ra các quyết định tấn công/phòng thủ rất hợp lý và nhạy bén.
* Tuy nhiên, do Minimax duyệt cây rất nặng, việc áp dụng **Cắt tỉa Alpha-Beta** là yếu tố sống còn để giảm số nút duyệt (tiết kiệm đến 70% thời gian xử lý), giữ cho khung hình của game ổn định ở mức 60 FPS. Expectimax giúp Boss thích ứng tốt khi người chơi thay đổi lối đánh ngẫu nhiên, hoàn thiện một AI Boss có độ khó cao và thực tế.
